#!/usr/bin/env python3
"""Production deployment script for StudHelper backend."""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command: str, check: bool = True) -> bool:
    """Run a shell command and return success status."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=False)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {command}")
        return False
    return result.returncode == 0


def check_requirements():
    """Check deployment requirements."""
    print("🔍 Checking deployment requirements...")
    
    requirements = ["docker", "docker-compose"]
    missing = []
    
    for req in requirements:
        if not run_command(f"which {req}", check=False):
            missing.append(req)
    
    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        return False
    
    print("✅ All requirements satisfied")
    return True


def setup_environment(env: str):
    """Setup environment files."""
    print(f"🔧 Setting up {env} environment...")
    
    env_file = f".env.{env}"
    if not Path(env_file).exists():
        print(f"❌ Environment file {env_file} not found")
        return False
    
    # Copy to .env for Docker
    run_command(f"cp {env_file} .env")
    print(f"✅ Environment configured for {env}")
    return True


def build_images(env: str):
    """Build Docker images."""
    print("🏗️  Building Docker images...")
    
    compose_file = f"docker/docker-compose.{env}.yml"
    if not Path(compose_file).exists():
        compose_file = "docker/docker-compose.yml"
    
    success = run_command(f"docker-compose -f {compose_file} build")
    if success:
        print("✅ Docker images built successfully")
    return success


def run_migrations():
    """Run database migrations."""
    print("🗄️  Running database migrations...")
    
    # Start database first
    run_command("docker-compose -f docker/docker-compose.prod.yml up -d db")
    
    # Wait a bit for database to start
    import time
    time.sleep(10)
    
    # Run migrations
    success = run_command(
        "docker-compose -f docker/docker-compose.prod.yml run --rm api "
        "python scripts/migrate_db.py upgrade"
    )
    
    if success:
        print("✅ Database migrations completed")
    return success


def deploy_application(env: str):
    """Deploy the application."""
    print(f"🚀 Deploying {env} application...")
    
    compose_file = f"docker/docker-compose.{env}.yml"
    if not Path(compose_file).exists():
        compose_file = "docker/docker-compose.yml"
    
    # Stop existing services
    run_command(f"docker-compose -f {compose_file} down", check=False)
    
    # Start services
    success = run_command(f"docker-compose -f {compose_file} up -d")
    
    if success:
        print("✅ Application deployed successfully")
        
        # Show status
        run_command(f"docker-compose -f {compose_file} ps")
        
        print("\n🎉 Deployment complete!")
        print(f"Application should be available at: http://localhost:8000")
        if env == "prod":
            print("Check logs with: docker-compose -f docker/docker-compose.prod.yml logs -f")
    
    return success


def health_check():
    """Perform health check."""
    print("🏥 Performing health check...")
    
    import time
    import requests
    
    # Wait for services to start
    time.sleep(30)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def rollback():
    """Rollback deployment."""
    print("🔄 Rolling back deployment...")
    
    # Stop current services
    run_command("docker-compose -f docker/docker-compose.prod.yml down")
    
    # Could implement more sophisticated rollback logic here
    # such as reverting to previous Docker images
    
    print("✅ Rollback completed")


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy StudHelper backend")
    parser.add_argument(
        "action",
        choices=["deploy", "rollback", "health-check"],
        help="Deployment action"
    )
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="prod", 
        help="Environment to deploy"
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip database migrations"
    )
    
    args = parser.parse_args()
    
    if args.action == "rollback":
        rollback()
        return
    
    if args.action == "health-check":
        success = health_check()
        sys.exit(0 if success else 1)
    
    print(f"🚀 Starting {args.env} deployment...")
    
    try:
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Setup environment
        if not setup_environment(args.env):
            sys.exit(1)
        
        # Build images
        if not build_images(args.env):
            sys.exit(1)
        
        # Run migrations
        if not args.skip_migrations and not run_migrations():
            print("❌ Migration failed, stopping deployment")
            sys.exit(1)
        
        # Deploy application
        if not deploy_application(args.env):
            sys.exit(1)
        
        # Health check
        if not health_check():
            print("⚠️  Deployment completed but health check failed")
            sys.exit(1)
        
        print("🎉 Deployment successful!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Deployment interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


