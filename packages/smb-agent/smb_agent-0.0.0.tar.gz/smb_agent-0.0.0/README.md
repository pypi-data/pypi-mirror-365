# SMB Agent

### Components

- **Frontend UI**: React/Next.js interface for user interactions
- **Orchestrator**: Agent code with tools

### Running the Application

First set env vars (.env.example)

#### Simple Start
Bash script that runs app and opens it in a window:
```{bash}
./scripts/quick-start.sh
```

#### Manual build and run with Docker Compose
```{bash}
docker-compose up --build
```

### Development Setup

#### Pre-commit Hooks
This project uses pre-commit hooks to ensure code quality. To set up:

```{bash}
./scripts/setup-precommit.sh
```

This will:
- Install ruff linter and formatter
- Install pytest for running tests
- Set up pre-commit hooks that run automatically before each commit

To run the hooks manually:
```{bash}
uv run pre-commit run --all-files
```