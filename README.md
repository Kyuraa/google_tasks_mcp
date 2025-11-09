# Google Tasks MCP Server

A Model Context Protocol (MCP) server that provides Google Tasks integration for AI assistants. The MCP server is created from a FastAPI backend using `FastMCP.from_fastapi()`, automatically generating MCP tools from FastAPI routes.

## Architecture

```
AI Assistant → MCP Server (from FastAPI) → Google Tasks API
```

## Features

### Task List Management
- List all task lists
- Create new task lists
- Get task list details
- Update task list titles
- Delete task lists

### Task Management
- List tasks in a task list
- Create new tasks
- Get task details
- Update tasks (title, notes, due date, status)
- Delete tasks
- Mark tasks as completed/incomplete

## Setup

### 1. Google API Credentials

Create a `tokens.json` file in the `fastapi_backend/` directory with your OAuth tokens:
```json
{
  "refresh_token": "your_refresh_token",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

The system will automatically use these tokens to authenticate with Google Tasks API. No additional `credentials.json` file is needed.

### 2. Install Dependencies

Install all dependencies from the root directory:

```bash
pip install -r requirements.txt
```

### 3. Run the MCP Server

The MCP server now includes the FastAPI backend, so you only need to run one service:

```bash
cd mcp_server
python server.py
```

The first time you run this, it will open a browser for Google OAuth authentication. Complete the authentication flow and the tokens will be saved.

**Note**: The FastAPI backend is now embedded within the MCP server and accessible at `/api/*` endpoints.

## Configuration

### Environment Variables

You can configure the following environment variables:

- `FASTAPI_URL`: URL of the FastAPI backend (default: `http://localhost:8000`)
- `GOOGLE_CREDENTIALS_PATH`: Path to Google credentials.json file (default: `credentials.json`)
- `GOOGLE_TOKEN_PATH`: Path to save Google OAuth tokens (default: `tokens.json`)

## MCP Configuration

Add the following to your MCP settings file (e.g., `cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "google-tasks": {
      "command": "python",
      "args": ["/path/to/google_tasks_mcp/mcp_server/server.py"],
      "env": {
        "FASTAPI_URL": "http://localhost:8000",
        "GOOGLE_TOKEN_PATH": "/path/to/google_tasks_mcp/fastapi_backend/tokens.json"
      }
    }
  }
}
```

**Important**: Update the paths in the configuration to match your actual file locations. The `GOOGLE_TOKEN_PATH` should point to your `tokens.json` file.

## Available Tools

### Task List Tools
- `list_task_lists()` - List all task lists
- `create_task_list(title)` - Create a new task list
- `get_task_list(tasklist_id)` - Get task list details
- `update_task_list(tasklist_id, title)` - Update task list title
- `delete_task_list(tasklist_id)` - Delete a task list

### Task Tools
- `list_tasks(tasklist_id)` - List tasks in a task list
- `create_task(tasklist_id, title, notes?, due?)` - Create a new task
- `get_task(tasklist_id, task_id)` - Get task details
- `update_task(tasklist_id, task_id, title?, notes?, due?, status?)` - Update a task
- `delete_task(tasklist_id, task_id)` - Delete a task
- `complete_task(tasklist_id, task_id)` - Mark task as completed
- `uncomplete_task(tasklist_id, task_id)` - Mark task as needs action

## API Endpoints

The FastAPI backend provides the following REST endpoints:

### Task Lists
- `GET /tasklists` - List all task lists
- `POST /tasklists` - Create a task list
- `GET /tasklists/{id}` - Get task list details
- `PUT /tasklists/{id}` - Update task list
- `DELETE /tasklists/{id}` - Delete task list

### Tasks
- `GET /tasklists/{list_id}/tasks` - List tasks in a task list
- `POST /tasklists/{list_id}/tasks` - Create a task
- `GET /tasklists/{list_id}/tasks/{task_id}` - Get task details
- `PUT /tasklists/{list_id}/tasks/{task_id}` - Update a task
- `DELETE /tasklists/{list_id}/tasks/{task_id}` - Delete a task

## Development

### Testing the FastAPI Backend

```bash
cd fastapi_backend
curl http://localhost:8000/health
```

### Testing the MCP Server

You can test the MCP server using the MCP Inspector or by integrating it with your AI assistant.

## Troubleshooting

### Authentication Issues
- Ensure `tokens.json` contains valid OAuth credentials with refresh_token, client_id, and client_secret
- Delete or update `tokens.json` if tokens are invalid or expired
- Check that the Google Tasks API is enabled in your Google Cloud project

### Connection Issues
- Ensure the FastAPI backend is running on the expected port
- Check the `FASTAPI_URL` environment variable in the MCP server
- Verify network connectivity between MCP server and FastAPI backend

### API Errors
- Check the FastAPI logs for detailed error messages
- Ensure your Google API quotas are not exceeded
- Verify that task list and task IDs are valid

## License

This project is open source. Feel free to modify and distribute.
