# Member Registration App - Container Deployment

## 🐋 Running with Podman

This guide shows how to run the member registration app using Podman on any machine.

### Prerequisites

- **Podman** installed on the target machine
- **Git** (optional, for cloning)

### Method 1: Using the Management Script (Recommended)

The easiest way to manage the container is using the provided `manage.sh` script:

```bash
# Make script executable
chmod +x manage.sh

# Build the image
./manage.sh build

# Start the container
./manage.sh start

# View status
./manage.sh status

# View registered members
./manage.sh members

# Show logs
./manage.sh logs

# Restart the container
./manage.sh restart

# Stop the container
./manage.sh stop

# Clean up everything
./manage.sh clean
```

### Management Script Features

The `manage.sh` script provides:

- ✅ **Automated build process**
- ✅ **Container lifecycle management** (start/stop/restart)
- ✅ **Volume management** with automatic creation
- ✅ **Status monitoring** and health checks
- ✅ **Log viewing** with follow mode
- ✅ **Member data viewing** without container access
- ✅ **Safe cleanup** with confirmation prompts
- ✅ **Colored output** for better readability
- ✅ **Error handling** and validation

**Available Commands:**
```bash
./manage.sh build     # Build container image
./manage.sh start     # Start the application
./manage.sh stop      # Stop the application
./manage.sh restart   # Restart the application
./manage.sh status    # Show container status
./manage.sh logs      # View application logs
./manage.sh members   # View registered members
./manage.sh clean     # Clean up resources
./manage.sh help      # Show help information
```

### Method 2: Using the Dockerfile Manually

#### 1. Copy Files to Target Machine

Transfer these files to your target machine:
```
member-join/
├── Dockerfile
├── main.py
├── view_members.py
├── pyproject.toml
├── manage.sh              # Container management script
└── .gitignore
```

#### 2. Build the Container Image

```bash
podman build -t member-registration .
```

#### 3. Run the Container

**Basic run (data lost on container stop):**
```bash
podman run -p 8085:8085 member-registration
```

**With persistent data (recommended):**
```bash
# Create a volume for the database
podman volume create member-data

# Run with persistent storage
podman run -d \
  --name member-app \
  -p 8085:8085 \
  -v member-data:/app/data \
  member-registration
```

#### 4. Access the Application

Open your browser and go to:
- **http://localhost:8085** (on the same machine)
- **http://YOUR_SERVER_IP:8085** (from other machines on the network)

#### 5. View Registered Members

```bash
# Access the running container
podman exec -it member-app python view_members.py
```

#### 6. Stop and Start

```bash
# Stop the container
podman stop member-app

# Start it again (data preserved)
podman start member-app

# Remove container (keeps volume)
podman rm member-app

# Remove everything including data
podman volume rm member-data
```

### Method 2: Docker Compose Alternative (Podman Compose)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  member-registration:
    build: .
    ports:
      - "8085:8085"
    volumes:
      - member_data:/app/data
    environment:
      - HOST=0.0.0.0
      - SHOW_BROWSER=false
      - DATABASE_PATH=/app/data/members.db
    restart: unless-stopped

volumes:
  member_data:
```

Run with:
```bash
podman-compose up -d
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `/app/data/members.db` | Database file location |
| `HOST` | `0.0.0.0` | Host to bind to |
| `SHOW_BROWSER` | `false` | Whether to open browser |

### Firewall Configuration

If accessing from other machines, ensure port 8085 is open:

**CentOS/RHEL/Fedora:**
```bash
sudo firewall-cmd --add-port=8085/tcp --permanent
sudo firewall-cmd --reload
```

**Ubuntu/Debian:**
```bash
sudo ufw allow 8085
```

### Troubleshooting

#### Port Already in Use
```bash
# Find what's using port 8085
sudo netstat -tulpn | grep 8085

# Use a different port
podman run -p 8090:8085 member-registration
```

#### Container Won't Start
```bash
# Check logs
podman logs member-app

# Run interactively for debugging
podman run -it --rm member-registration /bin/bash
```

#### Database Issues
```bash
# Check database location
podman exec member-app ls -la /app/data/

# Backup database
podman cp member-app:/app/data/members.db ./backup-members.db
```

### Production Considerations

1. **Use a reverse proxy** (nginx) for SSL/TLS
2. **Set up monitoring** and health checks
3. **Configure log rotation**
4. **Use secrets** for sensitive configuration
5. **Set resource limits:**

```bash
podman run -d \
  --name member-app \
  --memory=512m \
  --cpus=1.0 \
  -p 8085:8085 \
  -v member-data:/app/data \
  member-registration
```

### Quick Commands Reference

```bash
# Build image
podman build -t member-registration .

# Run with persistent data
podman run -d --name member-app -p 8085:8085 -v member-data:/app/data member-registration

# View logs
podman logs -f member-app

# View members
podman exec -it member-app python view_members.py

# Stop/start
podman stop member-app
podman start member-app

# Clean up
podman rm member-app
podman volume rm member-data
podman rmi member-registration
```

### Features

✅ **Web-based registration form**
✅ **SQLite database with persistence**
✅ **Mobile number uniqueness (8 digits)**
✅ **Email uniqueness validation**
✅ **Container-ready deployment**
✅ **Data persistence with volumes**