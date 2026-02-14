# Development Environment Setup Guide

**Document Version:** 1.0
**Created:** February 1, 2026
**Author:** Nike (AI Companion)
**Audience:** Arvind Sarin, Future Developers

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Mac Setup](#mac-setup)
3. [VPS Setup](#vps-setup)
4. [Python Environment](#python-environment)
5. [Database Setup](#database-setup)
6. [API Keys & Secrets](#api-keys--secrets)
7. [Services Configuration](#services-configuration)
8. [IDE Setup](#ide-setup)
9. [Testing Environment](#testing-environment)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Minimum System Requirements

#### Mac (Development Machine)

| Resource | Minimum             | Recommended          |
| -------- | ------------------- | -------------------- |
| macOS    | 13.0 (Ventura)      | 14.0+ (Sonoma)       |
| RAM      | 8 GB                | 16 GB                |
| Storage  | 20 GB free          | 50 GB free           |
| CPU      | Apple M1 / Intel i5 | Apple M2+ / Intel i7 |

#### VPS (Production Server)

| Resource | Minimum          | Recommended      |
| -------- | ---------------- | ---------------- |
| OS       | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |
| RAM      | 2 GB             | 4 GB             |
| Storage  | 40 GB SSD        | 80 GB SSD        |
| CPU      | 2 vCPU           | 4 vCPU           |

---

## Mac Setup

### Step 1: Install Homebrew

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify installation
brew --version
```

### Step 2: Install System Dependencies

```bash
# Update Homebrew
brew update

# Install core tools
brew install git
brew install python@3.11
brew install node@20
brew install postgresql@15
brew install redis
brew install fswatch

# Install development tools
brew install jq
brew install httpie
brew install gh  # GitHub CLI

# Verify installations
git --version
python3 --version
node --version
psql --version
```

### Step 3: Install PostgreSQL Extensions

```bash
# Install pgvector for vector similarity search
brew install pgvector

# Start PostgreSQL service
brew services start postgresql@15

# Enable pgvector extension
psql postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Step 4: Configure Git

```bash
# Set global git config
git config --global user.name "Arvind Sarin"
git config --global user.email "arvind@example.com"

# Configure SSH for GitHub
ssh-keygen -t ed25519 -C "arvind@example.com"
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub: https://github.com/settings/keys
```

### Step 5: Clone Repository

```bash
# Clone openclaw workspace
cd ~
git clone git@github.com:openclaw/openclaw.git
cd openclaw

# Verify structure
ls -la
```

---

## VPS Setup

### Step 1: Initial Server Setup

```bash
# SSH into VPS
ssh clawdbot

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates
```

### Step 2: Install Python 3.11

```bash
# Add deadsnakes PPA for Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify
python3 --version
```

### Step 3: Install Node.js 20

```bash
# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version
npm --version
```

### Step 4: Install PostgreSQL 15

```bash
# Add PostgreSQL APT repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update

# Install PostgreSQL 15
sudo apt install -y postgresql-15 postgresql-contrib-15

# Install pgvector
sudo apt install -y postgresql-15-pgvector

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 5: Install inotify-tools (for file watching)

```bash
sudo apt install -y inotify-tools
```

### Step 6: Clone Repository

```bash
# Clone openclaw workspace
cd /home/ubuntu
git clone git@github.com:openclaw/openclaw.git
cd openclaw
```

---

## Python Environment

### Step 1: Create Virtual Environment

```bash
# Navigate to openclaw directory
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Core Dependencies

```bash
# Install from requirements.txt (if exists)
pip install -r requirements.txt

# Or install manually
pip install \
    playwright \
    chromadb \
    openai \
    anthropic \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    alembic \
    pgvector \
    pydantic \
    python-dateutil \
    pyyaml \
    aiohttp \
    httpx \
    numpy \
    pandas
```

### Step 3: Install Development Dependencies

```bash
pip install \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy \
    pre-commit
```

### Step 4: Install Playwright Browsers

```bash
# Install Chromium for web scraping
playwright install chromium

# Install all browsers (optional)
playwright install
```

### Step 5: Create requirements.txt

```bash
# Generate requirements.txt
pip freeze > requirements.txt
```

**Standard requirements.txt:**

```txt
# Core
playwright>=1.40.0
chromadb>=0.4.22
openai>=1.10.0
anthropic>=0.18.0

# Web Framework
fastapi>=0.109.0
uvicorn>=0.27.0
httpx>=0.26.0

# Database
sqlalchemy>=2.0.25
psycopg2-binary>=2.9.9
alembic>=1.13.1
pgvector>=0.2.4

# Utilities
pydantic>=2.6.0
python-dateutil>=2.8.2
pyyaml>=6.0.1
aiohttp>=3.9.3
numpy>=1.26.3
pandas>=2.2.0

# Development
pytest>=8.0.0
pytest-asyncio>=0.23.4
pytest-cov>=4.1.0
black>=24.1.1
isort>=5.13.2
flake8>=7.0.0
mypy>=1.8.0
pre-commit>=3.6.0
```

---

## Database Setup

### Step 1: Create Database (Mac)

```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb openclaw

# Create user
psql openclaw <<EOF
CREATE USER nike WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE openclaw TO nike;
\c openclaw
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
GRANT ALL ON SCHEMA public TO nike;
EOF

# Verify
psql openclaw -c "\dx"  # List extensions
psql openclaw -c "\du"  # List users
```

### Step 2: Create Database (VPS)

```bash
# Switch to postgres user
sudo -u postgres psql <<EOF
CREATE DATABASE openclaw;
CREATE USER nike WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE openclaw TO nike;
\c openclaw
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
GRANT ALL ON SCHEMA public TO nike;
EOF

# Configure remote access (if needed)
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: host openclaw nike 0.0.0.0/0 md5

sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = '*'

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Step 3: Apply Schema

```bash
# Navigate to memex directory
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw/memex

# Apply initial schema
psql "postgresql://nike:password@localhost:5432/openclaw" -f schema/001_initial_schema.sql

# Verify tables
psql "postgresql://nike:password@localhost:5432/openclaw" -c "\dt"
```

### Step 4: Initialize Alembic Migrations

```bash
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw/memex

# Initialize Alembic
alembic init migrations

# Update alembic.ini
sed -i '' 's|sqlalchemy.url = .*|sqlalchemy.url = postgresql://nike:password@localhost:5432/openclaw|' alembic.ini

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## API Keys & Secrets

### Step 1: Create Environment File

```bash
# Create .env file
cat > /Users/arvindsarin/Cursor/Claude-2026/openclaw/.env <<EOF
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://nike:your_password@localhost:5432/openclaw

# Plaud.AI (for scraper)
PLAUD_EMAIL=arvind@example.com
PLAUD_PASSWORD=your_plaud_password

# Memex Configuration
MEMEX_API_PORT=8891
CHROMADB_PATH=./data/chromadb

# xAI (Grok)
XAI_API_KEY=xai-...

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
EOF

# Secure the file
chmod 600 /Users/arvindsarin/Cursor/Claude-2026/openclaw/.env
```

### Step 2: Load Environment Variables

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# OpenClaw environment
export $(grep -v '^#' /Users/arvindsarin/Cursor/Claude-2026/openclaw/.env | xargs)
```

### Step 3: Verify API Keys

```bash
# Test OpenAI
python3 -c "
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Say hello'}],
    max_tokens=10
)
print('OpenAI OK:', response.choices[0].message.content)
"

# Test Anthropic
python3 -c "
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model='claude-3-haiku-20240307',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Say hello'}]
)
print('Anthropic OK:', response.content[0].text)
"
```

---

## Services Configuration

### Step 1: Configure Kanban Server (VPS)

```bash
# Create systemd service
sudo cat > /etc/systemd/system/kanban-server.service <<EOF
[Unit]
Description=Kanban Dashboard Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/openclaw/kanban/server
ExecStart=/usr/bin/node kanban-server.js
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable kanban-server
sudo systemctl start kanban-server

# Check status
sudo systemctl status kanban-server
```

### Step 2: Configure Auto-Sync (Mac)

```bash
# Create launchd plist
cat > ~/Library/LaunchAgents/com.openclaw.autosync.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.autosync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/arvindsarin/Cursor/Claude-2026/openclaw/scripts/auto-sync.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/arvindsarin/Cursor/Claude-2026/openclaw/logs/auto-sync.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/arvindsarin/Cursor/Claude-2026/openclaw/logs/auto-sync-error.log</string>
</dict>
</plist>
EOF

# Load the service
launchctl load ~/Library/LaunchAgents/com.openclaw.autosync.plist

# Check status
launchctl list | grep openclaw
```

### Step 3: Configure Auto-Sync (VPS)

```bash
# Create systemd service
sudo cat > /etc/systemd/system/openclaw-sync.service <<EOF
[Unit]
Description=OpenClaw Auto-Sync Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/openclaw
ExecStart=/home/ubuntu/openclaw/scripts/auto-sync-vps.sh
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable openclaw-sync
sudo systemctl start openclaw-sync
```

### Step 4: Configure Memex API (Optional)

```bash
# Create systemd service for Memex API
sudo cat > /etc/systemd/system/memex-api.service <<EOF
[Unit]
Description=Memex API Server
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/openclaw/memex
ExecStart=/home/ubuntu/openclaw/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8891
Restart=on-failure
RestartSec=10
Environment="DATABASE_URL=postgresql://nike:password@localhost:5432/openclaw"
Environment="OPENAI_API_KEY=sk-..."

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable memex-api
sudo systemctl start memex-api
```

---

## IDE Setup

### VS Code Configuration

**Extensions to Install:**

```bash
# Install via command line
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension GitHub.copilot
code --install-extension anthropics.claude-code
```

**settings.json:**

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [88, 120],
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".git": true,
    "venv": true,
    "*.egg-info": true
  },
  "python.analysis.typeCheckingMode": "basic"
}
```

**launch.json (Debug Configurations):**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["api.main:app", "--reload", "--port", "8891"],
      "cwd": "${workspaceFolder}/memex",
      "env": {
        "DATABASE_URL": "postgresql://nike:password@localhost:5432/openclaw"
      }
    },
    {
      "name": "Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "cwd": "${workspaceFolder}/memex"
    }
  ]
}
```

### Cursor IDE Configuration

Cursor uses similar settings to VS Code. Additional configuration:

**CLAUDE.md for Cursor:**

```markdown
# Clawd Workspace Instructions

## Project Context

This is Nike's (AI companion) operational workspace. Nike assists Arvind Sarin with:

- Personal knowledge management
- Business automation
- Marketing/sales content generation

## Key Directories

- `/kanban` - Task management system
- `/memex` - AI second brain (in development)
- `/scripts` - Automation scripts
- `/skills` - AI skill integrations

## Code Style

- Python: Black formatter, 88 char line length
- JavaScript: Prettier, 2 space indent
- Always include type hints in Python
- Write docstrings for all public functions

## Testing

- Run `pytest tests/ -v` before committing
- Minimum 80% coverage for new code
```

---

## Testing Environment

### Step 1: Configure pytest

**pytest.ini:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --cov=. --cov-report=html --cov-report=term-missing
filterwarnings =
    ignore::DeprecationWarning
```

### Step 2: Create Test Fixtures

**tests/conftest.py:**

```python
import pytest
import asyncio
from pathlib import Path
import tempfile

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_openai_key(monkeypatch):
    """Mock OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

@pytest.fixture
def mock_database_url(monkeypatch):
    """Mock database URL."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
```

### Step 3: Run Tests

```bash
# Run all tests
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw
pytest

# Run with coverage
pytest --cov=memex --cov-report=html

# Run specific test file
pytest tests/test_scraper.py -v

# Run specific test
pytest tests/test_scraper.py::test_login -v

# Run marked tests
pytest -m "not slow"
```

### Step 4: Pre-commit Hooks

**.pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

**Install pre-commit:**

```bash
pip install pre-commit
pre-commit install
```

---

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Failed

**Error:** `connection refused`

**Solution:**

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql  # Mac
sudo systemctl status postgresql      # Linux

# Start if not running
brew services start postgresql@15     # Mac
sudo systemctl start postgresql       # Linux

# Check connection
psql -h localhost -U nike -d openclaw
```

#### 2. Playwright Browser Not Found

**Error:** `Browser was not found`

**Solution:**

```bash
# Install browsers
playwright install

# Or just Chromium
playwright install chromium

# With dependencies (Linux)
playwright install-deps chromium
```

#### 3. OpenAI API Error

**Error:** `Invalid API key`

**Solution:**

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test the key
python3 -c "
from openai import OpenAI
client = OpenAI()
print(client.models.list().data[0].id)
"
```

#### 4. ChromaDB Persistence Error

**Error:** `Cannot write to directory`

**Solution:**

```bash
# Check permissions
ls -la data/chromadb

# Fix permissions
chmod 755 data/chromadb

# Or create with correct permissions
mkdir -p data/chromadb && chmod 755 data/chromadb
```

#### 5. Virtual Environment Issues

**Error:** `ModuleNotFoundError`

**Solution:**

```bash
# Ensure venv is activated
source venv/bin/activate

# Verify correct Python
which python
which pip

# Reinstall packages
pip install -r requirements.txt
```

### Useful Debug Commands

```bash
# Check all running services
systemctl list-units --type=service --state=running  # Linux
launchctl list | grep openclaw                           # Mac

# Check port usage
lsof -i :8888  # Kanban server
lsof -i :8891  # Memex API
lsof -i :5432  # PostgreSQL

# Check logs
tail -f logs/auto-sync.log
journalctl -u kanban-server -f  # Linux

# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Test API endpoints
curl http://localhost:8888/health
curl http://localhost:8891/docs
```

---

## Quick Reference

### Start All Services (Mac)

```bash
#!/bin/bash
# start-all.sh

# Start PostgreSQL
brew services start postgresql@15

# Activate venv
source /Users/arvindsarin/Cursor/Claude-2026/openclaw/venv/bin/activate

# Start Memex API (in background)
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw/memex
uvicorn api.main:app --port 8891 &

echo "All services started!"
echo "Memex API: http://localhost:8891/docs"
```

### Stop All Services (Mac)

```bash
#!/bin/bash
# stop-all.sh

# Stop Memex API
pkill -f "uvicorn api.main:app"

# Stop PostgreSQL (optional)
# brew services stop postgresql@15

echo "Services stopped!"
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

echo "=== Clawd Health Check ==="

# PostgreSQL
echo -n "PostgreSQL: "
psql $DATABASE_URL -c "SELECT 1;" > /dev/null 2>&1 && echo "OK" || echo "FAILED"

# Kanban Server
echo -n "Kanban Server (8888): "
curl -s http://localhost:8888/kanban.json > /dev/null && echo "OK" || echo "NOT RUNNING"

# Memex API
echo -n "Memex API (8891): "
curl -s http://localhost:8891/ > /dev/null && echo "OK" || echo "NOT RUNNING"

# ChromaDB
echo -n "ChromaDB: "
python3 -c "import chromadb; c = chromadb.PersistentClient('./data/chromadb'); print('OK')" 2>/dev/null || echo "FAILED"

echo "=========================="
```

---

_Document generated by Nike on February 1, 2026_
