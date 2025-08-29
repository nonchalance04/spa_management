"""
Database migration script to add auth_token and token_expires_at fields
to Therapist and Cashier tables.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def add_token_fields():
    """Add auth_token and token_expires_at fields to Therapist and Cashier tables."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Add fields to Therapist table
            print("Adding token fields to Therapist table...")
            
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='therapists' 
                AND column_name IN ('auth_token', 'token_expires_at')
            """))
            existing_columns = [row[0] for row in result]
            
            if 'auth_token' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE therapists 
                    ADD COLUMN auth_token VARCHAR(255) UNIQUE
                """))
                print("  - Added auth_token column to therapist table")
            else:
                print("  - auth_token column already exists in therapist table")
            
            if 'token_expires_at' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE therapists 
                    ADD COLUMN token_expires_at TIMESTAMP
                """))
                print("  - Added token_expires_at column to therapist table")
            else:
                print("  - token_expires_at column already exists in therapist table")
            
            # Add fields to Cashier table
            print("\nAdding token fields to Cashier table...")
            
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='cashiers' 
                AND column_name IN ('auth_token', 'token_expires_at')
            """))
            existing_columns = [row[0] for row in result]
            
            if 'auth_token' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE cashiers
                    ADD COLUMN auth_token VARCHAR(255) UNIQUE
                """))
                print("  - Added auth_token column to cashier table")
            else:
                print("  - auth_token column already exists in cashier table")
            
            if 'token_expires_at' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE cashiers 
                    ADD COLUMN token_expires_at TIMESTAMP
                """))
                print("  - Added token_expires_at column to cashier table")
            else:
                print("  - token_expires_at column already exists in cashier table")
            
            # Commit the changes
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    success = add_token_fields()
    sys.exit(0 if success else 1)
