# Spec Readiness Assessment

**Date**: 2026-01-01
**Status**: 🟡 **80% Ready** - Can start specs with some open questions

---

## What We Have ✅

### 1. Comprehensive Roadmap
- ✅ 14 entities defined with commands
- ✅ Database schemas designed
- ✅ Phase breakdown (1-5)
- ✅ Success metrics per phase
- ✅ Integration points identified

### 2. CodeFRAME Core Understanding
- ✅ **API Structure**: FastAPI with 14 routers (agents, blockers, tasks, metrics, etc.)
- ✅ **Database**: SQLite with repository pattern (17 repositories)
- ✅ **WebSocket**: `/ws` endpoint for real-time updates
- ✅ **Session Management**: `.codeframe/session_state.json` file storage
- ✅ **Web-UI**: Next.js app at `http://localhost:8000`

### 3. Existing Patterns
- ✅ CLI architecture (object-command pattern established)
- ✅ Database context manager pattern
- ✅ Rich TUI components (from Phase 1)
- ✅ Error handling (circuit breaker pattern)

---

## Open Questions 🤔

### Phase 2 Implementation Questions

#### 1. Projects Entity

**Q1.1**: Project-Repo Mapping Storage
- Where should project-repo mapping live?
  - Option A: Only in CLI database (`projects`, `project_repos` tables)
  - Option B: Add to CodeFRAME core database (shared state)
  - Option C: Hybrid (CLI manages, syncs to core on session start)
- **✅ DECISION**: Sync to CodeFRAME core (Option B/C)
- **Rationale**: Core needs project context for sessions and multi-repo coordination

**Q1.2**: Project Auto-Discovery
- Should CLI auto-discover projects from:
  - GitHub organizations?
  - Local filesystem (scan for `.codeframe/` directories)?
  - CodeFRAME core database (if it has project concept)?
- **Recommendation**: Start with manual creation, add auto-discovery in Phase 3

**Q1.3**: Default Project Behavior
- When user doesn't specify `--project`, should CLI:
  - Auto-detect from current directory?
  - Use last-used project?
  - Require explicit specification?
- **Recommendation**: Auto-detect from current directory (git repo name)

#### 2. Specs Entity

**Q2.1**: Spec Storage Location
- Where to store spec content?
  - Option A: SQLite `specs` table (content as TEXT)
  - Option B: Git repo (`docs/specs/prd.md`)
  - Option C: Both (database metadata, git for content + version history)
- **✅ DECISION**: Specs in Git (Option B/C)
- **Rationale**: Version control for specs, easier collaboration, familiar workflow
- **Storage location**: Project repository (`docs/specs/` directory)

**Q2.2**: AI Spec→Issues Generation
- Which AI model/service?
  - CodeFRAME's existing LLM integration (Anthropic SDK)?
  - Separate CLI-managed integration?
- What's the prompt template?
  - Need to define spec parsing → issue breakdown prompt
- How granular should issues be?
  - Target: 1-3 days of work per issue?
  - Or user-configurable granularity?
- **Recommendation**: Use CodeFRAME's existing LLM setup, 1-3 day granularity
- **Decision needed**: Prompt template design (need example PRD → issues)

**Q2.3**: Spec Approval Workflow
- Who can approve specs?
  - Only project owner?
  - Any team member?
  - Multi-approver support?
- **Recommendation**: Start with single-approver (project owner)

#### 3. Sessions Entity & CodeFRAME Integration

**Q3.1**: CLI ↔ Core Communication Protocol

**REST API Endpoints** (to implement or verify):
- `POST /api/sessions/create` - Create new session
  - Payload: `{project_id, issue_id?, model?, ...}`
  - Returns: `{session_id, status}`
- `GET /api/sessions/{session_id}` - Get session status
  - Returns: `{status, agents[], blockers[], cost, ...}`
- `POST /api/sessions/{session_id}/pause` - Pause session
- `POST /api/sessions/{session_id}/resume` - Resume session
- `DELETE /api/sessions/{session_id}` - End session

**Question**: Do these endpoints exist in CodeFRAME core?
- From routers: I see `/api/projects/{project_id}/session` (GET only)
- **Action needed**: Audit existing CodeFRAME API surface
- **Decision needed**: If missing, implement in core or CLI wrapper?

**Q3.2**: WebSocket Message Protocol
- What's the WebSocket message format for:
  - Agent status updates?
  - Blocker notifications?
  - Cost updates?
- **Action needed**: Document existing WebSocket protocol from `routers/websocket.py`
- **Recommendation**: Use existing protocol, extend if needed

**Q3.3**: Database Synchronization
- CodeFRAME core has its own SQLite database
- CLI will have its own SQLite database
- How to keep them in sync?
  - Option A: Shared database file (both read/write same file)
  - Option B: CLI reads core DB, writes to own DB
  - Option C: API-only (CLI never touches core DB directly)
- **✅ DECISION**: Shared database for underlying data, API for communication
- **Rationale**: Shared DB for data consistency, API for controlled access and validation
- **Implementation**: CLI and Core share `codeframe.db`, but CLI uses API for all write operations

**Q3.4**: Web-UI Launch Mechanics
- How does CLI launch web-ui?
  - Option A: Subprocess management (`subprocess.Popen(["npm", "run", "dev"])`)
  - Option B: Detect if already running, open browser only
  - Option C: HTTP health check → launch if needed
- **✅ DECISION**: Launch if needed (Option C)
- **Implementation**:
  1. Check health endpoint: `GET http://localhost:8000/api/health`
  2. If not running: Launch web-ui subprocess (`npm run dev` or `uv run codeframe ui`)
  3. Wait for health check to pass (max 10s)
  4. Open browser to `http://localhost:8000`
- **Browser**: Use `webbrowser.open()` (system default)

**Q3.5**: Headless Mode Requirements
- In headless mode (no `--ui`), how does user interact with blockers?
  - Option A: Desktop notifications + CLI prompt
  - Option B: Poll for blockers, show in `cf sessions status`
  - Option C: Both (notifications + polling)
- **Recommendation**: Option C for best UX

#### 4. Agents Entity

**Q4.1**: Agent Launch via CLI
- Should `cf agents launch` directly call CodeFRAME or go through sessions?
  - Option A: `cf agents launch` → `cf sessions start` → CodeFRAME
  - Option B: `cf agents launch` → direct CodeFRAME agent API
- **Recommendation**: Option A (sessions are the abstraction layer)

**Q4.2**: Cost Tracking
- CodeFRAME has `token_usage` repository
- How does CLI access this?
  - Via API: `GET /api/sessions/{session_id}/costs`?
  - Direct DB read?
- **Recommendation**: API endpoint for real-time costs

#### 5. Configuration Management

**Q5.1**: Config File Location
- Where to store CLI configuration?
  - `~/.config/codeframe-cli/config.yaml`?
  - `~/.codeframe/cli-config.yaml`?
  - Project-specific: `.codeframe/cli.yaml`?
- **Recommendation**: Both global (`~/.config/codeframe-cli/`) and per-project (`.codeframe/cli.yaml`)

**Q5.2**: Credential Storage
- How to store encrypted credentials (GitHub token, platform API keys)?
  - System keyring (keyring library)?
  - Encrypted file?
  - Plain text (user responsibility)?
- **Recommendation**: System keyring for security

**Q5.3**: Config Schema
```yaml
# ~/.config/codeframe-cli/config.yaml
codeframe_core:
  url: "http://localhost:8000"
  auto_launch_ui: false

github:
  token: "<encrypted-or-keyring-ref>"
  username: "frankbria"

projects:
  default: "gregory-taylor-photography"
  auto_detect: true

display:
  format: "table"  # table|json|yaml
  theme: "dark"    # dark|light

notifications:
  desktop: true
  webhook: null
```

**Q5.4**: Multi-Environment Support
- Should CLI support connecting to different CodeFRAME instances?
  - Local dev: `http://localhost:8000`
  - Staging: `https://codeframe-staging.example.com`
  - Production: `https://codeframe.example.com`
- **Recommendation**: Yes, via config or `--env` flag

### Phase 4 Questions (Lower Priority)

#### 6. Deployment Environments

**Q6.1**: Platform Integration Priority
- Which deployment platforms to support first?
  - Vercel (easiest API, common for Next.js)
  - Railway (good API, popular)
  - VPS (most flexible, hardest to abstract)
- **Recommendation**: Vercel first (Gregory Taylor uses it?)

**Q6.2**: Environment Credentials
- How to handle platform API keys securely?
  - Per-project config file (encrypted)?
  - System keyring?
  - Environment variables?
- **Recommendation**: System keyring with per-project env vars as fallback

---

## What We Need to Proceed

### 1. CodeFRAME Core API Audit

**Action**: Document existing REST API endpoints

```bash
# Run this in CodeFRAME core repository
# Clone from: https://github.com/frankbria/codeframe
grep -r "@router\." codeframe/ui/routers/*.py | grep "def " > api_endpoints.txt
```

**Deliverable**: API endpoint inventory with:
- Method + Path
- Request payload schema
- Response schema
- Authentication requirements

### 2. WebSocket Protocol Documentation

**Action**: Document WebSocket message format

**Questions**:
- What messages does server send to clients?
- What messages do clients send to server?
- Message schema (JSON format)?

### 3. Example Spec → Issues Workflow

**Action**: Create example PRD and expected issue breakdown

**Example**:
```markdown
# PRD: User Authentication System

## Overview
Add user authentication with email/password and OAuth (Google, GitHub).

## Requirements
- Email/password registration
- Email verification
- OAuth integration (Google, GitHub)
- Password reset flow
- Session management (JWT)
- Rate limiting on auth endpoints

## Success Metrics
- < 2s login time
- > 99.9% uptime
- Zero credential leaks
```

**Expected Issues** (AI-generated):
1. "Implement email/password registration backend" (backend, 2 days)
2. "Create registration UI with form validation" (frontend, 1 day)
3. "Add email verification service" (backend, 1 day)
4. "Implement Google OAuth integration" (backend, 1 day)
5. "Implement GitHub OAuth integration" (backend, 1 day)
6. "Build OAuth callback handlers and UI" (frontend, 1 day)
7. "Create password reset flow (backend + email)" (backend, 2 days)
8. "Build password reset UI" (frontend, 1 day)
9. "Implement JWT session management" (backend, 2 days)
10. "Add rate limiting middleware" (backend, 1 day)
11. "Write E2E tests for auth flows" (test, 2 days)

**Decision needed**: Is this the right granularity?

### 4. Database Migration Strategy

**Action**: Design migration from current schema to Phase 2 schema

**Questions**:
- Use Alembic for migrations?
- Or manual SQL migration scripts?
- How to handle rollback?

**Recommendation**: SQL migration scripts (simpler for SQLite)

```sql
-- migrations/001_add_projects.sql
CREATE TABLE IF NOT EXISTS projects (
  project_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_repos (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,
  repo_name TEXT,
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  UNIQUE(project_id, repo_name)
);
```

### 5. CLI Module Structure Design

**Action**: Design Python module structure for Phase 2

**Proposed Structure**:
```
src/codeframe/
  cli.py              # Main entry point
  cli_issues.py       # Issues commands
  cli_repos.py        # Repos commands
  cli_projects.py     # NEW: Projects commands
  cli_specs.py        # NEW: Specs commands
  cli_sessions.py     # NEW: Sessions commands
  cli_agents.py       # NEW: Agents commands

  lib/
    api_client.py     # CodeFRAME API client (REST + WebSocket)
    config.py         # Configuration management
    formatters.py     # Output formatting (table, json, yaml)
    ui_launcher.py    # Web-UI launch logic

  entities/
    project.py        # Project entity + repository
    spec.py           # Spec entity + repository
    session.py        # Session entity (wraps CodeFRAME sessions)
    agent.py          # Agent entity (wraps CodeFRAME agents)
```

**Decision needed**: Is this structure aligned with your vision?

---

## Recommended Next Steps

### Immediate (This Week)

1. **CodeFRAME API Audit** ⚡ HIGH PRIORITY
   - Document all existing REST endpoints
   - Document WebSocket protocol
   - Identify gaps (missing endpoints we need)
   - **Deliverable**: `CODEFRAME_API.md` in CLI repo

2. **Answer Open Questions** ⚡ HIGH PRIORITY
   - Review questions above
   - Make decisions on:
     - Project-repo mapping storage (Q1.1)
     - Spec storage location (Q2.1)
     - Database synchronization strategy (Q3.3)
     - Web-UI launch mechanics (Q3.4)
   - **Deliverable**: Decisions documented in this file

3. **Create Example Spec→Issues** 📝 MEDIUM PRIORITY
   - Write example PRD
   - Define expected issue breakdown
   - Validate granularity with you
   - **Deliverable**: `examples/prd_to_issues.md`

### Short-Term (Next 2 Weeks)

4. **Phase 2 Technical Spec** 📋 Start after #1-3
   - Detailed implementation plan for:
     - Projects entity (commands, DB, logic)
     - Specs entity (commands, DB, AI integration)
     - Sessions entity (API client, WebSocket, UI launcher)
     - Agents entity (wrapper around CodeFRAME)
   - **Deliverable**: `PHASE_2_SPEC.md`

5. **Database Migration Design** 🗄️ Parallel with #4
   - SQL migration scripts
   - Rollback strategy
   - Testing plan
   - **Deliverable**: `migrations/` directory with scripts

6. **API Client Design** 🔌 Parallel with #4
   - REST client (httpx)
   - WebSocket client (websockets)
   - Reconnection logic
   - Error handling
   - **Deliverable**: `src/codeframe/lib/api_client.py` (skeleton)

---

## Spec Readiness by Entity

| Entity | Readiness | Blockers |
|--------|-----------|----------|
| **projects** | 🟢 90% | Q1.1 (storage), Q1.3 (default behavior) |
| **specs** | 🟡 70% | Q2.1 (storage), Q2.2 (AI prompt), example needed |
| **sessions** | 🟡 60% | API audit needed, Q3.1-3.5 |
| **agents** | 🟡 60% | Same as sessions (wraps sessions) |
| **repos** (enhanced) | 🟢 85% | Mostly extension of Phase 1 |
| **issues** (enhanced) | 🟢 85% | State tracking logic needed |

---

## Conclusion

**We can start creating specs now** with the understanding that some details will be filled in as we get answers to open questions.

**Recommended Approach**:
1. Start with **Projects entity spec** (highest readiness, fewest blockers)
2. While working on Projects, do **CodeFRAME API audit** in parallel
3. Use API audit results to finalize **Sessions/Agents specs**
4. Create **Specs entity spec** after resolving AI integration questions

**Timeline to Full Specs**:
- Projects spec: Ready now (can write today)
- CodeFRAME API audit: 2-3 days
- Sessions/Agents specs: 1 week (after API audit)
- Specs entity spec: 1 week (needs AI prompt design)

**Total time to complete Phase 2 specs: ~2 weeks**

---

**Questions for you:**
1. Should I start with Projects entity spec today?
2. Do you want me to do the CodeFRAME API audit first, or can we work in parallel?
3. Any of the open questions you can answer right now to unblock specs?
