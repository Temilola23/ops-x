"""
Database migration - Add refinements table
"""

import os
from pathlib import Path
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / "scripts" / ".env"
if env_path.exists():
    load_dotenv(env_path)

from database import engine

print("\n" + "="*70)
print("DATABASE MIGRATION - Adding Refinements Table")
print("="*70)

try:
    with engine.connect() as conn:
        # Add refinements table
        print("\n1. Creating refinements table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS refinements (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                stakeholder_id INTEGER NOT NULL REFERENCES stakeholders(id) ON DELETE CASCADE,
                request_text TEXT NOT NULL,
                ai_model_preference VARCHAR(50),
                ai_model_used VARCHAR(50),
                files_changed JSON,
                pr_url VARCHAR(500),
                coderabbit_score INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.commit()
        print("   ✓ Created refinements table")
        
        # Add indexes for performance
        print("\n2. Creating indexes...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_refinements_project 
            ON refinements (project_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_refinements_stakeholder 
            ON refinements (stakeholder_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_refinements_status 
            ON refinements (status)
        """))
        conn.commit()
        print("   ✓ Created indexes")
        
        print("\n" + "="*70)
        print("MIGRATION COMPLETE!")
        print("="*70 + "\n")
        
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()

