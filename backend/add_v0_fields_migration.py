"""
Database migration script to add v0 fields to projects table
Run this to update your existing database schema
"""

from sqlalchemy import text
from database import engine

def migrate_add_v0_fields():
    """Add v0_chat_id and v0_preview_url columns to projects table"""
    
    with engine.connect() as conn:
        try:
            # Add v0_chat_id column
            print("Adding v0_chat_id column...")
            conn.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS v0_chat_id VARCHAR(255)
            """))
            
            # Add index for v0_chat_id
            print("Creating index on v0_chat_id...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_v0_chat_id 
                ON projects(v0_chat_id)
            """))
            
            # Add v0_preview_url column
            print("Adding v0_preview_url column...")
            conn.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS v0_preview_url VARCHAR(512)
            """))
            
            conn.commit()
            print("✅ Migration completed successfully!")
            print("   - Added v0_chat_id column with index")
            print("   - Added v0_preview_url column")
            print()
            print("Now the refine page will show the v0 preview! 🎉")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("   Adding v0 integration fields to projects table")
    print()
    migrate_add_v0_fields()

