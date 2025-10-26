"""
Fix refinements table by dropping and recreating it with correct schema
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', '.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

engine = create_engine(DATABASE_URL)

print("\n" + "="*70)
print("FIXING REFINEMENTS TABLE")
print("="*70)

with engine.connect() as conn:
    # Step 1: Drop the existing table
    print("\n1. Dropping existing refinements table...")
    try:
        conn.execute(text("DROP TABLE IF EXISTS refinements CASCADE"))
        conn.commit()
        print("   ✓ Table dropped")
    except Exception as e:
        print(f"   Error: {e}")
        exit(1)
    
    # Step 2: Create new table with correct schema
    print("\n2. Creating refinements table with correct schema...")
    create_table_sql = """
    CREATE TABLE refinements (
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
    """
    try:
        conn.execute(text(create_table_sql))
        conn.commit()
        print("   ✓ Table created with all columns")
    except Exception as e:
        print(f"   Error: {e}")
        exit(1)
    
    # Step 3: Create indexes
    print("\n3. Creating indexes...")
    indexes = [
        "CREATE INDEX idx_project_refinements ON refinements(project_id)",
        "CREATE INDEX idx_refinement_status ON refinements(status)",
        "CREATE INDEX idx_refinement_created ON refinements(created_at DESC)"
    ]
    for idx_sql in indexes:
        try:
            conn.execute(text(idx_sql))
            conn.commit()
            print(f"   ✓ Created index")
        except Exception as e:
            print(f"   Warning: {e}")

print("\n" + "="*70)
print("MIGRATION COMPLETE!")
print("="*70)
print("\nThe refinements table now has all required columns:")
print("  - id, project_id, stakeholder_id")
print("  - request_text (FIXED!)")
print("  - ai_model_preference, ai_model_used")
print("  - files_changed, pr_url, coderabbit_score")
print("  - status, error_message")
print("  - created_at, completed_at")
print("\nRestart the backend to pick up the changes.")
print("="*70 + "\n")

