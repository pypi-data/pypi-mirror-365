# Development Guide

This guide explains how to develop the `frost` package using the containerized
development environment.

## Quick Start

### 1. Start Development Container

```bash
make docker-dev
```

This will:

-   Build the development Docker image
-   Start the container with your source code mounted
-   Drop you into an interactive shell inside the container

### 2. Inside the Container

Once inside the container, you can use all the standard development commands:

```bash
# Install dependencies (already done during build, but useful for updates)
uv sync --frozen --group all --all-extras

# Format code
uv run ruff check --fix --exit-zero frost tests
uv run ruff format frost tests

# Run linting
uv run ruff check frost tests

# Run type checking
uv run mypy frost tests
uv run pyright frost tests

# Run tests
uv run pytest tests

# Run full CI pipeline
uv run ruff check --fix --exit-zero frost tests && \
uv run ruff format frost tests && \
uv run ruff check frost tests && \
uv run mypy frost tests && \
uv run pyright frost tests && \
uv run pytest tests
```

### 3. Alternative: Run Commands from Host

You can also run individual commands without entering the container:

```bash
# Run tests
make docker-dev-run cmd="uv run pytest tests"

# Run linting
make docker-dev-run cmd="uv run ruff check frost tests"

# Run type checking
make docker-dev-run cmd="uv run mypy frost tests"

# Format code
make docker-dev-run cmd="uv run ruff format frost tests"
```

## Development Workflow

### Live Code Editing

-   Your source code is mounted into the container at `/app`
-   Changes you make on your host machine are immediately reflected in the
    container
-   The virtual environment is persisted in a Docker volume for faster startup

### Managing Dependencies

To add new dependencies:

```bash
# Enter the container
make docker-dev

# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --group dev <package-name>

# Exit container and rebuild to bake in changes
exit
make docker-dev-clean
make docker-dev
```

### File Permissions

The container runs as user `1000:1000` to match typical development setups and
avoid permission issues with mounted volumes.

## Available Commands

| Command                         | Description                                 |
| ------------------------------- | ------------------------------------------- |
| `make docker-dev`               | Start development container and enter shell |
| `make docker-dev-run cmd='...'` | Run a specific command in the container     |
| `make docker-dev-stop`          | Stop the development container              |
| `make docker-dev-clean`         | Clean up container and volumes              |

## Container Features

-   **Python 3.13**: Latest Python version as per project requirements
-   **UV Package Manager**: Fast, modern Python package management
-   **All Dev Tools**: Ruff, MyPy, PyRight, pytest pre-installed
-   **Git**: Available for version control operations
-   **Persistent Virtual Environment**: Speeds up container restarts
-   **Source Code Mounting**: Live editing without rebuilds

## Alternative: Direct Docker Usage

If you prefer not to use the Make targets:

```bash
# Build and start container
docker-compose --profile dev -f docker-compose.dev.yml up --build -d frost-dev

# Enter container
docker-compose --profile dev -f docker-compose.dev.yml exec frost-dev bash

# Stop container
docker-compose --profile dev -f docker-compose.dev.yml down
```

## Troubleshooting

### Permission Issues

If you encounter permission issues, ensure your user ID is 1000, or modify the
`user` field in `docker-compose.dev.yml` to match your user ID:

```bash
# Check your user ID
id -u

# Update docker-compose.dev.yml if needed
user: "$(id -u):$(id -g)"
```

### Slow Performance

If the container feels slow:

-   Ensure Docker has sufficient resources allocated
-   Consider using Docker Desktop's improved file sharing on macOS

### Dependencies Not Found

If dependencies seem missing after adding them:

```bash
make docker-dev-clean
make docker-dev
```

This rebuilds the container with updated dependencies.

```
🐳 Starting development container...
docker-compose --profile dev -f docker-compose.dev.yml up --build -d frost-dev
WARN[0000] /Users/gaohn/gaohn/frost/docker-compose.dev.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
unable to get image 'frost-frost-dev': Cannot connect to the Docker daemon at unix:///Users/gaohn/.docker/run/docker.sock. Is the docker daemon running?
make: *** [docker-dev] Error 1
❯ make docker-dev
🐳 Starting development container...
docker-compose --profile dev -f docker-compose.dev.yml up --build -d frost-dev
WARN[0000] /Users/gaohn/gaohn/frost/docker-compose.dev.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
Compose can now delegate builds to bake for better performance.
 To do so, set COMPOSE_BAKE=true.
[+] Building 19.2s (17/19)                                                                                                                                   docker:desktop-linux
 => [frost-dev internal] load build definition from Dockerfile.dev                                                                                                           0.0s
 => => transferring dockerfile: 1.08kB                                                                                                                                       0.0s
 => [frost-dev internal] load metadata for docker.io/library/debian:bookworm-slim                                                                                            3.9s
 => [frost-dev internal] load metadata for ghcr.io/astral-sh/uv:bookworm-slim                                                                                                3.9s
 => [frost-dev auth] library/debian:pull token for registry-1.docker.io                                                                                                      0.0s
 => [frost-dev internal] load .dockerignore                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                              0.0s
 => [frost-dev builder 1/6] FROM ghcr.io/astral-sh/uv:bookworm-slim@sha256:f958f0d24ea43cb51a864e3f2acfe7d016f5b65e9d89ad7463e91435477221aa                                  2.5s
 => => resolve ghcr.io/astral-sh/uv:bookworm-slim@sha256:f958f0d24ea43cb51a864e3f2acfe7d016f5b65e9d89ad7463e91435477221aa                                                    0.0s
 => => sha256:9222aaac7ddc97d5c774e116b5e256f94a5a5ca7a5feb6d45b4453723e81f2b8 675B / 675B                                                                                   0.0s
 => => sha256:58a94372f7f21e77451794129b234cce51131d4a23d12485fd44b142d533e51f 1.50kB / 1.50kB                                                                               0.0s
 => => sha256:312dfc1c4d131b949b83ee3420313e249b52bd6557cdd9a7293f1541ef4deb6f 16.75MB / 16.75MB                                                                             2.3s
 => => sha256:f958f0d24ea43cb51a864e3f2acfe7d016f5b65e9d89ad7463e91435477221aa 2.21kB / 2.21kB                                                                               0.0s
 => => extracting sha256:312dfc1c4d131b949b83ee3420313e249b52bd6557cdd9a7293f1541ef4deb6f                                                                                    0.1s
 => [frost-dev stage-1 1/7] FROM docker.io/library/debian:bookworm-slim@sha256:e5865e6858dacc255bead044a7f2d0ad8c362433cfaa5acefb670c1edf54dfef                              0.0s
 => => resolve docker.io/library/debian:bookworm-slim@sha256:e5865e6858dacc255bead044a7f2d0ad8c362433cfaa5acefb670c1edf54dfef                                                0.0s
 => => sha256:e5865e6858dacc255bead044a7f2d0ad8c362433cfaa5acefb670c1edf54dfef 8.56kB / 8.56kB                                                                               0.0s
 => => sha256:6e748d5b2b6c313522604e8309634b9406fc637c4cf11a6e1294d2d4f2a73903 1.04kB / 1.04kB                                                                               0.0s
 => => sha256:b107311e391cb95dd3a90d46cb09b66bf2e2d5d648df16b992d84263b812f5ef 468B / 468B                                                                                   0.0s
 => [frost-dev internal] load build context                                                                                                                                  2.1s
 => => transferring context: 161.66MB                                                                                                                                        2.0s
 => [frost-dev stage-1 2/7] RUN apt-get update && apt-get install -y --no-install-recommends     git     && rm -rf /var/lib/apt/lists/*                                      7.2s
 => [frost-dev builder 2/6] RUN uv python install 3.13                                                                                                                       4.7s
 => [frost-dev stage-1 3/7] RUN groupadd -r python && useradd -r -g python python &&     groupadd -r app && useradd -r -g app -m -d /home/app app                            0.3s
 => [frost-dev builder 3/6] WORKDIR /app                                                                                                                                     0.0s
 => [frost-dev builder 4/6] RUN --mount=type=cache,target=/root/.cache/uv     --mount=type=bind,source=uv.lock,target=uv.lock     --mount=type=bind,source=pyproject.toml,t  4.0s
 => [frost-dev builder 5/6] COPY . /app                                                                                                                                      1.2s
 => [frost-dev builder 6/6] RUN --mount=type=cache,target=/root/.cache/uv     uv sync --locked                                                                               2.1s
 => CACHED [frost-dev stage-1 4/7] COPY --from=builder --chown=python:python /python /python                                                                                 0.0s
 => ERROR [frost-dev stage-1 5/7] COPY --from=builder /uv /uvx /usr/local/bin/                                                                                               0.0s
------
 > [frost-dev stage-1 5/7] COPY --from=builder /uv /uvx /usr/local/bin/:
------
failed to solve: failed to compute cache key: failed to calculate checksum of ref 06747cce-2f3b-4a2e-8a50-037c964ce415::zn1y7uh1mpstknbq4oz05xymq: "/uv": not found
make: *** [docker-dev] Error 1
```
