# AI Filesystem Service

A virtual filesystem service designed for AI agents, providing secure file storage and management through LangChain-compatible tools. Each user gets an isolated filesystem where they can create, read, update, and append to files.

## Features

- 🔐 **User Isolation**: Each user has their own isolated filesystem using PostgreSQL Row Level Security
- 🛠️ **LangChain Integration**: Ready-to-use tools for AI agents
- 🔄 **Version Control**: Automatic versioning for all file changes
- 🐳 **Docker Support**: Easy local development with docker-compose
- 🔑 **Flexible Authentication**: Supports both Supabase auth and dev mode

## Architecture

The system consists of three main components:

1. **FastAPI Server** (`server/`): REST API that handles file operations
2. **PostgreSQL Database**: Stores files with user isolation via RLS
3. **LangChain Tools** (`ai_filesystem/`): Python client and tools for AI agents

## Quick Start

### Local Development with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-filesystem.git
cd ai-filesystem
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up
```

This will start:
- PostgreSQL database on port 5432
- FastAPI server on http://localhost:8000

### Using the Filesystem Tools

```python
from ai_filesystem import get_filesystem_tools

# Initialize tools
tools = get_filesystem_tools("http://localhost:8000")

# Use with LangChain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
llm_with_tools = llm.bind_tools(tools)

# The tools will automatically handle authentication
# based on your configuration
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/dbname` |
| `SUPABASE_URL` | Your Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key for auth | `eyJhbGc...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEV_MODE` | Skip authentication (development only) | `false` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `10485760` (10MB) |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per user | `100` |

## Authentication

The service supports two authentication modes:

### Production Mode (DEV_MODE=false)

Uses Supabase JWT tokens for authentication. Each request must include a valid Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/v1/files
```

In LangChain/LangGraph, the token is automatically extracted from the config:

```python
config = {
    "configurable": {
        "langgraph_auth_user": {
            "supabase_token": "your_jwt_token"
        }
    }
}
```

### Development Mode (DEV_MODE=true)

Bypasses authentication for local testing. Any Bearer token is accepted, and all users get ID `00000000-0000-0000-0000-000000000000`.

⚠️ **Warning**: Never use DEV_MODE in production!

**NOTE** If you are testing an agent locally, you need to set `DEV_MODE=true` in your agent's environment as well. This will enable the tools to work without custom authentication being set up.

## API Endpoints

All endpoints require authentication (unless in dev mode):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/files` | List all files for the authenticated user |
| GET | `/v1/files/{path}` | Read a specific file |
| POST | `/v1/files` | Create a new file |
| PUT | `/v1/files/{path}` | Update file (requires version) |
| POST | `/v1/files/{path}/append` | Append to existing file |

## Database Schema

The service uses a single `user_files` table with Row Level Security:

```sql
CREATE TABLE user_files (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    path TEXT NOT NULL,
    content TEXT,
    size BIGINT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, path)
);
```

## Deployment

### Railway Deployment

1. Create a new Railway project
2. Add a PostgreSQL service
3. Add your GitHub repository as a service
4. Set environment variables:
   - `DATABASE_URL` (auto-set by Railway)
   - `SUPABASE_URL` and `SUPABASE_ANON_KEY`
   - `DEV_MODE=false` for production
5. Run database migrations using Railway CLI:
   ```bash
   railway link
   railway connect postgres
   # Paste contents of server/migrations/001_create_user_files.sql
   ```

### Other Platforms

The service includes a `Dockerfile` and can be deployed to any platform that supports containers:
- Render
- Fly.io
- Google Cloud Run
- AWS App Runner

## Security Considerations

1. **Row Level Security**: The database uses RLS to ensure users can only access their own files
2. **Authentication**: In production, all requests are validated against Supabase
3. **Version Control**: Prevents race conditions with optimistic locking
4. **Rate Limiting**: Configurable per-user rate limits
5. **File Size Limits**: Configurable maximum file size

## Development

### Project Structure

```
.
├── server/                 # FastAPI backend
│   ├── main.py           # Application entry point
│   ├── routers/          # API endpoints
│   ├── auth.py           # Authentication logic
│   ├── database.py       # Database connection
│   └── migrations/       # SQL migrations
├── ai_filesystem/         # LangChain tools
│   ├── tools.py          # Tool implementations
│   ├── client.py         # HTTP client
│   └── models.py         # Pydantic models
├── docker-compose.yml     # Local development setup
└── Dockerfile            # Container definition
```