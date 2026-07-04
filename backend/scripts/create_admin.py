#!/usr/bin/env python3
"""Create a test admin user"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.user import User

def create_admin_user():
    db: Session = SessionLocal()
    try:
        # Check if admin exists
        existing = db.query(User).filter(User.username == 'admin').first()
        
        # Hash password
        pwd = 'Admin@123'
        salt = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')
        
        if existing:
            # Update password
            existing.password = hashed_pwd
            db.commit()
            print(f"[UPDATED] User 'admin' password updated!")
        else:
            # Create new admin
            admin = User(
                username='admin',
                password=hashed_pwd,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"[CREATED] Admin user 'admin' created!")
        
        print("-" * 50)
        print("Login Credentials:")
        print(f"  Username: admin")
        print(f"  Password: Admin@123")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
