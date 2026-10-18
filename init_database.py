"""Database initialization script for Image Drive"""

import os
import sys
from app import app, db, User

def init_database():
    """Initialize database and create tables"""
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        print("Database tables created successfully!")

        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        print("Directories created successfully!")

        # Create a default admin user
        print("\nCreating default admin user...")
        admin = User(username='admin', email='admin@imagedrive.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Please change this password after first login!")

        print("\n" + "="*50)
        print("Database initialization completed successfully!")
        print("="*50)
        print("\nYou can now run the application with:")
        print("  python app.py")
        print("\nThen visit: http://localhost:5000")
        print("="*50)

if __name__ == '__main__':
    print("="*50)
    print("Image Drive - Database Initialization")
    print("="*50)
    print("\nThis will reset the database and create new tables.")

    confirm = input("\nDo you want to continue? (yes/no): ")

    if confirm.lower() in ['yes', 'y']:
        init_database()
    else:
        print("Initialization cancelled.")
        sys.exit(0)
