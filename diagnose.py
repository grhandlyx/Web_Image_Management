#!/usr/bin/env python3
"""Diagnostic script for Image Drive system"""

import os
import sys
from app import app, db, User, Session, Image

def check_database():
    """Check database status"""
    print("=" * 50)
    print("DATABASE CHECK")
    print("=" * 50)

    with app.app_context():
        try:
            # Check tables
            print(f"✓ Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Count users
            user_count = User.query.count()
            print(f"✓ Total users: {user_count}")

            if user_count > 0:
                print("\nExisting users:")
                for user in User.query.all():
                    print(f"  - {user.username} ({user.email})")
            else:
                print("⚠ No users found. You need to register first!")

            # Count sessions
            session_count = Session.query.count()
            print(f"✓ Active sessions: {session_count}")

            # Count images
            image_count = Image.query.count()
            print(f"✓ Total images: {image_count}")

            return True
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False

def check_directories():
    """Check required directories"""
    print("\n" + "=" * 50)
    print("DIRECTORY CHECK")
    print("=" * 50)

    dirs = [
        ('Upload folder', app.config['UPLOAD_FOLDER']),
        ('Temp folder', app.config['TEMP_FOLDER']),
        ('Logs folder', 'logs'),
        ('Static CSS', 'static/css'),
        ('Static JS', 'static/js'),
        ('Templates', 'templates'),
    ]

    all_ok = True
    for name, path in dirs:
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"{status} {name}: {path}")
        if not exists:
            all_ok = False

    return all_ok

def check_dependencies():
    """Check Python dependencies"""
    print("\n" + "=" * 50)
    print("DEPENDENCIES CHECK")
    print("=" * 50)

    required = [
        'flask',
        'flask_sqlalchemy',
        'werkzeug',
        'PIL',
        'torch',
        'transformers',
        'pytesseract',
        'numpy',
        'scikit-learn'
    ]

    all_ok = True
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_ok = False

    return all_ok

def create_test_user():
    """Create a test user"""
    print("\n" + "=" * 50)
    print("CREATE TEST USER")
    print("=" * 50)

    with app.app_context():
        # Check if test user exists
        existing = User.query.filter_by(username='test').first()
        if existing:
            print("⚠ Test user already exists")
            print(f"  Username: test")
            print(f"  Password: test123")
            return

        # Create test user
        try:
            user = User(username='test', email='test@example.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            print("✓ Test user created successfully!")
            print(f"  Username: test")
            print(f"  Password: test123")
            print(f"  Email: test@example.com")
        except Exception as e:
            print(f"✗ Failed to create test user: {e}")

def main():
    """Run all diagnostics"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " IMAGE DRIVE - SYSTEM DIAGNOSTICS ".center(48) + "║")
    print("╚" + "=" * 48 + "╝")
    print()

    # Run checks
    db_ok = check_database()
    dir_ok = check_directories()
    dep_ok = check_dependencies()

    # Create test user if needed
    if db_ok:
        create_test_user()

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    if db_ok and dir_ok and dep_ok:
        print("✓ All checks passed!")
        print("\nYou can now:")
        print("1. Start the server: ./run.sh")
        print("2. Open browser: http://localhost:5000")
        print("3. Login with: test / test123")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        if not dep_ok:
            print("\nTo install dependencies: pip install -r requirements.txt")

    print()

if __name__ == '__main__':
    main()
