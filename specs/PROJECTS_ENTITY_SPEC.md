# Projects Entity - Technical Specification

**Entity**: `projects`
**Phase**: 2 - CodeFRAME Agent Integration
**Status**: ✅ Ready for Implementation
**Created**: 2026-01-01
**Owner**: CodeFRAME CLI Team

---

## Table of Contents

- [Overview](#overview)
- [User Stories](#user-stories)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [CLI Commands](#cli-commands)
- [API Integration](#api-integration)
- [Implementation Plan](#implementation-plan)
- [Testing Strategy](#testing-strategy)
- [Success Metrics](#success-metrics)

---

## Overview

### Purpose

The Projects entity provides multi-repository grouping for complex projects. While most projects have a 1:1 mapping with repositories, some projects (like `gregory-taylor-photography`) span multiple repositories (`gregory-taylor-backend`, `gregory-taylor-frontend`).

Projects serve as the organizational unit for:
- Grouping related repositories
- Managing specifications (PRDs, technical docs)
- Coordinating multi-repo development sessions
- Tracking cross-repo deployments

### Key Capabilities

1. **Multi-Repo Grouping**: Link multiple GitHub repos to a single project
2. **Auto-Detection**: Detect current project from git repo in working directory
3. **Spec Management**: Associate PRDs and technical specs with projects
4. **Session Context**: Provide project context to CodeFRAME sessions
5. **Dashboard View**: Cross-repo status (issues, PRs, deployments)

### Design Decisions

**Decision 1: Database Storage Strategy**
- **Chosen**: Sync to CodeFRAME core database
- **Rationale**: CodeFRAME core needs project context for sessions, specs, and multi-repo coordination
- **Implementation**: CLI manages projects, syncs to core via API

**Decision 2: Default Project Behavior**
- **Chosen**: Auto-detect from current directory (git repo name)
- **Fallback**: Use last-used project (stored in `~/.config/codeframe-cli/state.json`)
- **Override**: `--project` flag or `CF_PROJECT` env var

**Decision 3: Repository Mapping**
- **Storage**: Both CLI DB and CodeFRAME core DB (synced)
- **Format**: Many-to-many via `project_repos` join table
- **Validation**: Verify repos exist on GitHub during add

---

## User Stories

### Story 1: Create Multi-Repo Project
```
As a developer,
I want to create a project that groups my backend and frontend repos,
So that I can manage them as a single unit.

Acceptance Criteria:
- Can create project with multiple repos in one command
- Repos are validated against GitHub
- Project appears in CodeFRAME core
- Can view project details with `cf projects view`
```

**Example**:
```bash
cf projects create gregory-taylor-photography \
  --repos "frankbria/gregory-taylor-backend,frankbria/gregory-taylor-frontend" \
  --description "Professional photography portfolio and booking platform"
```

### Story 2: Auto-Detect Current Project
```
As a developer working in a project repo,
I want commands to auto-detect the current project,
So I don't have to specify --project every time.

Acceptance Criteria:
- CLI detects project from git remote URL
- Falls back to last-used project if not in a git repo
- Can override with --project flag
- Shows detected project in command output
```

**Example**:
```bash
cd ~/projects/gregory-taylor-backend
cf issues list
# Output: Listing issues for project 'gregory-taylor-photography'...
```

### Story 3: View Cross-Repo Status
```
As a project manager,
I want to see the status of all repos in a project,
So I can track progress across the entire project.

Acceptance Criteria:
- Shows open issues per repo
- Shows active PRs per repo
- Shows active CodeFRAME sessions
- Shows recent deployments
- Updates in real-time or on-demand
```

**Example**:
```bash
cf projects view gregory-taylor-photography

# Output:
# Project: gregory-taylor-photography
# Description: Professional photography portfolio and booking platform
#
# Repositories (2):
#   frankbria/gregory-taylor-backend
#     - Open issues: 12
#     - Active PRs: 2
#     - Last deployment: 2026-01-01 10:30 AM (production)
#
#   frankbria/gregory-taylor-frontend
#     - Open issues: 8
#     - Active PRs: 1
#     - Last deployment: 2026-01-01 09:15 AM (production)
#
# Active Sessions (1):
#   session-abc123: Building feature #45 (backend)
#   Status: In progress - Test worker running
#   Cost: $2.34
```

### Story 4: Manage Project Repos
```
As a developer,
I want to add or remove repos from a project,
So I can adjust the project structure as needed.

Acceptance Criteria:
- Can add repo to existing project
- Can remove repo from project
- Changes sync to CodeFRAME core
- Validates repos exist on GitHub
```

**Example**:
```bash
# Add mobile app repo later
cf projects add-repo gregory-taylor-photography \
  frankbria/gregory-taylor-mobile

# Remove deprecated repo
cf projects remove-repo gregory-taylor-photography \
  frankbria/gregory-taylor-legacy
```

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CodeFRAME CLI                           │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │  cli.py      │────────▶│ cli_projects │                │
│  │  (entry)     │         │   .py        │                │
│  └──────────────┘         └───────┬──────┘                │
│                                    │                        │
│                           ┌────────▼──────────┐            │
│                           │ entities/         │            │
│                           │  project.py       │            │
│                           │ ┌───────────────┐ │            │
│                           │ │ ProjectRepo   │ │            │
│                           │ │ - create()    │ │            │
│                           │ │ - list()      │ │            │
│                           │ │ - get()       │ │            │
│                           │ │ - add_repo()  │ │            │
│                           │ │ - delete()    │ │            │
│                           │ └───────────────┘ │            │
│                           └────────┬──────────┘            │
│                                    │                        │
│         ┌──────────────────────────┼──────────────┐        │
│         │                          │              │        │
│    ┌────▼─────┐            ┌──────▼──────┐  ┌───▼─────┐  │
│    │ SQLite   │            │ API Client  │  │ GitHub  │  │
│    │ (local)  │            │ (to core)   │  │ API     │  │
│    └──────────┘            └─────────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST/GET
                                    │
┌───────────────────────────────────▼─────────────────────────┐
│                    CodeFRAME Core                           │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │  ui/routers/projects.py                  │              │
│  │  - POST /api/projects                    │              │
│  │  - GET  /api/projects/{id}               │              │
│  │  - PUT  /api/projects/{id}/repos         │              │
│  └─────────────────┬────────────────────────┘              │
│                    │                                        │
│  ┌─────────────────▼────────────────────────┐              │
│  │  persistence/repositories/               │              │
│  │    project_repository.py                 │              │
│  │  - create_project()                      │              │
│  │  - add_project_repo()                    │              │
│  │  - get_project_repos()                   │              │
│  └─────────────────┬────────────────────────┘              │
│                    │                                        │
│  ┌─────────────────▼────────────────────────┐              │
│  │  SQLite (codeframe.db)                   │              │
│  │  - projects table                        │              │
│  │  - project_repos table                   │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Project Creation Flow**:
1. User runs: `cf projects create my-project --repos "owner/repo1,owner/repo2"`
2. CLI validates repos exist on GitHub (via GitHub API)
3. CLI creates project in local SQLite
4. CLI syncs to CodeFRAME core via `POST /api/projects`
5. Core creates project in core DB
6. Core creates project-repo mappings
7. CLI displays confirmation

**Project Auto-Detection Flow**:
1. User runs: `cf issues list` (no --project flag)
2. CLI checks current directory for git repo
3. Extracts remote URL (e.g., `git@github.com:frankbria/gregory-taylor-backend.git`)
4. Queries local DB for project containing this repo
5. Uses found project as context
6. If not found, uses last-used project from state file

**Project View Flow**:
1. User runs: `cf projects view my-project`
2. CLI fetches project details from local DB
3. CLI fetches repo stats from CodeFRAME API:
   - Open issues per repo (via `GET /api/projects/{id}/repos/{repo}/issues`)
   - Active PRs (via GitHub API)
   - Active sessions (via `GET /api/sessions?project_id={id}`)
   - Recent deployments (via `GET /api/deployments?project_id={id}`)
4. CLI renders Rich table with aggregated data

---

## Database Schema

### CLI Database (codeframe-cli)

```sql
-- Projects table (local cache + metadata)
CREATE TABLE projects (
  project_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP,
  core_project_id INTEGER,  -- FK to CodeFRAME core project
  sync_status TEXT CHECK (sync_status IN ('synced', 'pending', 'error')) DEFAULT 'pending',
  UNIQUE(name)
);

-- Project-Repository mapping
CREATE TABLE project_repos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  repo_name TEXT NOT NULL,  -- Format: "owner/repo"
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
  UNIQUE(project_id, repo_name)
);

-- Indexes for performance
CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_project_repos_repo ON project_repos(repo_name);
CREATE INDEX idx_project_repos_project ON project_repos(project_id);
```

### CodeFRAME Core Database

**Note**: These tables need to be added to CodeFRAME core schema.

```sql
-- Projects table (authoritative source)
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  workspace_path TEXT,  -- Path to local workspace (optional)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project-Repository mapping
CREATE TABLE IF NOT EXISTS project_repos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  repo_name TEXT NOT NULL,  -- Format: "owner/repo"
  repo_url TEXT,  -- Full GitHub URL
  default_branch TEXT DEFAULT 'main',
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  UNIQUE(project_id, repo_name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_project_repos_project ON project_repos(project_id);
CREATE INDEX IF NOT EXISTS idx_project_repos_repo ON project_repos(repo_name);
```

### Migration Strategy

**Phase 1: Add to CodeFRAME Core**
1. Add migration script: `codeframe/migrations/014_add_projects.sql`
2. Update `SchemaManager` to apply migration
3. Add `ProjectRepository` to `codeframe/persistence/repositories/`
4. Add API endpoints to `codeframe/ui/routers/projects.py`

**Phase 2: CLI Implementation**
1. Add CLI database tables via migration: `codeframe-cli/migrations/002_add_projects.sql`
2. Implement `ProjectRepository` in CLI
3. Implement sync logic (CLI → Core API)

**Rollback Plan**:
- Keep tables but mark as unused
- CLI gracefully handles missing core API endpoints
- No data loss (SQLite supports schema versioning)

---

## CLI Commands

### `cf projects create`

**Signature**:
```bash
cf projects create PROJECT_NAME [OPTIONS]
```

**Options**:
- `--repos REPOS` - Comma-separated list of repos (format: `owner/repo`)
- `--description DESC` - Project description
- `--workspace PATH` - Path to local workspace (optional)

**Behavior**:
1. Validate project name (alphanumeric + hyphens, no spaces)
2. Validate repos exist on GitHub (via GitHub API)
3. Create project in local DB
4. Sync to CodeFRAME core via API
5. Display confirmation with project ID

**Example**:
```bash
$ cf projects create gregory-taylor-photography \
    --repos "frankbria/gregory-taylor-backend,frankbria/gregory-taylor-frontend" \
    --description "Professional photography portfolio"

✓ Validating repositories on GitHub...
  ✓ frankbria/gregory-taylor-backend (exists)
  ✓ frankbria/gregory-taylor-frontend (exists)

✓ Creating project in local database...
✓ Syncing to CodeFRAME core...

Project created successfully!
  Name: gregory-taylor-photography
  ID: 1
  Repositories: 2
  Description: Professional photography portfolio

Run 'cf projects view gregory-taylor-photography' to see details.
```

**Error Handling**:
- Invalid project name → Show naming rules
- Repo doesn't exist on GitHub → List invalid repos
- Duplicate project name → Suggest using `cf projects view` instead
- Core API unavailable → Create locally, mark as pending sync

---

### `cf projects list`

**Signature**:
```bash
cf projects list [OPTIONS]
```

**Options**:
- `--format FORMAT` - Output format (table|json|yaml)
- `--sort-by FIELD` - Sort by (name|created|last-used)

**Behavior**:
1. Fetch all projects from local DB
2. Enrich with stats from Core API (optional, cached)
3. Display in Rich table

**Example**:
```bash
$ cf projects list

Projects (3)

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID ┃ Name                      ┃ Repos┃ Sessions┃ Last Used  ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1  │ gregory-taylor-photography│ 2    │ 1       │ 2 hours ago│
│ 2  │ personal-website          │ 1    │ 0       │ 3 days ago │
│ 3  │ codeframe-experiments     │ 1    │ 0       │ 1 week ago │
└────┴───────────────────────────┴──────┴─────────┴────────────┘

Run 'cf projects view <name>' for details.
```

---

### `cf projects view`

**Signature**:
```bash
cf projects view PROJECT_NAME [OPTIONS]
```

**Options**:
- `--format FORMAT` - Output format (table|json|yaml)
- `--live` - Live updating view (auto-refresh every 5s)

**Behavior**:
1. Fetch project from local DB
2. Fetch repo stats from CodeFRAME API:
   - Open issues (via Core API)
   - Active PRs (via GitHub API)
   - Active sessions (via Core API)
   - Recent deployments (via Core API)
3. Render Rich panel with stats

**Example**:
```bash
$ cf projects view gregory-taylor-photography

╭─ Project: gregory-taylor-photography ────────────────────────╮
│ Professional photography portfolio and booking platform      │
│                                                              │
│ Repositories (2):                                            │
│                                                              │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓│
│ ┃ Repository                    ┃ Issues┃ PRs   ┃ Deployed ┃│
│ ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩│
│ │ frankbria/gregory-taylor-back…│ 12    │ 2     │ 1h ago   ││
│ │ frankbria/gregory-taylor-front│ 8     │ 1     │ 2h ago   ││
│ └───────────────────────────────┴───────┴───────┴──────────┘│
│                                                              │
│ Active Sessions (1):                                         │
│   • session-abc123: Building feature #45                    │
│     Status: Test worker running                              │
│     Cost: $2.34                                              │
│                                                              │
│ Recent Activity:                                             │
│   • 1h ago - Deployed backend to production                 │
│   • 2h ago - Deployed frontend to production                │
│   • 3h ago - PR #23 merged (frontend)                       │
│                                                              │
│ Project ID: 1                                                │
│ Created: 2025-12-15                                          │
╰──────────────────────────────────────────────────────────────╯
```

---

### `cf projects add-repo`

**Signature**:
```bash
cf projects add-repo PROJECT_NAME REPO
```

**Arguments**:
- `PROJECT_NAME` - Project name
- `REPO` - Repository in format `owner/repo`

**Behavior**:
1. Validate repo exists on GitHub
2. Add to local DB
3. Sync to Core API
4. Display confirmation

**Example**:
```bash
$ cf projects add-repo gregory-taylor-photography \
    frankbria/gregory-taylor-mobile

✓ Validating repository...
  ✓ frankbria/gregory-taylor-mobile (exists)

✓ Adding to project...
✓ Syncing to CodeFRAME core...

Repository added successfully!
  Project: gregory-taylor-photography
  Repository: frankbria/gregory-taylor-mobile
  Total repositories: 3
```

---

### `cf projects remove-repo`

**Signature**:
```bash
cf projects remove-repo PROJECT_NAME REPO [OPTIONS]
```

**Arguments**:
- `PROJECT_NAME` - Project name
- `REPO` - Repository in format `owner/repo`

**Options**:
- `--force` - Skip confirmation prompt

**Behavior**:
1. Confirm with user (unless --force)
2. Remove from local DB
3. Sync to Core API
4. Display confirmation

**Example**:
```bash
$ cf projects remove-repo gregory-taylor-photography \
    frankbria/gregory-taylor-legacy

⚠ Remove frankbria/gregory-taylor-legacy from project?
  This will not delete the repository, only remove it from the project.
  Continue? [y/N]: y

✓ Removing from project...
✓ Syncing to CodeFRAME core...

Repository removed successfully!
  Project: gregory-taylor-photography
  Repository: frankbria/gregory-taylor-legacy
  Remaining repositories: 2
```

---

### `cf projects delete`

**Signature**:
```bash
cf projects delete PROJECT_NAME [OPTIONS]
```

**Arguments**:
- `PROJECT_NAME` - Project name

**Options**:
- `--force` - Skip confirmation prompt

**Behavior**:
1. Confirm with user (unless --force)
2. Check for active sessions → warn if any
3. Delete from local DB (cascade to project_repos)
4. Sync to Core API
5. Display confirmation

**Example**:
```bash
$ cf projects delete old-experiment

⚠ Delete project 'old-experiment'?
  This will:
  - Remove the project and all repository mappings
  - NOT delete the actual repositories
  - NOT delete any specs or issues
  Continue? [y/N]: y

✓ Deleting project...
✓ Syncing to CodeFRAME core...

Project deleted successfully!
  Name: old-experiment
  Repositories removed: 1
```

---

## API Integration

### CodeFRAME Core API Endpoints (To Be Implemented)

#### `POST /api/projects`

**Purpose**: Create new project

**Request**:
```json
{
  "name": "gregory-taylor-photography",
  "description": "Professional photography portfolio",
  "repos": [
    {
      "repo_name": "frankbria/gregory-taylor-backend",
      "repo_url": "https://github.com/frankbria/gregory-taylor-backend",
      "default_branch": "main"
    },
    {
      "repo_name": "frankbria/gregory-taylor-frontend",
      "repo_url": "https://github.com/frankbria/gregory-taylor-frontend",
      "default_branch": "main"
    }
  ],
  "workspace_path": null
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "gregory-taylor-photography",
  "description": "Professional photography portfolio",
  "workspace_path": null,
  "created_at": "2026-01-01T10:00:00Z",
  "repos": [
    {
      "id": 1,
      "repo_name": "frankbria/gregory-taylor-backend",
      "repo_url": "https://github.com/frankbria/gregory-taylor-backend",
      "default_branch": "main"
    },
    {
      "id": 2,
      "repo_name": "frankbria/gregory-taylor-frontend",
      "repo_url": "https://github.com/frankbria/gregory-taylor-frontend",
      "default_branch": "main"
    }
  ]
}
```

**Errors**:
- `409 Conflict` - Project name already exists
- `400 Bad Request` - Invalid request payload

---

#### `GET /api/projects`

**Purpose**: List all projects

**Request**: None

**Response** (200 OK):
```json
{
  "projects": [
    {
      "id": 1,
      "name": "gregory-taylor-photography",
      "description": "Professional photography portfolio",
      "repo_count": 2,
      "created_at": "2026-01-01T10:00:00Z"
    }
  ]
}
```

---

#### `GET /api/projects/{id}`

**Purpose**: Get project details

**Request**: None

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "gregory-taylor-photography",
  "description": "Professional photography portfolio",
  "workspace_path": null,
  "created_at": "2026-01-01T10:00:00Z",
  "repos": [
    {
      "id": 1,
      "repo_name": "frankbria/gregory-taylor-backend",
      "repo_url": "https://github.com/frankbria/gregory-taylor-backend",
      "default_branch": "main",
      "stats": {
        "open_issues": 12,
        "open_prs": 2
      }
    }
  ],
  "active_sessions": [
    {
      "id": "session-abc123",
      "status": "active",
      "current_task": "Building feature #45",
      "cost": 2.34
    }
  ]
}
```

**Errors**:
- `404 Not Found` - Project doesn't exist

---

#### `PUT /api/projects/{id}/repos`

**Purpose**: Add repository to project

**Request**:
```json
{
  "action": "add",
  "repo_name": "frankbria/gregory-taylor-mobile",
  "repo_url": "https://github.com/frankbria/gregory-taylor-mobile",
  "default_branch": "main"
}
```

**Response** (200 OK):
```json
{
  "id": 3,
  "repo_name": "frankbria/gregory-taylor-mobile",
  "repo_url": "https://github.com/frankbria/gregory-taylor-mobile",
  "default_branch": "main"
}
```

---

#### `DELETE /api/projects/{id}/repos/{repo_id}`

**Purpose**: Remove repository from project

**Request**: None

**Response** (204 No Content)

**Errors**:
- `404 Not Found` - Project or repo doesn't exist
- `400 Bad Request` - Can't remove last repo from project

---

#### `DELETE /api/projects/{id}`

**Purpose**: Delete project

**Request**: None

**Response** (204 No Content)

**Errors**:
- `404 Not Found` - Project doesn't exist
- `409 Conflict` - Active sessions exist

---

### GitHub API Integration

**Used For**:
- Repository validation (check if repo exists)
- Fetching PR counts
- Fetching issue counts

**Rate Limiting**:
- Cache GitHub API responses (5-minute TTL)
- Respect GitHub rate limits (5000 req/hour for authenticated)

**Error Handling**:
- `404` → Repo doesn't exist
- `403` → Rate limit exceeded → Use cached data
- `401` → Invalid token → Show error, suggest re-auth

---

## Implementation Plan

### Phase 1: Database & Core API (Week 1)

**Tasks**:
1. ✅ **Design database schema** (DONE)
2. **Add migration to CodeFRAME core**:
   - Create `codeframe/migrations/014_add_projects.sql`
   - Update `SchemaManager` to apply migration
3. **Implement `ProjectRepository` in core**:
   - `create_project(name, description, repos)`
   - `get_project(id)`
   - `list_projects()`
   - `add_project_repo(project_id, repo)`
   - `remove_project_repo(project_id, repo_id)`
   - `delete_project(id)`
4. **Add API endpoints to core**:
   - Create `codeframe/ui/routers/projects.py`
   - Implement 6 endpoints (POST, GET, GET/id, PUT/repos, DELETE/repos, DELETE)
   - Add authentication decorators
5. **Testing**:
   - Unit tests for `ProjectRepository`
   - Integration tests for API endpoints
   - E2E test for project creation flow

**Deliverables**:
- Migration script applied
- API endpoints functional
- Tests passing (>85% coverage)

---

### Phase 2: CLI Implementation (Week 2)

**Tasks**:
1. **CLI database migration**:
   - Create `migrations/002_add_projects.sql`
   - Add migration runner to CLI
2. **Implement `entities/project.py`**:
   - `ProjectRepository` (local DB operations)
   - `Project` entity class
   - Sync logic (CLI → Core API)
3. **Implement API client**:
   - `lib/api_client.py` - HTTP client for Core API
   - `create_project()`, `get_project()`, etc.
   - Error handling and retries
4. **Implement `cli_projects.py`**:
   - `setup_projects_parser()`
   - `cmd_projects_create()`
   - `cmd_projects_list()`
   - `cmd_projects_view()`
   - `cmd_projects_add_repo()`
   - `cmd_projects_remove_repo()`
   - `cmd_projects_delete()`
5. **Implement auto-detection**:
   - Detect git repo from current directory
   - Query local DB for project containing repo
   - Fallback to last-used project
6. **Implement formatters**:
   - Rich table output for `list` and `view`
   - JSON/YAML formatters
7. **Testing**:
   - Unit tests for `ProjectRepository`
   - Integration tests (CLI → Core API)
   - E2E tests for each command

**Deliverables**:
- All 6 commands functional
- Auto-detection working
- Tests passing (>85% coverage)
- Documentation updated

---

### Phase 3: Integration & Polish (Week 3)

**Tasks**:
1. **Integrate with other entities**:
   - Update `issues` commands to use project context
   - Update `sessions` commands to accept `--project`
2. **Add state management**:
   - Track last-used project in `~/.config/codeframe-cli/state.json`
   - Update on every command using `--project`
3. **Error handling polish**:
   - User-friendly error messages
   - Retry logic for API failures
   - Offline mode (graceful degradation)
4. **Performance optimization**:
   - Cache project list (5-minute TTL)
   - Cache GitHub API responses
5. **Documentation**:
   - Update README.md with projects commands
   - Add examples to CLAUDE.md
   - Create user guide

**Deliverables**:
- Seamless integration with existing commands
- Robust error handling
- Complete documentation

---

## Testing Strategy

### Unit Tests

**Coverage Target**: >85%

**Test Cases**:
1. `ProjectRepository.create_project()`:
   - ✅ Creates project with valid data
   - ✅ Validates project name (no spaces, special chars)
   - ✅ Returns project ID
   - ✅ Handles duplicate names

2. `ProjectRepository.add_repo()`:
   - ✅ Adds repo to project
   - ✅ Validates repo format
   - ✅ Prevents duplicate repos
   - ✅ Returns repo ID

3. `ProjectRepository.get_project()`:
   - ✅ Returns project by name
   - ✅ Returns None if not found
   - ✅ Includes repo list

4. Auto-detection:
   - ✅ Detects project from git remote URL
   - ✅ Falls back to last-used project
   - ✅ Returns None if no context

### Integration Tests

**Test Cases**:
1. Create project flow:
   - CLI creates project locally
   - CLI syncs to Core API
   - Core creates project in DB
   - CLI updates local cache with core ID

2. Add repo flow:
   - CLI validates repo on GitHub
   - CLI adds to local DB
   - CLI syncs to Core API
   - Core adds repo mapping

3. View project flow:
   - CLI fetches project from local DB
   - CLI fetches stats from Core API
   - CLI renders Rich table

### E2E Tests

**Test Scenarios**:
1. Multi-repo project creation:
   ```bash
   cf projects create test-project \
     --repos "owner/repo1,owner/repo2" \
     --description "Test"
   cf projects view test-project
   cf projects delete test-project --force
   ```

2. Auto-detection:
   ```bash
   cd /tmp/test-repo
   git init
   git remote add origin git@github.com:owner/repo1.git
   cf issues list  # Should detect project
   ```

3. Repo management:
   ```bash
   cf projects create test-project --repos "owner/repo1"
   cf projects add-repo test-project owner/repo2
   cf projects remove-repo test-project owner/repo1 --force
   ```

---

## Success Metrics

### Performance Targets

- ✅ Project creation: <2 seconds (including GitHub validation)
- ✅ Project list: <1 second for 20 projects
- ✅ Project view: <2 seconds (with stats from Core API)
- ✅ Auto-detection: <100ms

### Quality Targets

- ✅ Test coverage: >85%
- ✅ All commands have --help text
- ✅ Error messages are actionable
- ✅ No silent failures

### User Experience Targets

- ✅ User never needs to specify project if working in repo directory
- ✅ `cf projects view` shows all relevant info without additional commands
- ✅ Offline mode: CLI works without Core API (limited functionality)

---

## Open Questions

### Resolved

✅ **Q1.1**: Store project-repo mapping in CLI DB only, or sync to CodeFRAME core?
- **Answer**: Sync to core (both databases have projects)

✅ **Q1.3**: Default project behavior?
- **Answer**: Auto-detect from current directory (git repo name)

### Remaining

**Q1.4**: Should projects have a "default repo" concept?
- Use case: Multi-repo project, but most work is in one repo
- Benefit: Could default to that repo for certain commands
- **Recommendation**: Defer to Phase 3 (not critical for MVP)

**Q1.5**: Project archival/deletion?
- Should we support archiving (soft delete) vs hard delete?
- **Recommendation**: Hard delete for MVP, add archive later if needed

---

## Next Steps

1. ✅ **Spec complete** - Ready for review
2. **Get approval** - Review with team
3. **Implement Phase 1** - Core API (Week 1)
4. **Implement Phase 2** - CLI (Week 2)
5. **Integrate & polish** - Phase 3 (Week 3)

**Estimated completion**: 3 weeks from approval

---

## Appendix

### Example State File

```json
{
  "last_used_project": "gregory-taylor-photography",
  "project_history": [
    {"name": "gregory-taylor-photography", "used_at": "2026-01-01T14:30:00Z"},
    {"name": "personal-website", "used_at": "2025-12-30T10:15:00Z"}
  ]
}
```

### Example Config File

```yaml
# ~/.config/codeframe-cli/config.yaml
projects:
  auto_detect: true
  default: null  # or project name
  cache_ttl_seconds: 300  # 5 minutes
```

### GitHub API Examples

```python
# Validate repo exists
import httpx

async def validate_github_repo(repo_name: str, token: str) -> bool:
    """Check if GitHub repo exists."""
    headers = {"Authorization": f"token {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo_name}",
            headers=headers
        )
        return response.status_code == 200
```
