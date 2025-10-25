# DATABASE SETUP GUIDE

## OPS-X Database Architecture

**PostgreSQL** (relational data) + **Chroma** (vector embeddings)

---

## QUICK START (Local Development)

### 1. Install PostgreSQL

#### macOS:
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Windows:
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Create database
createdb opsx_db

# OR using psql:
psql postgres
CREATE DATABASE opsx_db;
\q
```

### 3. Set Environment Variable

Add to `scripts/.env`:
```bash
DATABASE_URL=postgresql://localhost:5432/opsx_db
CHROMA_PERSIST_DIR=./chroma_data
```

### 4. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
cd backend
python3 -c "from database import init_db; init_db()"
```

Or just start the server (auto-initializes):
```bash
python3 main.py
```

---

## DATABASE SCHEMA

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    session_id VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Projects Table
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    prompt TEXT,
    github_repo VARCHAR(255),
    app_url VARCHAR(512),
    status VARCHAR(50) DEFAULT 'pending',
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Stakeholders Table
```sql
CREATE TABLE stakeholders (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    github_branch VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Branches Table
```sql
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    stakeholder_id INTEGER REFERENCES stakeholders(id),
    branch_name VARCHAR(255) NOT NULL,
    github_url VARCHAR(512),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    user_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    role VARCHAR(50),
    is_ai BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Code Embeddings Table (metadata only)
```sql
CREATE TABLE code_embeddings (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    file_path VARCHAR(512) NOT NULL,
    chroma_id VARCHAR(255) UNIQUE,
    language VARCHAR(50),
    chunk_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## CHROMA DB

Chroma stores actual vector embeddings for semantic code search.

**Location:** `./chroma_data` (configurable via `CHROMA_PERSIST_DIR`)

**What's stored:**
- Code file embeddings (vectors)
- File metadata (project_id, file_path, language)
- Code snippets for context

**Usage:**
```python
from integrations.chroma_client import chroma_search, generate_embedding

# Search code
query_embedding = generate_embedding("authentication logic")
results = chroma_search.search_code(
    query_embedding=query_embedding,
    project_id="123",
    n_results=5
)
```

---

## PRODUCTION SETUP

### Option 1: Supabase (Recommended)

1. Go to [supabase.com](https://supabase.com)
2. Create project (free tier)
3. Get connection string from Settings → Database
4. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
   ```

### Option 2: Render/Railway/Heroku

1. Create PostgreSQL database
2. Get connection string
3. Update `.env` with provided URL

### Option 3: Self-hosted PostgreSQL

```bash
# Update postgresql.conf for remote access
sudo vim /etc/postgresql/15/main/postgresql.conf
# Change: listen_addresses = '*'

# Update pg_hba.conf
sudo vim /etc/postgresql/15/main/pg_hba.conf
# Add: host all all 0.0.0.0/0 md5

# Restart
sudo systemctl restart postgresql
```

---

## DATABASE MIGRATIONS

Using Alembic for schema changes:

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## TESTING DATABASE

```bash
cd backend

# Test connection
python3 -c "from database import engine; engine.connect(); print('Connected!')"

# Test Chroma
python3 -c "from integrations.chroma_client import chroma_search; print(chroma_search.get_stats())"

# Create test data
python3 << EOF
from database import get_db_context
from models import User, Project

with get_db_context() as db:
    user = User(email="test@example.com", name="Test User")
    db.add(user)
    db.flush()
    
    project = Project(name="Test Project", prompt="Test prompt", owner_id=user.id)
    db.add(project)
    db.commit()
    
    print(f"Created project: {project.id}")
EOF
```

---

## TROUBLESHOOTING

### "FATAL: database 'opsx_db' does not exist"
```bash
createdb opsx_db
```

### "FATAL: role 'username' does not exist"
```bash
createuser username
# OR use postgres user:
DATABASE_URL=postgresql://postgres@localhost:5432/opsx_db
```

### "connection refused"
```bash
# Check if PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Start if not running
brew services start postgresql@15  # macOS
sudo systemctl start postgresql  # Linux
```

### Chroma errors
```bash
# Delete and recreate
rm -rf chroma_data
python3 main.py  # Will recreate
```

---

## API CHANGES

### Before (in-memory):
```python
projects_db: Dict[str, dict] = {}
```

### After (PostgreSQL):
```python
from database import get_db
from models import Project

@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects
```

### Semantic Search (NEW):
```bash
POST /api/projects/{id}/search/semantic
{
  "query": "find authentication logic",
  "n_results": 5
}
```

---

## WHAT YOU NEED FROM USER

User needs to:

1. **Install PostgreSQL** (if not already installed)
   ```bash
   brew install postgresql@15  # macOS
   ```

2. **Create database**
   ```bash
   createdb opsx_db
   ```

3. **Update `.env`**
   ```bash
   DATABASE_URL=postgresql://localhost:5432/opsx_db
   ```

4. **Start server** (auto-initializes database)
   ```bash
   cd backend
   python3 main.py
   ```

That's it! Database will be created automatically on first run.

