#!/usr/bin/env python3
"""Test environment setup script."""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.database import create_tables, Base
from src.auth.service import AuthService
from src.core.database import get_db
from src.config import get_settings
from src.auth.schemas import UserCreate


async def setup_test_database():
    """Setup test database."""
    print("Setting up test database...")
    
    # Remove existing test db
    test_db_path = Path("./test.db")
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Create fresh tables
    await create_tables()
    print("✅ Test database created")


async def create_test_users():
    """Create test users."""
    print("Creating test users...")
    
    async with get_db() as db:
        auth_service = AuthService(db)
        
        # Test users data
        test_users = [
            {
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "full_name": "Test User"
            },
            {
                "email": "admin@example.com", 
                "username": "admin",
                "password": "adminpass123",
                "full_name": "Admin User"
            },
            {
                "email": "student@example.com",
                "username": "student", 
                "password": "studentpass123",
                "full_name": "Student User"
            }
        ]
        
        for user_data in test_users:
            try:
                user = await auth_service.create_user(UserCreate(
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                ))
                print(f"  ✅ Created user: {user.email}")
            except Exception as e:
                print(f"  ⚠️  User {user_data['email']} already exists or error: {e}")


def setup_test_directories():
    """Create test directories."""
    print("Setting up test directories...")
    
    test_dirs = [
        "./test_uploads",
        "./test_chroma_data", 
        "./test_logs",
        "./test_temp"
    ]
    
    for directory in test_dirs:
        path = Path(directory)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")


def create_test_fixtures():
    """Create test fixture files."""
    print("Creating test fixtures...")
    
    # Sample PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000189 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
285
%%EOF"""
    
    # Save test PDF
    fixtures_dir = Path("./tests/fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    (fixtures_dir / "sample.pdf").write_bytes(pdf_content)
    
    # Sample text content
    text_content = """
# Test Document

This is a test document for StudHelper.

## Introduction

StudHelper is an AI-powered study assistant that helps students learn more effectively.

## Features

- Document processing
- AI chat assistance  
- Vector search
- Usage tracking

## Conclusion

This document demonstrates the text processing capabilities.
"""
    
    (fixtures_dir / "sample.txt").write_text(text_content)
    print("  ✅ Created test fixture files")


async def cleanup_test_environment():
    """Clean up test environment."""
    print("Cleaning up test environment...")
    
    cleanup_paths = [
        "./test.db",
        "./test_uploads", 
        "./test_chroma_data",
        "./test_logs",
        "./test_temp"
    ]
    
    for path_str in cleanup_paths:
        path = Path(path_str)
        if path.exists():
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            print(f"  ✅ Cleaned: {path_str}")


async def main():
    """Main test setup function."""
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        await cleanup_test_environment()
        print("🧹 Test environment cleaned up!")
        return
    
    print("🧪 Setting up test environment...")
    
    try:
        # Set test environment
        os.environ["ENVIRONMENT"] = "test"
        
        setup_test_directories()
        await setup_test_database()
        await create_test_users()
        create_test_fixtures()
        
        print("\n🎉 Test environment setup complete!")
        print("\nNext steps:")
        print("1. Run tests: pytest")
        print("2. Run with coverage: pytest --cov=src")
        print("3. Clean up when done: python scripts/test_setup.py cleanup")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


