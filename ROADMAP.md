# CodeFRAME CLI Roadmap

**Vision**: The command-line interface for autonomous AI development - orchestrating the entire lifecycle from ideation through deployment.

**Version**: 0.1.0 (Alpha)
**Last Updated**: 2026-01-01

---

## Table of Contents

- [Overview](#overview)
- [Architecture Philosophy](#architecture-philosophy)
- [Entity & Command Matrix](#entity--command-matrix)
- [Phase Roadmap](#phase-roadmap)
- [Technical Specifications](#technical-specifications)
- [Integration Points](#integration-points)
- [Future Vision](#future-vision)

---

## Overview

CodeFRAME CLI orchestrates AI-driven development across the entire software lifecycle:

```
IDEATION → PLANNING → BUILDING → REVIEWING → DEPLOYING → MONITORING
```

### Current State (Phase 1 ✅)
- **issues**: Traycer AI integration for automated issue planning
- **repos**: Repository health monitoring
- TUI dashboard with live monitoring
- Rate limit management with external activity detection

### Next Up (Phase 2 🚧)
- Cross-repo status views
- PR management and coordination
- Issue state tracking across lifecycle
- Integration with main CodeFRAME agents

---

## Architecture Philosophy

### Object-Command Pattern

```
cf <OBJECT> <COMMAND> [options]
```

**Objects** = High-level entities (issues, agents, deployments)
**Commands** = Actions on those entities (view, launch, status)

### Design Principles

1. **Orchestration, Not Implementation** - CLI coordinates services, doesn't do the work
2. **Async-First** - Non-blocking operations, live status updates
3. **Human-in-the-Loop** - Clear prompts when decisions needed
4. **Multi-Repo by Default** - Work across all repos unless filtered
5. **Progressive Disclosure** - Simple commands for common tasks, flags for advanced control

---

## Entity & Command Matrix

### Complete Entity Catalog

| Entity | Description | Phase | Status |
|--------|-------------|-------|--------|
| **issues** | GitHub issues and automated planning | 1 | ✅ Complete |
| **repos** | Repository health and status | 1 | ✅ Partial |
| **projects** | Multi-repo project grouping and management | 2 | 📋 Planned |
| **specs** | Project specifications (PRD, technical docs) | 2 | 📋 Planned |
| **agents** | CodeFRAME agent lifecycle management | 2 | 📋 Planned |
| **prs** | Pull request coordination | 3 | 📋 Planned |
| **sessions** | Development session management (CodeFRAME) | 2 | 📋 Planned |
| **reviews** | Code review orchestration | 3 | 📋 Planned |
| **deployments** | Deployment tracking (test/staging/prod) | 4 | 📋 Planned |
| **environments** | Environment-specific configuration | 4 | 📋 Planned |
| **metrics** | Cost, performance, and usage analytics | 4 | 📋 Planned |
| **checkpoints** | Project state snapshots | 3 | 📋 Planned |
| **workflows** | Custom automation pipelines | 5 | 🔮 Future |
| **ideas** | AI-powered idea generation | 5 | 🔮 Future |

**Note**: Projects map to one or more repos (e.g., `gregory-taylor-photography` project contains `gregory-taylor-backend` and `gregory-taylor-frontend` repos). Most projects are 1:1 with repos, but multi-repo projects are supported.

---

## Phase Roadmap

### ✅ Phase 1: Traycer Integration (COMPLETE)

**Goal**: Automated issue planning with intelligent rate limit management

**Delivered Entities:**
- `issues` - Full CRUD + Traycer queue management
- `repos` - Health monitoring

**Delivered Commands:**
```bash
# Issues
cf issues view [--live] [--refresh N]
cf issues create-plan [--global]
cf issues process
cf issues status

# Repos
cf repos health
```

**Technical Achievements:**
- SQLite database with 3 tables
- Rich TUI dashboard
- Circuit breaker pattern
- External activity detection via GitHub Search API
- Slot-based rate limiting (15 slots, 30-min recharge)

---

### 🚧 Phase 2: CodeFRAME Agent Integration (IN PROGRESS)

**Goal**: Run the CodeFRAME agentic process from CLI - headless or with web-ui

**Priority**: HIGH
**Timeline**: Next 2-4 weeks
**Dependencies**: None

**Key Focus**: This phase integrates with the existing CodeFRAME system ([github.com/frankbria/codeframe](https://github.com/frankbria/codeframe)) to enable:
1. Launching CodeFRAME agents from CLI (headless mode)
2. Optional web-ui launch via CLI flag
3. Project and spec management
4. Session lifecycle management
5. Multi-repo project coordination

#### New Entities

**1. projects** - Multi-Repo Project Grouping

Projects group one or more repositories under a single logical unit.

**Commands:**
```bash
cf projects create PROJECT_NAME [--repos REPOS]
  # Creates new project
  # Options:
  #   --repos: Comma-separated list (e.g., "owner/backend,owner/frontend")
  #   --description: Project description
  # Example:
  #   cf projects create gregory-taylor-photography \
  #     --repos "frankbria/gregory-taylor-backend,frankbria/gregory-taylor-frontend"

cf projects list
  # Lists all projects
  # Output:
  #   - Project name
  #   - Repositories (count)
  #   - Active sessions
  #   - Last activity

cf projects view PROJECT_NAME
  # Shows project details
  # Output:
  #   - Associated repos
  #   - Open issues across repos
  #   - Active PRs
  #   - Recent deployments
  #   - Project specs (if any)

cf projects add-repo PROJECT_NAME REPO
  # Adds repo to existing project

cf projects remove-repo PROJECT_NAME REPO
  # Removes repo from project

cf projects delete PROJECT_NAME [--force]
  # Deletes project (not repos)
  # Options:
  #   --force: Skip confirmation
```

**Technical Specs:**
- **Database Tables**:
  - `projects`: project_id, name, description, created_at
  - `project_repos`: Links projects to repos (many-to-many)

**2. specs** - Project Specifications Management

Manages PRD, technical specs, and other project documentation.

**Commands:**
```bash
cf specs create PROJECT_NAME --type TYPE
  # Creates new spec for project
  # Types:
  #   prd: Product Requirements Document
  #   technical: Technical Specification
  #   api: API Documentation
  #   architecture: Architecture Design Doc
  # Opens editor for spec content (EDITOR environment variable)
  # Or use --from-file to import existing doc

cf specs list [PROJECT_NAME]
  # Lists specs
  # Without PROJECT_NAME: all specs across projects
  # Output:
  #   - Spec type
  #   - Last updated
  #   - Status (draft|approved|implemented)

cf specs view SPEC_ID
  # Shows spec content
  # Renders markdown if applicable

cf specs edit SPEC_ID
  # Opens spec in editor

cf specs approve SPEC_ID
  # Marks spec as approved
  # Enables automatic issue generation from spec

cf specs generate-issues SPEC_ID
  # Generates GitHub issues from approved spec
  # Uses AI to break down spec into actionable tasks
  # Links issues to project

cf specs status SPEC_ID
  # Shows implementation status
  # Output:
  #   - Generated issues (open/closed)
  #   - Implementation progress
  #   - Linked PRs
```

**Technical Specs:**
- **Database Tables**:
  - `specs`: spec_id, project_id, type, content, status, created_at, approved_at
  - `spec_issues`: Links specs to generated issues

- **Integration**:
  - AI-powered spec → issues breakdown
  - Markdown rendering for display
  - Git storage for version control (optional)

**3. sessions** - CodeFRAME Session Management

Integration with CodeFRAME session lifecycle (`codeframe/core/session.py`).

**Commands:**
```bash
cf sessions start [--project PROJECT] [--issue ISSUE] [--ui]
  # Starts new CodeFRAME development session
  # Options:
  #   --project: Project name (required if --issue not provided)
  #   --issue: Issue number to work on
  #   --ui: Launch web-ui dashboard (default: headless)
  #   --model: LLM model (sonnet-4.5|opus-4|haiku-4)
  # Actions:
  #   - Creates session in CodeFRAME core
  #   - Initializes context (HOT/WARM/COLD memory)
  #   - Optionally opens web-ui at http://localhost:8000
  # Returns: session_id

cf sessions status [SESSION_ID]
  # Shows session status
  # Without SESSION_ID: all active sessions
  # Output:
  #   - Session state (active|paused|completed)
  #   - Current task
  #   - Active agents
  #   - Blockers
  #   - Time elapsed
  #   - Cost to date

cf sessions ui SESSION_ID
  # Opens web-ui for existing session
  # Launches browser at http://localhost:8000/session/SESSION_ID

cf sessions pause SESSION_ID
  # Pauses session (graceful)

cf sessions resume SESSION_ID [--ui]
  # Resumes paused session
  # Options:
  #   --ui: Launch web-ui

cf sessions end SESSION_ID [--save]
  # Ends session gracefully
  # Options:
  #   --save: Create checkpoint before ending

cf sessions list [--project PROJECT] [--status STATUS]
  # Lists sessions
  # Options:
  #   --project: Filter by project
  #   --status: Filter (active|paused|completed)
```

**Technical Specs:**
- **Database Tables**:
  - `sessions`: session_id, project_id, issue_id, status, started_at, ended_at
  - `session_context`: Context snapshots (HOT/WARM/COLD memory)

- **Integration**:
  - CodeFRAME session manager (REST API + WebSocket)
  - Web-ui launcher (subprocess management)
  - Shared SQLite database

**4. agents** - CodeFRAME Agent Lifecycle Management

Integration with main CodeFRAME system ([github.com/frankbria/codeframe](https://github.com/frankbria/codeframe)).

**Commands:**
```bash
cf agents launch ISSUE_NUMBER [--project PROJECT] [--ui]
  # Launches CodeFRAME lead agent on an issue
  # Options:
  #   --project: Project name (default: infer from issue)
  #   --ui: Launch web-ui dashboard
  #   --model: LLM model (sonnet-4.5|opus-4|haiku-4)
  #   --detach: Run in background (default: yes if not --ui)
  # Actions:
  #   - Creates CodeFRAME session
  #   - Launches lead agent
  #   - Optionally opens web-ui
  # Returns: session_id for tracking

cf agents status [SESSION_ID]
  # Shows agent execution status
  # Without SESSION_ID: shows all active sessions
  # Output:
  #   - Current task
  #   - Active workers (backend, frontend, test, review)
  #   - Blockers awaiting human input
  #   - Time elapsed, estimated completion
  #   - Current costs

cf agents logs SESSION_ID [--follow]
  # Streams agent logs
  # Options:
  #   --follow: Tail mode (like docker logs -f)
  #   --since: Time filter
  #   --worker: Filter by worker (backend|frontend|test|review)

cf agents pause SESSION_ID
  # Pauses agent execution (graceful)
  # Waits for current task to finish

cf agents resume SESSION_ID
  # Resumes paused session

cf agents stop SESSION_ID [--force]
  # Stops agent execution
  # Options:
  #   --force: Immediate termination (vs graceful)

cf agents cost [SESSION_ID]
  # Shows cost breakdown
  # Without SESSION_ID: aggregated view
  # Output:
  #   - Per-model costs (Sonnet/Opus/Haiku)
  #   - Per-worker costs
  #   - Time-based trends

cf agents list [--status STATUS]
  # Lists all sessions
  # Options:
  #   --status: Filter (active|paused|completed|failed)
  #   --since: Time filter
  #   --repo: Repo filter
```

**Technical Specs:**
- **Database Tables**:
  - `agent_sessions`: session_id, issue_number, repo, status, started_at, completed_at
  - `agent_tasks`: task_id, session_id, worker, status, output
  - `agent_blockers`: blocker_id, session_id, question, resolved_at, resolution
  - `agent_costs`: cost_id, session_id, model, tokens, cost, timestamp

- **Integration**:
  - WebSocket connection to CodeFRAME dashboard (port 8000)
  - REST API for launching/controlling agents
  - SQLite shared between CLI and CodeFRAME core
  - Notification system (desktop notifications for blockers)

- **State Management**:
  - Detect running CodeFRAME instances
  - Handle session recovery after CLI restart
  - Sync status from CodeFRAME database

**2. prs** - Pull Request Coordination

**Commands:**
```bash
cf prs create [ISSUE_NUMBER] [--draft]
  # Creates PR from agent work or current branch
  # Options:
  #   ISSUE_NUMBER: Link to issue (auto-detects if on agent branch)
  #   --draft: Create as draft PR
  #   --auto-merge: Enable auto-merge on approval
  # Triggers:
  #   - Runs quality gates (tests, coverage, review)
  #   - Creates PR description from issue + commits
  #   - Links to original issue

cf prs review PR_NUMBER [--request REVIEWER]
  # Initiates code review process
  # Options:
  #   --request: Request review from user
  #   --auto: Use AI reviewer (CodeFRAME review agent)
  # Actions:
  #   - Runs automated security scan
  #   - OWASP pattern detection
  #   - Complexity analysis
  #   - Generates review comments

cf prs status [PR_NUMBER]
  # Shows PR status
  # Without PR_NUMBER: all open PRs across repos
  # Output:
  #   - Review status (approved/changes-requested/pending)
  #   - CI/CD status
  #   - Quality gate results
  #   - Merge conflicts

cf prs merge PR_NUMBER [--squash|--rebase]
  # Merges PR
  # Options:
  #   --squash: Squash commits
  #   --rebase: Rebase and merge
  #   --delete-branch: Delete branch after merge (default: yes)
  # Validation:
  #   - All quality gates passed
  #   - Required approvals received
  #   - No merge conflicts

cf prs list [--status STATUS] [--author AUTHOR]
  # Lists PRs across repos
  # Options:
  #   --status: Filter (open|draft|merged|closed)
  #   --author: Filter by author
  #   --repo: Repo filter
  #   --label: Label filter
```

**Technical Specs:**
- **Database Tables**:
  - `pull_requests`: pr_id, number, repo, issue_id, status, created_at, merged_at
  - `pr_reviews`: review_id, pr_id, reviewer, status, comments
  - `pr_quality_gates`: gate_id, pr_id, gate_type, status, details

- **Integration**:
  - GitHub API via PyGithub
  - CodeFRAME review agent for automated review
  - Quality gate system from main CodeFRAME

**3. Enhanced repos** - Extended Repository Management

**New Commands:**
```bash
cf repos status [--global]
  # Cross-repo status dashboard
  # Shows:
  #   - Open issues by repo
  #   - Active PRs by repo
  #   - Agent sessions by repo
  #   - Recent deployments
  #   - Health indicators

cf repos init REPO_NAME [--template TEMPLATE]
  # Scaffolds new repository
  # Options:
  #   --template: Project template (fastapi|nextjs|monorepo|python-lib)
  #   --private: Create as private repo
  # Actions:
  #   - Creates GitHub repo
  #   - Clones template
  #   - Initializes CI/CD
  #   - Sets up branch protection

cf repos sync [--repo REPO]
  # Syncs repo state to database
  # Updates:
  #   - Issues cache
  #   - PR status
  #   - Branch info
  #   - Latest commits

cf repos audit [--security] [--performance]
  # Runs repo audits
  # Options:
  #   --security: Security vulnerability scan
  #   --performance: Performance analysis
  #   --dependencies: Dependency audit
```

**Technical Specs:**
- **Database Tables**:
  - `repositories`: repo_id, name, url, default_branch, last_sync
  - `repo_stats`: stat_id, repo_id, metric, value, timestamp

**4. Enhanced issues** - State Tracking

**New Commands:**
```bash
cf issues track ISSUE_NUMBER
  # Shows issue lifecycle tracking
  # States: planning → building → reviewing → deployed
  # Output:
  #   - Current state
  #   - Linked agent session (if building)
  #   - Linked PR (if reviewing)
  #   - Deployment info (if deployed)
  #   - Timeline of state transitions

cf issues assign ISSUE_NUMBER --agent
  # Assigns issue to CodeFRAME agent
  # Equivalent to: cf agents launch ISSUE_NUMBER
  # Sets issue state: planning → building

cf issues close ISSUE_NUMBER [--reason REASON]
  # Closes issue with tracking
  # Options:
  #   --reason: Closure reason (completed|wontfix|duplicate)
  # Updates state tracking
```

**Technical Specs:**
- **Database Tables**:
  - `issue_states`: state_id, issue_number, repo, state, transitioned_at
  - `issue_sessions`: Links issues to agent sessions
  - `issue_prs`: Links issues to PRs

#### Phase 2 Success Metrics

**Project & Spec Management:**
- [ ] Create multi-repo project in <2 seconds
- [ ] Generate issues from spec in <10 seconds (for typical PRD)
- [ ] View project dashboard with 5 repos in <2 seconds

**CodeFRAME Integration:**
- [ ] Launch CodeFRAME session from CLI in <5 seconds
- [ ] Web-ui launch time <3 seconds (browser open + dashboard ready)
- [ ] Agent status updates with <1 second latency (via WebSocket)
- [ ] Session pause/resume roundtrip <2 seconds

**Headless Mode:**
- [ ] CLI successfully connects to headless CodeFRAME session
- [ ] Blocker notifications delivered <1 second after agent raises blocker
- [ ] Cost tracking accurate to 100% (every LLM call tracked)

**Cross-Repo Coordination:**
- [ ] Multi-repo project view rendering <3 seconds for 5 repos
- [ ] Issue state tracking across project (planning→building→reviewing)

---

### 📋 Phase 3: Production Workflow (PLANNED)

**Goal**: Enable full production deployment workflow with quality assurance

**Priority**: MEDIUM
**Timeline**: 4-6 weeks after Phase 2
**Dependencies**: Phase 2 complete

#### New Entities

**1. sessions** - Development Session Management

Integration with CodeFRAME session lifecycle (`codeframe/core/session.py`).

**Commands:**
```bash
cf sessions start [--issue ISSUE] [--resume SESSION_ID]
  # Starts new development session or resumes existing
  # Options:
  #   --issue: Link to issue
  #   --resume: Resume previous session
  # Actions:
  #   - Creates session in CodeFRAME
  #   - Initializes context (HOT/WARM/COLD memory)
  #   - Auto-detects current work

cf sessions status [SESSION_ID]
  # Shows current session status
  # Output:
  #   - Active agents
  #   - Current tasks
  #   - Blockers
  #   - Time elapsed
  #   - Cost to date

cf sessions save [SESSION_ID] [--name NAME]
  # Manually saves session state
  # Options:
  #   --name: Descriptive name for save point
  # Creates checkpoint (see checkpoints entity)

cf sessions end [SESSION_ID]
  # Gracefully ends session
  # Actions:
  #   - Completes pending tasks
  #   - Saves final state
  #   - Generates session summary
  #   - Prompts for checkpoint creation

cf sessions list [--active]
  # Lists sessions
  # Options:
  #   --active: Only active sessions
  #   --repo: Filter by repo
  #   --since: Time filter
```

**2. checkpoints** - Project State Snapshots

Integration with CodeFRAME checkpoint system (`codeframe/core/checkpoints.py`).

**Commands:**
```bash
cf checkpoints create NAME [--description DESC]
  # Creates project checkpoint
  # Format: Git commit + SQLite backup + context JSON
  # Options:
  #   --description: Checkpoint description
  # Returns: checkpoint_id

cf checkpoints list [--since DURATION]
  # Lists checkpoints
  # Output:
  #   - Checkpoint name/ID
  #   - Created timestamp
  #   - Description
  #   - Disk size

cf checkpoints restore CHECKPOINT_ID [--preview]
  # Restores project to checkpoint
  # Options:
  #   --preview: Show diff without applying
  # Actions:
  #   - Shows file changes
  #   - Prompts for confirmation
  #   - Restores git + database + context

cf checkpoints diff CHECKPOINT_ID_1 CHECKPOINT_ID_2
  # Shows differences between checkpoints
  # Output:
  #   - File changes
  #   - Database changes
  #   - Context differences

cf checkpoints delete CHECKPOINT_ID [--force]
  # Deletes checkpoint
  # Options:
  #   --force: Skip confirmation
```

**3. reviews** - Code Review Orchestration

**Commands:**
```bash
cf reviews start PR_NUMBER [--auto|--request REVIEWER]
  # Initiates comprehensive code review
  # Options:
  #   --auto: Use AI reviewer (CodeFRAME review agent)
  #   --request: Request human reviewer
  # Stages:
  #   1. Security scan (OWASP patterns)
  #   2. Complexity analysis
  #   3. Test coverage check
  #   4. Style/lint validation
  #   5. Architecture review

cf reviews status PR_NUMBER
  # Shows review progress
  # Output:
  #   - Review stage (security → complexity → coverage → style → arch)
  #   - Issues found
  #   - Approval status

cf reviews approve PR_NUMBER [--comment COMMENT]
  # Approves review
  # Options:
  #   --comment: Approval comment

cf reviews request-changes PR_NUMBER --reason REASON
  # Requests changes
  # Options:
  #   --reason: Required changes description
```

#### Phase 3 Technical Specs

**Database Schema Additions:**
- `dev_sessions`: Full session lifecycle tracking
- `checkpoints`: Checkpoint metadata and paths
- `review_runs`: Code review executions
- `review_findings`: Issues found during review

**Integration Points:**
- CodeFRAME session manager (WebSocket + REST)
- CodeFRAME checkpoint system (file system + SQLite)
- CodeFRAME review agent (async task queue)

---

### 📋 Phase 4: Deployment & Monitoring (PLANNED)

**Goal**: Production deployment control and observability

**Priority**: MEDIUM
**Timeline**: 4-6 weeks after Phase 3
**Dependencies**: Phase 3 complete

#### New Entities

**1. environments** - Environment Configuration

Manages test, staging, and production environments. Users can configure which environments to use (some projects may skip test, others may have all three).

**Commands:**
```bash
cf environments list [--project PROJECT]
  # Lists configured environments
  # Output:
  #   - Environment name (test|staging|production)
  #   - Platform (vercel|railway|vps|local)
  #   - URL
  #   - Last deployment
  #   - Health status

cf environments create ENV_NAME --project PROJECT --platform PLATFORM
  # Creates environment configuration
  # Options:
  #   ENV_NAME: test|staging|production
  #   --platform: vercel|railway|vps|local
  #   --url: Environment URL
  #   --api-key: Platform API key (encrypted storage)
  #   --skip-in-pipeline: Don't use in automated deployments
  # Example:
  #   cf environments create staging \
  #     --project gregory-taylor-photography \
  #     --platform vercel \
  #     --url https://gregory-taylor-staging.vercel.app

cf environments update ENV_NAME --project PROJECT [OPTIONS]
  # Updates environment config
  # Options: Same as create

cf environments delete ENV_NAME --project PROJECT
  # Deletes environment config (not the actual environment)

cf environments health ENV_NAME --project PROJECT
  # Shows environment health
  # Output:
  #   - Service status
  #   - Error rates
  #   - Response times
  #   - Last health check
```

**Technical Specs:**
- **Database Tables**:
  - `environments`: env_id, project_id, name, platform, url, api_key_encrypted, skip_in_pipeline
  - `environment_health`: health_id, env_id, metric, value, timestamp

**2. deployments** - Deployment Tracking & Control

Handles deployments through test → staging → prod pipeline.

**Commands:**
```bash
cf deployments deploy PR_NUMBER [--env ENV] [--auto-rollback] [--skip-envs ENVS]
  # Deploys PR to environment (or through pipeline)
  # Options:
  #   --env: Target environment (test|staging|production)
  #          If not specified, deploys through configured pipeline
  #   --auto-rollback: Rollback on failure
  #   --skip-envs: Skip environments (e.g., "test" to go directly to staging)
  # Pipeline behavior:
  #   - Validates quality gates before first deployment
  #   - Deploys to test (if configured)
  #   - Runs smoke tests
  #   - Deploys to staging (if configured)
  #   - Runs integration tests
  #   - Waits for approval (production only)
  #   - Deploys to production
  # Actions:
  #   - Merges PR (on first deployment)
  #   - Triggers deployment
  #   - Monitors health checks
  #   - Notifies on completion or failure
  # Returns: deployment_id

cf deployments status [DEPLOYMENT_ID]
  # Shows deployment status
  # Without DEPLOYMENT_ID: recent deployments across all environments
  # Output:
  #   - Deployment state (pending|deploying|success|failed|rolled-back)
  #   - Environment
  #   - Health check results
  #   - Time elapsed
  #   - Logs link
  #   - Pipeline progress (if multi-env deployment)

cf deployments approve DEPLOYMENT_ID
  # Approves deployment to next environment
  # Typically used for production deployments
  # Continues pipeline if deployment was paused for approval

cf deployments rollback DEPLOYMENT_ID [--to PREVIOUS_DEPLOYMENT_ID]
  # Rolls back deployment
  # Options:
  #   --to: Specific deployment to rollback to (default: previous)
  # Actions:
  #   - Reverts to previous version
  #   - Monitors rollback health
  #   - Notifies on completion

cf deployments logs DEPLOYMENT_ID [--follow] [--tail N]
  # Shows deployment logs
  # Options:
  #   --follow: Tail mode
  #   --tail: Last N lines (default: 100)

cf deployments health [--env ENV] [--project PROJECT]
  # Shows environment health across projects
  # Options:
  #   --env: Filter environment
  #   --project: Filter project
  # Output:
  #   - Service status per environment
  #   - Error rates
  #   - Response times
  #   - Recent deployments

cf deployments pipeline PROJECT_NAME
  # Shows deployment pipeline for project
  # Output:
  #   - Configured environments (test → staging → prod)
  #   - Current deployments per environment
  #   - Last successful deployment
  #   - Pending approvals

cf deployments list [--env ENV] [--status STATUS] [--project PROJECT]
  # Lists deployments
  # Options:
  #   --env: Filter environment
  #   --status: Filter status
  #   --project: Filter project
  #   --since: Time filter
```

**Technical Specs:**
- **Database Tables**:
  - `deployments`: deployment_id, pr_id, env_id, status, started_at, completed_at, approved_by, approved_at
  - `deployment_pipeline`: Links deployments in multi-env pipeline
  - `deployment_health`: health_id, deployment_id, metric, value, timestamp
  - `deployment_logs`: log_id, deployment_id, timestamp, level, message
  - `deployment_approvals`: approval_id, deployment_id, approver, approved_at

- **Integration**:
  - Platform-specific clients (Vercel, Railway, VPS)
  - Health check endpoints
  - Log aggregation services
  - Notification system (for approval requests)

- **Pipeline Flow**:
  ```
  PR Merged → Deploy Test → Smoke Tests → Deploy Staging →
  Integration Tests → [Manual Approval] → Deploy Production →
  Monitor Health
  ```

**2. metrics** - Analytics & Cost Tracking

Integration with CodeFRAME metrics system (`codeframe/core/metrics.py`).

**Commands:**
```bash
cf metrics view [--since DURATION] [--format FORMAT]
  # Shows metrics dashboard
  # Options:
  #   --since: Time range (1h|24h|7d|30d)
  #   --format: Output format (table|json|chart)
  # Metrics:
  #   - Total cost
  #   - Per-model breakdown
  #   - Per-agent breakdown
  #   - Token usage trends

cf metrics cost [--breakdown-by DIMENSION]
  # Cost analytics
  # Options:
  #   --breakdown-by: Group by (agent|model|repo|day|week)
  # Output:
  #   - Total cost
  #   - Cost by dimension
  #   - Trends

cf metrics performance [--repo REPO]
  # Performance metrics
  # Options:
  #   --repo: Filter by repo
  # Output:
  #   - Average task completion time
  #   - Test pass rates
  #   - Build times
  #   - Deployment frequency

cf metrics export [--since DURATION] [--format FORMAT]
  # Exports metrics
  # Options:
  #   --since: Time range
  #   --format: Export format (csv|json|xlsx)
  # Output: File path

cf metrics budget set AMOUNT [--period PERIOD]
  # Sets cost budget
  # Options:
  #   --period: Budget period (daily|weekly|monthly)
  # Actions:
  #   - Sets budget alert threshold
  #   - Enables notifications

cf metrics budget status
  # Shows budget status
  # Output:
  #   - Current spend vs budget
  #   - Remaining budget
  #   - Projected overage
```

**Technical Specs:**
- **Database Tables**:
  - `metrics_snapshots`: snapshot_id, metric_type, value, timestamp
  - `cost_budget`: budget_id, amount, period, alerts_enabled
  - `cost_alerts`: alert_id, threshold_exceeded, notified_at

#### Phase 4 Technical Challenges

- Multi-platform deployment abstraction
- Real-time log streaming
- Cost attribution across distributed systems
- Health check aggregation

---

### 🔮 Phase 5: Advanced Features (FUTURE)

**Goal**: Enhanced developer experience and workflow customization

**Priority**: LOW
**Timeline**: TBD
**Dependencies**: Phase 4 complete

#### Potential Entities

**1. workflows** - Custom Automation Pipelines

**Concept:**
```bash
cf workflows create NAME --from-file workflow.yaml
  # Creates custom workflow
  # Example workflow.yaml:
  #   triggers:
  #     - issue_labeled: "urgent"
  #   actions:
  #     - agents.launch
  #     - prs.create
  #     - deployments.deploy --env staging

cf workflows run WORKFLOW_NAME [--trigger-data JSON]
  # Manually runs workflow

cf workflows list
  # Lists workflows

cf workflows enable|disable WORKFLOW_NAME
  # Enables/disables workflow
```

**2. ideas** - AI-Powered Idea Generation

**Concept:**
```bash
cf ideas generate [--topic TOPIC] [--count N]
  # Generates feature ideas using AI
  # Options:
  #   --topic: Focus area (authentication|payments|analytics)
  #   --count: Number of ideas to generate
  # Output:
  #   - Ranked list of ideas
  #   - Feasibility scores
  #   - Effort estimates

cf ideas refine IDEA_ID
  # Refines idea with more details
  # Interactive session to flesh out:
  #   - User stories
  #   - Technical requirements
  #   - Architecture considerations

cf ideas convert IDEA_ID
  # Converts idea to GitHub issues
  # Creates:
  #   - Main feature issue
  #   - Sub-task issues
  #   - Technical design doc
```

**3. teams** - Collaboration & Permissions

**Concept:**
```bash
cf teams create TEAM_NAME
  # Creates team

cf teams add-member TEAM_NAME USERNAME
  # Adds member to team

cf teams permissions set TEAM_NAME --repos "pattern" --access LEVEL
  # Sets team permissions
  # Access levels: read|write|admin
```

---

## Technical Specifications

### Database Architecture

**Database Strategy:**
- **Current**: SQLite for simplicity, portability, and zero-dependency deployment
- **Future (Phase 5+)**: Optional PostgreSQL support for multi-user scenarios and complex queries
- **Migration Path**: Abstract database interface allows swapping backends without code changes

**Current (Phase 1):**
```sql
-- Traycer queue management
CREATE TABLE queued_issues (
  repo_name TEXT,
  issue_number INTEGER,
  rate_limit_seconds INTEGER,
  next_retry_at TIMESTAMP,
  retry_count INTEGER,
  PRIMARY KEY (repo_name, issue_number)
);

CREATE TABLE processing_history (
  id INTEGER PRIMARY KEY,
  repo_name TEXT,
  issue_number INTEGER,
  processed_at TIMESTAMP,
  status TEXT
);

CREATE TABLE error_log (
  id INTEGER PRIMARY KEY,
  timestamp TIMESTAMP,
  error_type TEXT,
  message TEXT
);
```

**Phase 2 Additions:**
```sql
-- Project management
CREATE TABLE projects (
  project_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_repos (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,
  repo_name TEXT,
  FOREIGN KEY (project_id) REFERENCES projects(project_id),
  UNIQUE(project_id, repo_name)
);

-- Spec management
CREATE TABLE specs (
  spec_id INTEGER PRIMARY KEY,
  project_id INTEGER,
  type TEXT CHECK (type IN ('prd', 'technical', 'api', 'architecture')),
  content TEXT,
  status TEXT CHECK (status IN ('draft', 'approved', 'implemented')) DEFAULT 'draft',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  approved_at TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE spec_issues (
  id INTEGER PRIMARY KEY,
  spec_id INTEGER,
  issue_number INTEGER,
  repo_name TEXT,
  FOREIGN KEY (spec_id) REFERENCES specs(spec_id)
);

-- Session management (CodeFRAME integration)
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  project_id INTEGER,
  issue_id INTEGER,
  status TEXT CHECK (status IN ('active', 'paused', 'completed', 'failed')),
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ended_at TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE session_context (
  context_id INTEGER PRIMARY KEY,
  session_id TEXT,
  tier TEXT CHECK (tier IN ('HOT', 'WARM', 'COLD')),
  content TEXT,
  snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Agent management
CREATE TABLE agent_sessions (
  session_id TEXT PRIMARY KEY,
  issue_number INTEGER,
  repo TEXT,
  project_id INTEGER,
  status TEXT CHECK (status IN ('active', 'paused', 'completed', 'failed')),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  model TEXT,
  total_cost REAL,
  FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE agent_tasks (
  task_id TEXT PRIMARY KEY,
  session_id TEXT,
  worker TEXT CHECK (worker IN ('lead', 'backend', 'frontend', 'test', 'review')),
  description TEXT,
  status TEXT,
  output TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
);

CREATE TABLE agent_blockers (
  blocker_id TEXT PRIMARY KEY,
  session_id TEXT,
  question TEXT,
  created_at TIMESTAMP,
  resolved_at TIMESTAMP,
  resolution TEXT,
  FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
);

CREATE TABLE agent_costs (
  cost_id INTEGER PRIMARY KEY,
  session_id TEXT,
  model TEXT,
  input_tokens INTEGER,
  output_tokens INTEGER,
  cost REAL,
  timestamp TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
);

-- PR management
CREATE TABLE pull_requests (
  pr_id INTEGER PRIMARY KEY,
  number INTEGER,
  repo TEXT,
  issue_id INTEGER,
  status TEXT CHECK (status IN ('open', 'draft', 'merged', 'closed')),
  created_at TIMESTAMP,
  merged_at TIMESTAMP
);

CREATE TABLE pr_reviews (
  review_id INTEGER PRIMARY KEY,
  pr_id INTEGER,
  reviewer TEXT,
  status TEXT CHECK (status IN ('pending', 'approved', 'changes_requested')),
  comments TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (pr_id) REFERENCES pull_requests(pr_id)
);

CREATE TABLE pr_quality_gates (
  gate_id INTEGER PRIMARY KEY,
  pr_id INTEGER,
  gate_type TEXT CHECK (gate_type IN ('tests', 'coverage', 'types', 'review', 'security')),
  status TEXT CHECK (status IN ('pending', 'passed', 'failed')),
  details TEXT,
  run_at TIMESTAMP,
  FOREIGN KEY (pr_id) REFERENCES pull_requests(pr_id)
);

-- Issue state tracking
CREATE TABLE issue_states (
  state_id INTEGER PRIMARY KEY,
  issue_number INTEGER,
  repo TEXT,
  state TEXT CHECK (state IN ('planning', 'building', 'reviewing', 'deployed')),
  transitioned_at TIMESTAMP
);

-- Repository tracking
CREATE TABLE repositories (
  repo_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  url TEXT,
  default_branch TEXT,
  last_sync TIMESTAMP
);
```

**Phase 3-5 Additions:** (See detailed specs in phase sections)

### API Integration Patterns

**Current Integrations:**
- GitHub API (PyGithub) - Issues, PRs, repos
- GitHub Search API (gh CLI) - External activity detection

**Planned Integrations:**

**CodeFRAME Core:**
```python
# WebSocket connection for real-time updates
import websockets

async def connect_codeframe():
    uri = "ws://localhost:8000/ws/sessions"
    async with websockets.connect(uri) as ws:
        # Subscribe to session updates
        await ws.send(json.dumps({
            "action": "subscribe",
            "session_id": session_id
        }))
        # Receive updates
        async for message in ws:
            update = json.loads(message)
            # Process update

# REST API for control
import httpx

async def launch_agent(issue_number, repo):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/agents/launch",
            json={
                "issue_number": issue_number,
                "repo": repo,
                "model": "sonnet-4.5"
            }
        )
        return response.json()["session_id"]
```

**Deployment Platforms:**
```python
# Abstract deployment interface
class DeploymentProvider(ABC):
    @abstractmethod
    async def deploy(self, repo, branch, env):
        pass

    @abstractmethod
    async def get_status(self, deployment_id):
        pass

    @abstractmethod
    async def rollback(self, deployment_id):
        pass

# Implementations
class VercelProvider(DeploymentProvider):
    # Vercel API integration
    pass

class RailwayProvider(DeploymentProvider):
    # Railway API integration
    pass

class VPSProvider(DeploymentProvider):
    # SSH + systemd integration
    pass
```

### CLI Framework Enhancements

**Current:** argparse + Rich for TUI

**Planned Enhancements:**

**1. Output Format Standardization**
```python
# All commands support standard output formats
@output_formatter
def command_handler(args):
    data = fetch_data()
    return data  # Auto-formatted based on --format flag

# Usage:
cf agents status --format json    # Machine-readable
cf agents status --format table   # Human-readable (default)
cf agents status --format yaml    # Config-friendly
```

**2. Interactive TUI Components**
```python
# Rich-based interactive components
from rich.prompt import Prompt, Confirm
from rich.progress import Progress

# Confirmation prompts
if Confirm.ask("Launch agent on this issue?"):
    launch_agent()

# Progress tracking
with Progress() as progress:
    task = progress.add_task("Deploying...", total=100)
    # Update progress
```

**3. Plugin System**
```python
# Allow third-party commands
class Plugin(ABC):
    @property
    def name(self) -> str:
        pass

    def setup_parser(self, subparsers):
        pass

# Example plugin
class CustomDeployPlugin(Plugin):
    name = "custom-deploy"

    def setup_parser(self, subparsers):
        parser = subparsers.add_parser("custom-deploy")
        # Add custom commands
```

---

## Integration Points

### CodeFRAME Core Integration

**Connection Methods:**
1. **WebSocket** - Real-time updates (agent status, blockers, costs)
2. **REST API** - Control operations (launch, pause, stop)
3. **Shared SQLite** - State synchronization
4. **File System** - Checkpoints, logs

**Discovery:**
```python
def discover_codeframe_instance():
    """Auto-discovers running CodeFRAME instance."""
    # 1. Check for WebSocket on localhost:8000
    # 2. Check for PID file in ~/.codeframe/
    # 3. Check for active sessions in database
    pass
```

**Health Checks:**
```python
async def check_codeframe_health():
    """Verifies CodeFRAME core is healthy."""
    # 1. WebSocket ping/pong
    # 2. REST API health endpoint
    # 3. Database connectivity
    # 4. File system access
    pass
```

### GitHub Integration

**Current:**
- PyGithub for Issues API
- gh CLI for Search API

**Enhancements:**
- GitHub Checks API for quality gates
- GitHub Deployments API for deployment tracking
- GitHub Packages for artifact management

### Notification System

**Channels:**
- Desktop notifications (via notify-send on Linux)
- Webhooks (POST to custom endpoints)
- Email (via SMTP)
- Slack/Discord (via webhooks)

**Configuration:**
```yaml
# ~/.config/codeframe-cli/notifications.yaml
notifications:
  blockers:
    - desktop
    - webhook: https://example.com/blockers

  deployments:
    - email: frank@codeframe.ai
    - slack: https://hooks.slack.com/...

  costs:
    threshold: 10.00  # Alert when session cost exceeds $10
    channels:
      - desktop
      - email
```

---

## Future Vision

### The Autonomous Development Loop

```
1. IDEATION
   cf ideas generate --topic "user-authentication"
   cf ideas refine idea-123
   cf ideas convert idea-123
   → Creates GitHub issues

2. PLANNING
   cf issues create-plan --global
   cf issues view --live
   → Traycer AI generates plans

3. BUILDING
   cf agents launch issue-456
   cf agents status --follow
   → CodeFRAME agents implement features
   → CLI notifies on blockers
   → Human answers questions
   → Agents continue

4. REVIEWING
   cf prs create issue-456
   cf reviews start pr-789 --auto
   → AI code review
   → Quality gates
   → Human approval if needed

5. DEPLOYING
   cf deployments deploy pr-789 --env staging
   cf deployments health --env staging
   → Monitors health
   cf deployments deploy pr-789 --env production
   → Production deployment

6. MONITORING
   cf metrics view --since 24h
   cf metrics cost --breakdown-by agent
   → Cost tracking
   → Performance monitoring

7. REPEAT
   Loop back to step 1
```

### Vision: Fully Autonomous Workflow

```bash
# Single command to go from idea to production
cf autopilot run \
  --idea "Add OAuth login" \
  --deploy-after-review \
  --budget 50.00

# What happens:
# 1. Generates detailed idea with AI
# 2. Converts to GitHub issues
# 3. Launches agents on issues
# 4. Creates PRs when agents complete
# 5. Runs automated review
# 6. Deploys to staging
# 7. Runs smoke tests
# 8. Deploys to production
# 9. Monitors health
# 10. Notifies on completion or blockers

# All while respecting $50 budget
# All while asking for human input when truly needed
```

---

## Success Metrics

### Phase 2 Targets
- Agent launch latency: <5s
- Status update latency: <1s
- PR creation time: <2min (including quality gates)
- Cross-repo dashboard: <3s for 20 repos
- Cost tracking accuracy: 100% (every LLM call tracked)

### Phase 3 Targets
- Session save/restore: <10s
- Checkpoint creation: <10s
- Checkpoint restore: <30s
- Code review execution: <5min
- Review finding accuracy: >90% (vs human review)

### Phase 4 Targets
- Deployment time: <5min (staging), <10min (production)
- Rollback time: <2min
- Health check latency: <500ms
- Metrics dashboard load: <1s
- Cost report generation: <2s

### Ultimate Success Criteria
- **Time to Production**: Idea → deployed feature in <8 hours (unattended)
- **Human Intervention**: <3 blocker questions per feature
- **Quality**: 100% test pass rate, >85% coverage, zero critical security issues
- **Cost Efficiency**: <$20 per feature (averaged)
- **Developer Satisfaction**: "I check in like a coworker, not a supervisor"

---

## Contributing to the Roadmap

This roadmap is a living document. Contributions welcome!

**How to propose changes:**
1. Create issue in codeframe-cli repo
2. Tag with `roadmap` label
3. Describe:
   - New entity or command
   - Use case / problem it solves
   - Integration requirements
   - Success metrics

**Prioritization criteria:**
- **Impact**: How many users benefit?
- **Effort**: Development complexity
- **Dependencies**: Blocks other features?
- **Risk**: Technical or product risk
- **Alignment**: Fits autonomous development vision?

---

**Last Updated**: 2026-01-01
**Maintainer**: Frank Bria (frank@codeframe.ai)
**Status**: Living Document - Updated Quarterly
