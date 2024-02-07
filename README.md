# Caobo Backend

This repository contains the backend service for the Caobo project, implemented in Python. It utilizes FastAPI for creating a RESTful API, Alembic for database migrations, and Docker for containerization.

## Features

- RESTful API endpoints
- Database migration management with Alembic
- Containerized deployment with Docker

## Getting Started

### Prerequisites

- Docker
- Python 3.8 or newer
- Poetry for dependency management
- Remote - Containers extension for Visual Studio Code

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourgithubusername/caobo-backend-main.git
   cd caobo-backend-main
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Development Environment

The project supports development inside a container using Visual Studio Code's Remote - Containers extension. This ensures a consistent development environment for all contributors.

### Prerequisites

- Visual Studio Code
- Docker
- Remote - Containers extension for Visual Studio Code

### Starting Development Container

1. Open Visual Studio Code.
2. Ensure you have the Remote - Containers extension installed.
3. Open the command palette (Ctrl+Shift+P on Windows/Linux, Command+Shift+P on macOS).
4. Select `Remote-Containers: Open Folder in Container...`.
5. Navigate to the cloned repository directory and open it.


Visual Studio Code will build the container defined in the `.devcontainer` directory and start a new VS Code session inside the container. Your development environment is now set up and ready to use.

### Run the app

``` python
uvicorn app.main:app --reload --port 5000
```
The API will be available at `http://localhost:5000`.

Check the API docs at `http://localhost:5000/docs` and `http://localhost:5000/redoc`

## Testing

To run tests, execute:

```bash
pytest tests/test_dependencies.py
```