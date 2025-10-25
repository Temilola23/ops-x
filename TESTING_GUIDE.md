# OPS-X TESTING & DATABASE ACCESS GUIDE

## STATUS: ✅ Setup Complete!

- PostgreSQL @15.14 installed & running
- Database `opsx_db` created
- Python dependencies installed (`psycopg2-binary`, `alembic`)
- Chroma client updated (deprecated API fixed)
- Environment configured

---

## HOW TO TEST

### 1. Start Backend Server

```bash
cd backend
source ../venv/bin/activate
python3 main.py
```

**Expected Output:**
```
Loaded environment from /Users/temilolaolowolayemo/Documents/GitHub/ops-x/scripts/.env
Initializing PostgreSQL database...
Creating database tables...
Database tables created successfully!
PostgreSQL connection successful!
Chroma initialized: {'total_embeddings': 0, 'collection_name': 'code_embeddings'}
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test API Health

**Terminal:**
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status": "healthy"}
```

### 3. Test Database: Create Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "prompt": "Build a todo app"
  }'
```

**Expected:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Test Project",
    "prompt": "Build a todo app",
    "status": "pending",
    "github_repo": null,
    "app_url": null,
    "owner_id": 1,
    "created_at": "2025-...",
    "updated_at": null
  },
  "error": null
}
```

### 4. Test Database: List Projects

```bash
curl http://localhost:8000/api/projects
```

### 5. Test Stakeholder Creation

```bash
curl -X POST http://localhost:8000/api/projects/1/stakeholders \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "Frontend"
  }'
```

### 6. Test AI Branch Suggestions

```bash
curl -X POST http://localhost:8000/api/projects/1/branches/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "stakeholder_name": "John Doe",
    "stakeholder_role": "Frontend",
    "project_name": "Test Project"
  }'
```

### 7. Test V0 Build (Full Integration)

```bash
curl -X POST http://localhost:8000/mcp/app/build/v0/stream \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "MyAwesomeApp",
    "requirements": "A simple calculator app with React",
    "deploy_vercel": false
  }'
```

This will:
- Generate code with V0
- Create GitHub repo
- Store embeddings in Chroma
- Store metadata in PostgreSQL

---

## HOW TO ACCESS DATABASE

### Option 1: psql Command Line

```bash
# Add PostgreSQL to PATH (for this session)
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# Connect to database
psql opsx_db
```

**Common Commands:**
```sql
-- List all tables
\dt

-- View projects
SELECT * FROM projects;

-- View stakeholders
SELECT * FROM stakeholders;

-- View branches
SELECT * FROM branches;

-- View users
SELECT * FROM users;

-- See table structure
\d projects

-- Count records
SELECT COUNT(*) FROM projects;

-- Exit
\q
```

### Option 2: TablePlus (GUI - Recommended)

1. Download [TablePlus](https://tableplus.com/)
2. Create new connection:
   - **Type:** PostgreSQL
   - **Host:** localhost
   - **Port:** 5432
   - **User:** your_mac_username
   - **Password:** (leave empty)
   - **Database:** opsx_db

3. Click "Connect"

### Option 3: pgAdmin (GUI)

1. Install: `brew install --cask pgadmin4`
2. Open pgAdmin
3. Add Server:
   - **Host:** localhost
   - **Port:** 5432
   - **Database:** opsx_db
   - **Username:** your_mac_username

### Option 4: DBeaver (Free GUI)

1. Install: `brew install --cask dbeaver-community`
2. New Connection → PostgreSQL
3. Configure as above

### Option 5: Python Script

```python
# test_db.py
import psycopg2

conn = psycopg2.connect("postgresql://localhost:5432/opsx_db")
cursor = conn.cursor()

# Query projects
cursor.execute("SELECT * FROM projects")
projects = cursor.fetchall()

for project in projects:
    print(project)

cursor.close()
conn.close()
```

Run: `python3 test_db.py`

---

## WHAT TO LOOK FOR WHEN TESTING

### ✅ Backend Startup

**Look for:**
- "PostgreSQL connection successful!" ✅
- "Chroma initialized: {...}" ✅
- "Uvicorn running on http://0.0.0.0:8000" ✅
- NO "ModuleNotFoundError" ✅
- NO "connection refused" ✅

**If you see warnings:**
- "WARNING: Chroma initialization failed" → Chroma optional, semantic search disabled
- "WARNING: Database initialization failed" → Check PostgreSQL is running

### ✅ Database Tables Created

**Connect to psql and check:**
```sql
\dt
```

**Expected tables:**
- `users`
- `projects`
- `stakeholders`
- `branches`
- `chat_messages`
- `code_embeddings`

### ✅ Data Persistence

**Test:**
1. Create a project via API
2. Restart server
3. List projects again → Should still see your project!

**This proves:**
- Data stored in PostgreSQL (not in-memory)
- Survives server restarts
- Production-ready

### ✅ Chroma Storage

**After V0 build:**
```bash
# Check Chroma data directory
ls -la /Users/temilolaolowolayemo/Documents/GitHub/ops-x/backend/chroma_data/

# Expected: SQLite DB files
```

**Check Chroma stats:**
```bash
cd backend
python3 -c "from integrations.chroma_client import chroma_search; print(chroma_search.get_stats())"
```

**Expected after a build:**
```
{'total_embeddings': 10, 'collection_name': 'code_embeddings'}
```

### ✅ Semantic Search

**After V0 build with project_id=1:**
```bash
curl -X POST http://localhost:8000/api/projects/1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "find the main component",
    "n_results": 3
  }'
```

**Expected:**
```json
{
  "success": true,
  "data": {
    "query": "find the main component",
    "results": [
      {
        "file_path": "app/page.tsx",
        "snippet": "export default function Home() { ... }",
        "language": "typescript",
        "relevance_score": 0.87
      }
    ],
    "powered_by": "Chroma DB"
  }
}
```

### ✅ API Documentation

**Open in browser:**
```
http://localhost:8000/docs
```

**Check for:**
- All endpoints visible
- "Projects API" section ✅
- "Stakeholders API" section ✅
- "Branches API" section ✅
- "MCP - PURE V0 BUILD" section ✅
- Can test endpoints directly in Swagger UI

---

## COMMON ISSUES & FIXES

### 1. "ModuleNotFoundError: No module named 'psycopg2'"

**Fix:**
```bash
cd backend
source ../venv/bin/activate
pip install psycopg2-binary
```

### 2. "connection refused" or "could not connect to server"

**Fix:**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# If not running:
brew services start postgresql@15
```

### 3. "FATAL: database 'opsx_db' does not exist"

**Fix:**
```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
createdb opsx_db
```

### 4. "Chroma initialization failed"

**Status:** Non-critical, semantic search will be disabled

**To fix (optional):**
```bash
cd backend
rm -rf chroma_data
python3 main.py  # Will recreate
```

### 5. "relation 'projects' does not exist"

**Fix:** Database tables not created

```bash
cd backend
python3 -c "from database import init_db; init_db()"
```

---

## MONITORING DATABASE

### Watch Database Activity (Real-time)

```bash
# Terminal 1: Start server
cd backend && python3 main.py

# Terminal 2: Watch database
watch -n 1 'psql opsx_db -c "SELECT id, name, status FROM projects"'
```

### Query Statistics

```sql
-- Connect to database
psql opsx_db

-- See table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- See row counts
SELECT 'projects' AS table, COUNT(*) FROM projects
UNION ALL
SELECT 'stakeholders', COUNT(*) FROM stakeholders
UNION ALL
SELECT 'branches', COUNT(*) FROM branches;
```

---

## RESET DATABASE (If Needed)

```bash
# Drop and recreate database
dropdb opsx_db
createdb opsx_db

# Restart server (auto-creates tables)
cd backend && python3 main.py
```

---

## NEXT STEPS FOR TESTING

### Basic Flow:
1. ✅ Start server → Check startup logs
2. ✅ Create project → Verify in database
3. ✅ Add stakeholders → Verify in database
4. ✅ Run V0 build → Check Chroma storage
5. ✅ Test semantic search → Verify results
6. ✅ Restart server → Verify data persists

### Advanced Flow:
1. Create project via API
2. Add 3 stakeholders (Frontend, Backend, Founder)
3. Get AI branch suggestions for each
4. Create branches for each stakeholder
5. Run V0 build with `project_id`
6. Query semantic search: "authentication logic"
7. Check PostgreSQL for metadata
8. Check Chroma for embeddings

---

## ACCESSING DATA PROGRAMMATICALLY

### Python:
```python
from database import get_db_context
from models import Project

with get_db_context() as db:
    projects = db.query(Project).all()
    for p in projects:
        print(f"{p.id}: {p.name} ({p.status})")
```

### SQL:
```sql
-- Join projects with stakeholders
SELECT 
  p.name AS project,
  s.name AS stakeholder,
  s.role,
  s.github_branch
FROM projects p
LEFT JOIN stakeholders s ON s.project_id = p.id;
```

---

## DEMO FOR JUDGES

**Show:**
1. Create project via Swagger UI at `/docs`
2. Open TablePlus → Show data in PostgreSQL
3. Run V0 build → Show streaming
4. Semantic search → "find React component"
5. Show Chroma stats → X embeddings stored

**Key Points:**
- Data persists (PostgreSQL)
- Semantic search works (Chroma)
- Real-time updates (SSE streaming)
- Production-ready (not in-memory)

---

## SUMMARY

**What's Working:**
✅ PostgreSQL storing relational data
✅ Chroma storing code embeddings
✅ All APIs migrated from in-memory
✅ Auto-initialization on startup
✅ Semantic code search
✅ Data persistence across restarts

**How to Verify:**
1. Start server → Check logs
2. Create data via API → Check database
3. Restart → Data still there
4. Query → PostgreSQL + Chroma working

**Database URLs:**
- PostgreSQL: `postgresql://localhost:5432/opsx_db`
- Chroma: `./chroma_data` (local files)
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

