#!/usr/bin/env python3
"""Development environment setup script."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.database import create_tables
from src.auth.service import AuthService
from src.auth.schemas import UserCreate
from src.core.database import get_db
from src.config import get_settings


async def setup_database():
    """Setup database tables."""
    print("Creating database tables...")
    await create_tables()
    print("✅ Database tables created")


async def create_default_user():
    """Create default user for development."""
    print("Creating default user...")
    
    async with get_db() as db:
        auth_service = AuthService(db)
        
        # Check if default user exists
        user = await auth_service.get_user_by_email("default@studhelper.local")
        if user:
            print("✅ Default user already exists")
            return
        
        # Create default user using UserCreate schema
        user_data = UserCreate(
            email="default@studhelper.com",
            username="default_user",
            password="default_password_change_me"
        )
        
        await auth_service.create_user(user_data)
        print("✅ Default user created")


async def setup_directories():
    """Create necessary directories."""
    settings = get_settings()
    
    directories = [
        settings.UPLOAD_DIR,
        settings.CHROMA_PERSIST_DIR,
        "logs",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


async def main():
    """Main setup function."""
    print("🚀 Setting up StudHelper development environment...")
    
    try:
        await setup_directories()
        await setup_database()
        await create_default_user()
        
        print("\n🎉 Development environment setup complete!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Start the development server: uvicorn src.main:app --reload")
        print("3. Visit http://localhost:8000/docs to see the API documentation")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())