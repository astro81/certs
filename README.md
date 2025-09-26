## Prerequisites

- [Nix](https://nixos.org/download.html) (>= 2.13)  
- [Docker](https://www.docker.com/get-started)  
- [Docker Compose](https://docs.docker.com/compose/)

Optional: `curl` or `wget` for flake commands.

---

## Setup

### With Flakes (Recommended)

1. **Clone the repository**

```bash
git clone <repo-url>
cd <repo-directory>
```

2. **Enter the development shell**

```bash
nix develop
```

3. **Start/Stop**
```bash
# Start the full stack in Docker
nix run .#up

# Stop everything
nix run .#down
```

4. **Utils**
```bash
# Django commands
run            # runserver
migrations     # makemigrations
migrate        # migrate
createapp      # startapp
createadmin    # createsuperuser

# Docker-specific commands
docker-migrations
docker-migrate
docker-createapp
docker-createadmin

# Clean Docker resources
docker-clean-all
```

### Without Flakes
1. **Install Dependencies**
```bash
docker-compose
postgresql
mkcert
python314
uv
```

2. **Start/Stop**
```bash
# Start the full stack in Docker
docker compose up --build

# Stop everything
docker compose down
```

3. **Utils**

```bash
docker compose exec django_backend uv run manage.py makemigrations
docker compose exec django_backend uv run manage.py migrate --no-input
docker compose exec django_backend uv run manage.py startapp
docker compose exec django_backend uv run manage.py createsuperuser
```

