"""
Database migration script - Add new columns for team invites
"""

import os
from pathlib import Path
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / "scripts" / ".env"
if env_path.exists():
    load_dotenv(env_path)

from database import engine, Base
from models import User, Project, Stakeholder, Branch, ChatMessage, CodeEmbedding, Session

print("\n" + "="*70)
print("DATABASE MIGRATION - Adding Team Invite Columns")
print("="*70)

try:
    with engine.connect() as conn:
        # Add clerk_user_id to users table (if not exists)
        print("\n1. Adding clerk_user_id to users table...")
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS clerk_user_id VARCHAR(255) UNIQUE
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_clerk_user_id 
                ON users (clerk_user_id)
            """))
            conn.commit()
            print("   ✓ Added clerk_user_id column")
        except Exception as e:
            print(f"   Note: {e}")
        
        # Add user_id and status to stakeholders table
        print("\n2. Adding user_id and status to stakeholders table...")
        try:
            conn.execute(text("""
                ALTER TABLE stakeholders 
                ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)
            """))
            conn.execute(text("""
                ALTER TABLE stakeholders 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending'
            """))
            conn.commit()
            print("   ✓ Added user_id and status columns")
        except Exception as e:
            print(f"   Note: {e}")
        
        print("\n" + "="*70)
        print("MIGRATION COMPLETE!")
        print("="*70 + "\n")
        
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()

