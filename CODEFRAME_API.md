# CodeFRAME API Reference

Comprehensive API documentation for the CodeFRAME backend API.

**Base URL**: `http://localhost:8000` (development)

**Authentication**: All endpoints require authentication via session token (except WebSocket which accepts token as query parameter).

---

## Table of Contents

- [REST API Endpoints](#rest-api-endpoints)
  - [Projects](#projects)
  - [Tasks](#tasks)
  - [Agents](#agents)
  - [Blockers](#blockers)
  - [Chat](#chat)
  - [Discovery](#discovery)
  - [Checkpoints](#checkpoints)
- [WebSocket API](#websocket-api)
  - [Connection](#connection)
  - [Client Messages](#client-messages)
  - [Server Messages](#server-messages)

---

## REST API Endpoints

### Projects

#### GET /api/projects
**Purpose**: List all projects accessible to the authenticated user

**Authentication**: Required (current user)

**Request**: None

**Response**: 200 OK
```json
{
  "projects": [
    {
      "id": 1,
      "name": "my-project",
      "description": "Project description",
      "status": "active",
      "phase": "planning",
      "created_at": "2025-01-01T12:00:00Z",
      "workspace_path": "/path/to/workspace",
      "config": {}
    }
  ]
}
```

---

#### POST /api/projects
**Purpose**: Create a new project

**Authentication**: Required (current user)

**Request Body**:
```json
{
  "name": "project-name",
  "description": "Project description",
  "source_type": "git_remote" | "local_path" | "upload" | "empty",
  "source_location": "https://github.com/user/repo.git",
  "source_branch": "main",
  "workspace_name": "custom-workspace-name"
}
```

**Validation**:
- `name`: 1-100 characters, required
- `description`: 1-500 characters, required
- `source_type`: Optional, defaults to "empty"
- `source_location`: Required when source_type is not "empty"
- `source_branch`: Optional, defaults to "main"

**Response**: 201 Created
```json
{
  "id": 1,
  "name": "project-name",
  "status": "init",
  "phase": "discovery",
  "created_at": "2025-01-01T12:00:00Z",
  "config": {}
}
```

**Error Responses**:
- 403 Forbidden: `source_type='local_path'` not available in hosted mode
- 409 Conflict: Project with name already exists
- 500 Internal Server Error: Database or workspace creation failed

---

#### GET /api/projects/{project_id}
**Purpose**: Get project details by ID

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK
```json
{
  "id": 1,
  "name": "project-name",
  "description": "Project description",
  "status": "active",
  "phase": "planning",
  "created_at": "2025-01-01T12:00:00Z",
  "workspace_path": "/path/to/workspace",
  "config": {}
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/projects/{project_id}/status
**Purpose**: Get comprehensive project status including progress metrics

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK
```json
{
  "project_id": 1,
  "name": "project-name",
  "status": "active",
  "phase": "planning",
  "workflow_step": 1,
  "progress": {
    "total_tasks": 10,
    "completed_tasks": 3,
    "in_progress_tasks": 2,
    "pending_tasks": 5,
    "completion_percentage": 30.0
  }
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/projects/{project_id}/tasks
**Purpose**: Get project tasks with filtering and pagination

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Query Parameters**:
- `status`: Optional filter by task status. Valid values: `pending`, `assigned`, `in_progress`, `blocked`, `completed`, `failed`
- `limit`: Maximum tasks to return (1-1000, default: 50)
- `offset`: Tasks to skip for pagination (>=0, default: 0)

**Response**: 200 OK
```json
{
  "tasks": [
    {
      "id": 1,
      "project_id": 1,
      "issue_id": 1,
      "task_number": "1.1.1",
      "parent_issue_number": "1.1",
      "title": "Task title",
      "description": "Task description",
      "status": "in_progress",
      "assigned_to": "agent-123",
      "depends_on": "1.1.0",
      "can_parallelize": false,
      "priority": 2,
      "workflow_step": 3,
      "requires_mcp": false,
      "estimated_tokens": 5000,
      "actual_tokens": 4800,
      "created_at": "2025-01-01T12:00:00Z",
      "completed_at": null
    }
  ],
  "total": 100
}
```

**Error Responses**:
- 400 Bad Request: Invalid status value
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 422 Unprocessable Entity: Invalid parameters

---

#### GET /api/projects/{project_id}/activity
**Purpose**: Get recent activity log for project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Query Parameters**:
- `limit`: Maximum activity items to return (default: 50)

**Response**: 200 OK
```json
{
  "activity": [
    {
      "id": 1,
      "timestamp": "2025-01-01T12:00:00Z",
      "event_type": "task_completed",
      "description": "Task 1.1.1 completed",
      "metadata": {}
    }
  ]
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/projects/{project_id}/prd
**Purpose**: Get Product Requirements Document (PRD) for project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK
```json
{
  "project_id": "1",
  "prd_content": "# Product Requirements...",
  "generated_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T13:00:00Z",
  "status": "available" | "generating" | "not_found"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/projects/{project_id}/issues
**Purpose**: Get issues for a project with optional task inclusion

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Query Parameters**:
- `include`: Optional, set to `tasks` to include tasks for each issue

**Response**: 200 OK
```json
{
  "issues": [
    {
      "id": "1",
      "issue_number": "1.1",
      "title": "Issue title",
      "description": "Issue description",
      "status": "in_progress",
      "priority": 2,
      "depends_on": ["1.0"],
      "proposed_by": "agent" | "human",
      "created_at": "2025-01-01T12:00:00Z",
      "updated_at": "2025-01-01T13:00:00Z",
      "completed_at": null,
      "tasks": []
    }
  ],
  "total_issues": 10,
  "total_tasks": 50,
  "next_cursor": null,
  "prev_cursor": null
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/projects/{project_id}/session
**Purpose**: Get current session state for project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK
```json
{
  "last_session": {
    "summary": "Last session summary",
    "timestamp": "2025-01-01T12:00:00Z"
  },
  "next_actions": ["Action 1", "Action 2"],
  "progress_pct": 45.5,
  "active_blockers": [
    {
      "id": 1,
      "question": "How should we handle edge case X?",
      "blocker_type": "ASYNC"
    }
  ]
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### POST /api/projects/{project_id}/start
**Purpose**: Start Lead Agent for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**: None

**Response**:
- 202 Accepted: Agent starting
  ```json
  {
    "message": "Starting Lead Agent for project 1",
    "status": "starting"
  }
  ```
- 200 OK: Already running
  ```json
  {
    "message": "Project 1 is already running",
    "status": "running"
  }
  ```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: ANTHROPIC_API_KEY not configured

---

#### POST /api/projects/{project_id}/pause
**Purpose**: Pause project execution

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**: None

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Project paused"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### POST /api/projects/{project_id}/resume
**Purpose**: Resume project execution

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**: None

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Project resuming"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

### Tasks

#### POST /api/tasks
**Purpose**: Create a new task

**Authentication**: Required (user must have project access)

**Request Body**:
```json
{
  "project_id": 1,
  "title": "Task title",
  "description": "Task description",
  "priority": 3,
  "status": "pending",
  "workflow_step": 1,
  "depends_on": "1.0.5",
  "requires_mcp": false
}
```

**Validation**:
- `project_id`: Required
- `title`: 1-500 characters, required
- `description`: Optional, defaults to empty string
- `priority`: 0-4, defaults to 3
- `status`: Defaults to "pending"
- `workflow_step`: >= 1, defaults to 1
- `depends_on`: Optional task number
- `requires_mcp`: Boolean, defaults to false

**Response**: 201 Created
```json
{
  "id": 1,
  "project_id": 1,
  "title": "Task title",
  "description": "Task description",
  "status": "pending",
  "priority": 3,
  "workflow_step": 1,
  "depends_on": "1.0.5",
  "requires_mcp": false,
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: Error creating task

---

### Agents

#### GET /api/projects/{project_id}/agents
**Purpose**: Get all agents assigned to a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Query Parameters**:
- `is_active`: Boolean (default: true). If true, only return currently assigned agents

**Response**: 200 OK
```json
[
  {
    "agent_id": "agent-123",
    "type": "lead" | "backend" | "frontend" | "test" | "review",
    "provider": "claude" | "gpt4",
    "maturity_level": "directive" | "coaching" | "supporting" | "delegating",
    "status": "idle" | "working" | "blocked" | "offline",
    "current_task_id": 5,
    "last_heartbeat": "2025-01-01T12:00:00Z",
    "metrics": {
      "task_count": 10,
      "completed_count": 8,
      "completion_rate": 0.8,
      "avg_test_pass_rate": 0.95,
      "self_correction_rate": 0.75,
      "maturity_score": 0.82,
      "last_assessed": "2025-01-01T10:00:00Z"
    },
    "assignment_id": 1,
    "role": "primary_backend",
    "assigned_at": "2025-01-01T09:00:00Z",
    "unassigned_at": null,
    "is_active": true
  }
]
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: Error fetching agents

---

#### POST /api/projects/{project_id}/agents
**Purpose**: Assign an agent to a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**:
```json
{
  "agent_id": "agent-123",
  "role": "primary_backend"
}
```

**Validation**:
- `agent_id`: 1-100 characters, required
- `role`: 1-50 characters, defaults to "worker"

**Response**: 201 Created
```json
{
  "assignment_id": 1,
  "message": "Agent agent-123 assigned to project 1 with role primary_backend"
}
```

**Error Responses**:
- 400 Bad Request: Agent already assigned
- 403 Forbidden: Access denied
- 404 Not Found: Project or agent not found
- 500 Internal Server Error: Error assigning agent

---

#### DELETE /api/projects/{project_id}/agents/{agent_id}
**Purpose**: Remove an agent from a project (soft delete)

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `agent_id`: string

**Request Body**: None

**Response**: 204 No Content

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project or assignment not found
- 500 Internal Server Error: Error removing agent

---

#### PUT /api/projects/{project_id}/agents/{agent_id}/role
**Purpose**: Update an agent's role on a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `agent_id`: string

**Request Body**:
```json
{
  "role": "secondary_backend"
}
```

**Response**: 200 OK
```json
{
  "agent_id": "agent-123",
  "type": "backend",
  "provider": "claude",
  "maturity_level": "supporting",
  "status": "working",
  "current_task_id": 5,
  "last_heartbeat": "2025-01-01T12:00:00Z",
  "metrics": null,
  "assignment_id": 1,
  "role": "secondary_backend",
  "assigned_at": "2025-01-01T09:00:00Z",
  "unassigned_at": null,
  "is_active": true
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project or assignment not found
- 500 Internal Server Error: Error updating role

---

#### PATCH /api/projects/{project_id}/agents/{agent_id}
**Purpose**: Update an agent's role on a project (PATCH variant)

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `agent_id`: string

**Request Body**:
```json
{
  "role": "code_reviewer"
}
```

**Response**: 200 OK
```json
{
  "message": "Agent agent-123 role updated to code_reviewer on project 1"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project or assignment not found
- 422 Unprocessable Entity: Validation error
- 500 Internal Server Error: Error updating role

---

#### GET /api/agents/{agent_id}/projects
**Purpose**: Get all projects an agent is assigned to

**Authentication**: Required

**Path Parameters**:
- `agent_id`: string

**Query Parameters**:
- `active_only`: Boolean (default: true). If true, only return active assignments

**Response**: 200 OK
```json
[
  {
    "project_id": 1,
    "name": "project-name",
    "description": "Project description",
    "status": "active",
    "phase": "planning",
    "role": "primary_backend",
    "assigned_at": "2025-01-01T09:00:00Z",
    "unassigned_at": null,
    "is_active": true
  }
]
```

**Note**: Results are filtered to only include projects the current user has access to.

**Error Responses**:
- 404 Not Found: Agent not found
- 500 Internal Server Error: Error fetching projects

---

### Blockers

#### GET /api/projects/{project_id}/blockers
**Purpose**: Get blockers for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Query Parameters**:
- `status`: Optional filter by status (`PENDING`, `RESOLVED`, `EXPIRED`)

**Response**: 200 OK
```json
{
  "blockers": [
    {
      "id": 1,
      "agent_id": "agent-123",
      "task_id": 5,
      "blocker_type": "SYNC" | "ASYNC",
      "question": "How should we handle edge case X?",
      "answer": "Use fallback strategy Y",
      "status": "PENDING" | "RESOLVED" | "EXPIRED",
      "created_at": "2025-01-01T12:00:00Z",
      "resolved_at": "2025-01-01T13:00:00Z"
    }
  ],
  "total": 10,
  "pending_count": 3,
  "sync_count": 1,
  "async_count": 2
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/projects/{project_id}/blockers/metrics
**Purpose**: Get blocker metrics for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK
```json
{
  "avg_resolution_time_seconds": 3600.5,
  "expiration_rate_percent": 5.2,
  "total_blockers": 100,
  "resolved_count": 80,
  "expired_count": 5,
  "pending_count": 15,
  "sync_count": 10,
  "async_count": 5
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### GET /api/blockers/{blocker_id}
**Purpose**: Get details of a specific blocker

**Authentication**: Required (user must have access to blocker's project)

**Path Parameters**:
- `blocker_id`: integer

**Response**: 200 OK
```json
{
  "id": 1,
  "agent_id": "agent-123",
  "project_id": 1,
  "task_id": 5,
  "blocker_type": "ASYNC",
  "question": "How should we handle edge case X?",
  "answer": "Use fallback strategy Y",
  "status": "RESOLVED",
  "created_at": "2025-01-01T12:00:00Z",
  "resolved_at": "2025-01-01T13:00:00Z"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Blocker not found

---

#### POST /api/blockers/{blocker_id}/resolve
**Purpose**: Resolve a blocker with user's answer

**Authentication**: Required (user must have access to blocker's project)

**Path Parameters**:
- `blocker_id`: integer

**Request Body**:
```json
{
  "answer": "Use fallback strategy Y and log the edge case"
}
```

**Validation**:
- `answer`: 1-5000 characters, required, cannot be whitespace-only

**Response**: 200 OK
```json
{
  "blocker_id": 1,
  "status": "RESOLVED",
  "resolved_at": "2025-01-01T13:00:00Z"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Blocker not found
- 409 Conflict: Blocker already resolved
  ```json
  {
    "error": "Blocker already resolved",
    "blocker_id": 1,
    "resolved_at": "2025-01-01T13:00:00Z"
  }
  ```
- 422 Unprocessable Entity: Validation error (empty answer)

**WebSocket Event**: Broadcasts `blocker_resolved` event to connected clients

---

### Chat

#### POST /api/projects/{project_id}/chat
**Purpose**: Send chat message to Lead Agent and get AI response

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**:
```json
{
  "message": "What's the current status of task 1.1.1?"
}
```

**Validation**:
- `message`: Required, cannot be empty after trimming

**Response**: 200 OK
```json
{
  "response": "Task 1.1.1 is currently in progress. The agent is implementing...",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Empty message or agent not started
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: Agent communication failure

**WebSocket Event**: Broadcasts `chat_message` event with assistant response

---

#### GET /api/projects/{project_id}/chat/history
**Purpose**: Get conversation history for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Query Parameters**:
- `limit`: Maximum messages to return (default: 100)
- `offset`: Number of messages to skip (default: 0)

**Response**: 200 OK
```json
{
  "messages": [
    {
      "role": "user" | "assistant",
      "content": "Message content",
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ]
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

### Discovery

#### POST /api/projects/{project_id}/discovery/answer
**Purpose**: Submit answer to current discovery question

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**:
```json
{
  "answer": "The main goal of this project is to..."
}
```

**Validation**:
- `answer`: 1-5000 characters, required, cannot be whitespace-only

**Response**: 200 OK
```json
{
  "success": true,
  "next_question": "What tech stack are you planning to use?",
  "is_complete": false,
  "current_index": 3,
  "total_questions": 20,
  "progress_percentage": 15.0
}
```

**When discovery is complete**:
```json
{
  "success": true,
  "next_question": null,
  "is_complete": true,
  "current_index": 20,
  "total_questions": 20,
  "progress_percentage": 100.0
}
```

**Error Responses**:
- 400 Bad Request: Project not in discovery phase or discovery not active
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: ANTHROPIC_API_KEY not configured or processing error

**WebSocket Events**:
- Broadcasts `discovery_answer_submitted` event
- Broadcasts `discovery_question_presented` or `discovery_completed` event

---

#### GET /api/projects/{project_id}/discovery/progress
**Purpose**: Get discovery progress for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK

**When discovery is idle**:
```json
{
  "project_id": 1,
  "phase": "discovery",
  "discovery": null
}
```

**When discovery is active**:
```json
{
  "project_id": 1,
  "phase": "discovery",
  "discovery": {
    "state": "discovering",
    "progress_percentage": 45.0,
    "answered_count": 9,
    "total_required": 20,
    "remaining_count": 11,
    "current_question": {
      "id": "q10",
      "text": "What are the main features?"
    }
  }
}
```

**When discovery is completed**:
```json
{
  "project_id": 1,
  "phase": "planning",
  "discovery": {
    "state": "completed",
    "progress_percentage": 100.0,
    "answered_count": 20,
    "total_required": 20,
    "structured_data": {
      "project_name": "My App",
      "tech_stack": ["React", "Node.js"],
      "features": ["Feature 1", "Feature 2"]
    }
  }
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: Error retrieving progress

---

### Checkpoints

#### GET /api/projects/{project_id}/checkpoints
**Purpose**: List all checkpoints for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Response**: 200 OK
```json
{
  "checkpoints": [
    {
      "id": 1,
      "project_id": 1,
      "name": "Before refactor",
      "description": "Safety checkpoint before major refactoring",
      "trigger": "manual" | "auto" | "phase_transition" | "pause",
      "git_commit": "a1b2c3d4e5f6g7h8",
      "database_backup_path": "/path/to/backup.sqlite",
      "context_snapshot_path": "/path/to/context.json",
      "metadata": {
        "project_id": 1,
        "phase": "active",
        "tasks_completed": 15,
        "tasks_total": 50,
        "agents_active": ["agent-123", "agent-456"],
        "last_task_completed": "1.5.3",
        "context_items_count": 120,
        "total_cost_usd": 2.45
      },
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found

---

#### POST /api/projects/{project_id}/checkpoints
**Purpose**: Create a new checkpoint for a project

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer

**Request Body**:
```json
{
  "name": "Before refactor",
  "description": "Safety checkpoint before major refactoring",
  "trigger": "manual"
}
```

**Validation**:
- `name`: 1-100 characters, required
- `description`: Optional, max 500 characters
- `trigger`: Defaults to "manual"

**Response**: 201 Created
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Before refactor",
  "description": "Safety checkpoint before major refactoring",
  "trigger": "manual",
  "git_commit": "a1b2c3d4e5f6g7h8",
  "database_backup_path": "/path/to/backup.sqlite",
  "context_snapshot_path": "/path/to/context.json",
  "metadata": {
    "project_id": 1,
    "phase": "active",
    "tasks_completed": 15,
    "tasks_total": 50,
    "agents_active": ["agent-123"],
    "last_task_completed": "1.5.3",
    "context_items_count": 120,
    "total_cost_usd": 2.45
  },
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project not found
- 500 Internal Server Error: Checkpoint creation failed

**WebSocket Event**: Broadcasts `checkpoint_created` event

---

#### GET /api/projects/{project_id}/checkpoints/{checkpoint_id}
**Purpose**: Get details of a specific checkpoint

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `checkpoint_id`: integer

**Response**: 200 OK
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Before refactor",
  "description": "Safety checkpoint before major refactoring",
  "trigger": "manual",
  "git_commit": "a1b2c3d4e5f6g7h8",
  "database_backup_path": "/path/to/backup.sqlite",
  "context_snapshot_path": "/path/to/context.json",
  "metadata": {
    "project_id": 1,
    "phase": "active",
    "tasks_completed": 15,
    "tasks_total": 50,
    "agents_active": ["agent-123"],
    "last_task_completed": "1.5.3",
    "context_items_count": 120,
    "total_cost_usd": 2.45
  },
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project or checkpoint not found

---

#### DELETE /api/projects/{project_id}/checkpoints/{checkpoint_id}
**Purpose**: Delete a checkpoint and its files

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `checkpoint_id`: integer

**Request Body**: None

**Response**: 204 No Content

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project or checkpoint not found
- 500 Internal Server Error: File deletion failed

**WebSocket Event**: Broadcasts `checkpoint_deleted` event

---

#### POST /api/projects/{project_id}/checkpoints/{checkpoint_id}/restore
**Purpose**: Restore project to checkpoint state (or preview diff)

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `checkpoint_id`: integer

**Request Body**:
```json
{
  "confirm_restore": false
}
```

**If `confirm_restore=false` (preview only)**:

**Response**: 200 OK
```json
{
  "checkpoint_name": "Before refactor",
  "diff": "diff --git a/file.py b/file.py\n..."
}
```

**If `confirm_restore=true` (actual restore)**:

**Response**: 202 Accepted
```json
{
  "success": true,
  "checkpoint_name": "Before refactor",
  "git_commit": "a1b2c3d4e5f6g7h8",
  "items_restored": 120
}
```

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project, checkpoint not found, or backup files missing
- 500 Internal Server Error: Restore failed

**WebSocket Event**: Broadcasts `checkpoint_restored` event (when confirm_restore=true)

---

#### GET /api/projects/{project_id}/checkpoints/{checkpoint_id}/diff
**Purpose**: Get git diff for a checkpoint

**Authentication**: Required (user must have project access)

**Path Parameters**:
- `project_id`: integer
- `checkpoint_id`: integer

**Response**: 200 OK
```json
{
  "files_changed": 5,
  "insertions": 150,
  "deletions": 80,
  "diff": "diff --git a/file.py b/file.py\nindex a1b2c3d..e4f5g6h 100644\n..."
}
```

**Response Headers**:
- `Cache-Control`: `no-cache, must-revalidate`
- `ETag`: `"a1b2c3d4e5f6g7h8"` (SHA-256 hash of checkpoint:HEAD commits)
- `X-Binary-Files`: Number of binary files changed

**Error Responses**:
- 403 Forbidden: Access denied
- 404 Not Found: Project, checkpoint, or git commit not found
- 500 Internal Server Error: Git operation failed or timed out

**Notes**:
- Diff output is truncated to 10MB maximum
- Binary files are counted separately in `X-Binary-Files` header
- ETag changes when HEAD commit changes

---

## WebSocket API

### Connection

**Endpoint**: `ws://localhost:8000/ws`

**Authentication**:
- Required when `AUTH_REQUIRED=true` (production)
- Token passed as query parameter: `ws://localhost:8000/ws?token=YOUR_SESSION_TOKEN`
- Token validated against sessions table
- Unauthenticated connections allowed when `AUTH_REQUIRED=false` (development)

**Connection Flow**:
1. Client connects to WebSocket endpoint with token
2. Server validates token against sessions table
3. Server checks token expiration
4. If valid, connection is accepted and user_id is associated with connection
5. If invalid/expired, connection is closed with appropriate code

**Close Codes**:
- 1008: Authentication required but missing/invalid token
- 1008: Session expired

**Health Check**: `GET /ws/health` returns `{"status": "ready"}`

---

### Client Messages

All client messages must be valid JSON.

#### Ping
**Purpose**: Heartbeat to keep connection alive

**Format**:
```json
{
  "type": "ping"
}
```

**Server Response**:
```json
{
  "type": "pong"
}
```

---

#### Subscribe
**Purpose**: Subscribe to specific project updates

**Format**:
```json
{
  "type": "subscribe",
  "project_id": 1
}
```

**Validation**:
- `project_id`: Required, must be integer, must be positive
- User must have access to the project (authorization check)

**Server Response (success)**:
```json
{
  "type": "subscribed",
  "project_id": 1
}
```

**Server Response (error)**:
```json
{
  "type": "error",
  "error": "Error message"
}
```

**Error Conditions**:
- Missing project_id
- Non-integer project_id
- Non-positive project_id (≤ 0)
- User lacks access to project
- Subscription failed

---

#### Unsubscribe
**Purpose**: Unsubscribe from specific project updates

**Format**:
```json
{
  "type": "unsubscribe",
  "project_id": 1
}
```

**Validation**:
- `project_id`: Required, must be integer, must be positive

**Server Response (success)**:
```json
{
  "type": "unsubscribed",
  "project_id": 1
}
```

**Server Response (error)**:
```json
{
  "type": "error",
  "error": "Error message"
}
```

---

### Server Messages

Server broadcasts events to subscribed clients. All events are JSON objects.

#### agent_started
**When**: Agent starts for a project

**Format**:
```json
{
  "type": "agent_started",
  "project_id": 1,
  "agent_id": "agent-123",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### status_update
**When**: Project status changes

**Format**:
```json
{
  "type": "status_update",
  "project_id": 1,
  "status": "running",
  "phase": "active",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### chat_message
**When**: New chat message (user or assistant)

**Format**:
```json
{
  "type": "chat_message",
  "project_id": 1,
  "role": "assistant" | "user",
  "content": "Message content",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### task_assigned
**When**: Task is assigned to an agent

**Format**:
```json
{
  "type": "task_assigned",
  "project_id": 1,
  "task_id": 5,
  "agent_id": "agent-123",
  "task_number": "1.1.1",
  "title": "Task title",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### task_completed
**When**: Task is completed

**Format**:
```json
{
  "type": "task_completed",
  "project_id": 1,
  "task_id": 5,
  "task_number": "1.1.1",
  "title": "Task title",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### blocker_created
**When**: New blocker is created

**Format**:
```json
{
  "type": "blocker_created",
  "project_id": 1,
  "blocker_id": 1,
  "blocker_type": "SYNC" | "ASYNC",
  "question": "How should we handle edge case X?",
  "task_id": 5,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### blocker_resolved
**When**: Blocker is resolved

**Format**:
```json
{
  "type": "blocker_resolved",
  "blocker_id": 1,
  "answer": "Use fallback strategy Y",
  "resolved_at": "2025-01-01T13:00:00Z"
}
```

---

#### discovery_answer_submitted
**When**: Discovery answer is submitted

**Format**:
```json
{
  "type": "discovery_answer_submitted",
  "project_id": 1,
  "question_id": "q5",
  "answer_preview": "The main goal is...",
  "current_index": 5,
  "total_questions": 20,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### discovery_question_presented
**When**: New discovery question is presented

**Format**:
```json
{
  "type": "discovery_question_presented",
  "project_id": 1,
  "question_id": "q6",
  "question_text": "What tech stack are you using?",
  "current_index": 6,
  "total_questions": 20,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### discovery_completed
**When**: Discovery phase is completed

**Format**:
```json
{
  "type": "discovery_completed",
  "project_id": 1,
  "total_answers": 20,
  "next_phase": "prd_generation",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### checkpoint_created
**When**: Checkpoint is created

**Format**:
```json
{
  "type": "checkpoint_created",
  "project_id": 1,
  "checkpoint_id": 1,
  "checkpoint_name": "Before refactor",
  "trigger": "manual",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### checkpoint_deleted
**When**: Checkpoint is deleted

**Format**:
```json
{
  "type": "checkpoint_deleted",
  "project_id": 1,
  "checkpoint_id": 1,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### checkpoint_restored
**When**: Checkpoint is restored

**Format**:
```json
{
  "type": "checkpoint_restored",
  "project_id": 1,
  "checkpoint_id": 1,
  "checkpoint_name": "Before refactor",
  "git_commit": "a1b2c3d4e5f6g7h8",
  "files_changed": 5,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### context_tier_updated
**When**: Context tiers are updated

**Format**:
```json
{
  "type": "context_tier_updated",
  "agent_id": "agent-123",
  "item_count": 30,
  "tier_changes": {
    "hot": 5,
    "warm": 10,
    "cold": 15
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

#### flash_save_completed
**When**: Flash save operation completes

**Format**:
```json
{
  "type": "flash_save_completed",
  "agent_id": "agent-123",
  "checkpoint_id": 42,
  "reduction_percentage": 65.5,
  "items_archived": 25,
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

### Error Messages

**When**: Invalid client message or processing error

**Format**:
```json
{
  "type": "error",
  "error": "Error description"
}
```

**Common Errors**:
- "Invalid JSON format" - Malformed JSON
- "Subscribe message requires project_id" - Missing project_id
- "project_id must be an integer, got string" - Wrong type
- "project_id must be a positive integer" - Invalid value
- "Access denied: you do not have permission to access this project" - Authorization failure
- "Failed to subscribe to project" - Subscription error
- "Failed to unsubscribe from project" - Unsubscription error

---

## API Conventions

### Authentication
- All REST endpoints require authentication via session token (except health checks)
- WebSocket requires token as query parameter when `AUTH_REQUIRED=true`
- Tokens validated against `sessions` table
- Expired tokens are rejected and deleted from database

### Authorization
- User access checked via `user_has_project_access()` for all project-scoped endpoints
- Returns 403 Forbidden when user lacks access to existing resource
- Multi-agent endpoint `/api/agents/{agent_id}/projects` filters results by user access

### Timestamps
- All timestamps in ISO 8601 format (RFC 3339)
- UTC timezone indicated with 'Z' suffix
- Example: `2025-01-01T12:00:00Z`

### Error Response Format
Most endpoints return errors in this format:
```json
{
  "detail": "Error message"
}
```

Some endpoints return structured errors:
```json
{
  "error": "Error message",
  "project_id": 1
}
```

### Pagination
- Uses `limit` and `offset` query parameters
- Returns `total` count in response
- Default limits documented per endpoint

### Status Codes
- 200 OK: Successful GET/PUT/PATCH
- 201 Created: Successful POST creating resource
- 202 Accepted: Async operation started
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid input or state
- 403 Forbidden: Access denied
- 404 Not Found: Resource not found
- 409 Conflict: Duplicate resource
- 422 Unprocessable Entity: Validation error
- 500 Internal Server Error: Server error

---

## Data Models

### Project Statuses
- `init`: Project initialized
- `planning`: PRD generation/planning
- `running`: Agent actively working
- `active`: Project active
- `paused`: Execution paused
- `stopped`: Agent terminated
- `completed`: Project complete

### Project Phases
- `discovery`: Discovery questions
- `planning`: PRD and task planning
- `active`: Development
- `review`: Code review
- `complete`: Project complete

### Task Statuses
- `pending`: Not started
- `assigned`: Assigned to agent
- `in_progress`: Currently executing
- `blocked`: Blocked by dependency or blocker
- `completed`: Successfully completed
- `failed`: Failed execution

### Blocker Types
- `SYNC`: Critical blocker - agent pauses immediately
- `ASYNC`: Clarification request - agent continues work

### Blocker Statuses
- `PENDING`: Awaiting user response
- `RESOLVED`: User provided answer
- `EXPIRED`: Blocker timed out (24h default)

### Agent Types
- `lead`: Lead agent coordinating project
- `backend`: Backend development agent
- `frontend`: Frontend development agent
- `test`: Testing agent
- `review`: Code review agent

### Agent Maturity Levels
- `directive`: D1 - Low skill, needs step-by-step
- `coaching`: D2 - Some skill, needs guidance
- `supporting`: D3 - High skill, needs autonomy
- `delegating`: D4 - Expert, full ownership

### Agent Statuses
- `idle`: Not working on task
- `working`: Actively executing task
- `blocked`: Blocked by dependency
- `offline`: Not available

### Source Types
- `git_remote`: Clone from Git repository
- `local_path`: Use existing local directory
- `upload`: Upload files (future)
- `empty`: Start with empty project

---

## Rate Limits

No rate limits currently enforced. Future versions may implement rate limiting on computationally expensive endpoints.

---

## Versioning

API version: v1 (implicit)

Breaking changes will result in new API version with `/api/v2/` prefix.

---

## Support

For issues or questions, see the [CodeFRAME core repository](https://github.com/frankbria/codeframe) and [CodeFRAME CLI repository](https://github.com/frankbria/codeframe-cli).
