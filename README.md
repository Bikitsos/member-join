# Member Registration Application

A modern web-based member registration form built with NiceGUI, Python 3.12, and SQLite database.

## 🌟 Features

- ✅ **Clean Web Interface**: Modern, responsive registration form
- ✅ **Required Field Validation**: Name, Surname, Mobile (8 digits), Email
- ✅ **Real-time Validation**: Instant feedback on form errors
- ✅ **Duplicate Prevention**: Unique email and mobile number enforcement
- ✅ **SQLite Database**: Persistent data storage with automatic timestamps
- ✅ **Container Ready**: Podman/Docker deployment support
- ✅ **Member Viewer**: Command-line tool to view registered members

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Run the Application**:
   ```bash
   uv run main.py
   ```

3. **Access the Form**:
   - Open http://localhost:8085 in your browser

4. **View Registered Members**:
   ```bash
   uv run view_members.py
   ```

### Container Deployment

For deployment on other machines using Podman/Docker:

1. **Quick Start with Management Script**:
   ```bash
   chmod +x manage.sh
   ./manage.sh build
   ./manage.sh start
   ```

2. **Access the Application**:
   - Local: http://localhost:8085
   - Network: http://YOUR_SERVER_IP:8085

3. **View Members**:
   ```bash
   ./manage.sh members
   ```

📖 **Full container deployment guide**: See [CONTAINER_DEPLOYMENT.md](CONTAINER_DEPLOYMENT.md)

## 📋 Form Validation Rules

### Required Fields
- **Name**: Cannot be empty
- **Surname**: Cannot be empty
- **Mobile Number**: Exactly 8 digits (spaces/dashes allowed, stored clean)
- **Email**: Valid email format (name@domain.com)

### Uniqueness Constraints
- **Email**: Must be unique across all registrations
- **Mobile**: Must be unique across all registrations

### Validation Messages
- `"Name is required"` - Missing name
- `"Surname is required"` - Missing surname
- `"Mobile number is required"` - Missing mobile
- `"Invalid mobile number format"` - Not exactly 8 digits
- `"Email is required"` - Missing email
- `"Invalid email format"` - Invalid email format
- `"Mobile number is already registered"` - Duplicate mobile
- `"Email is already registered"` - Duplicate email

## 🗄️ Database Schema

```sql
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    mobile TEXT NOT NULL,           -- Stored as clean 8 digits
    email TEXT NOT NULL,            -- Stored lowercase
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unique indexes for duplicate prevention
CREATE UNIQUE INDEX idx_members_email ON members(email);
CREATE UNIQUE INDEX idx_members_mobile ON members(mobile);
```

## 📁 Project Structure

```
member-join/
├── main.py                    # Main web application
├── view_members.py           # Member viewer utility
├── pyproject.toml           # Python dependencies
├── members.db              # SQLite database (auto-created)
├── Dockerfile             # Container configuration
├── manage.sh             # Container management script
├── CONTAINER_DEPLOYMENT.md  # Deployment guide
├── .gitignore           # Git ignore patterns
└── README.md           # This file
```

## 🛠️ Development

### Adding New Features

1. **Database Changes**: Update `init_database()` function
2. **Form Fields**: Modify `create_member_form()` function
3. **Validation**: Update `submit_form()` function
4. **Styling**: Modify CSS in `main()` function

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `members.db` | SQLite database file path |
| `HOST` | `localhost` | Host to bind to (`0.0.0.0` for containers) |
| `SHOW_BROWSER` | `true` | Auto-open browser on start |

### Container Management

Use the provided `manage.sh` script for easy container operations:

```bash
./manage.sh help      # Show all commands
./manage.sh build     # Build container image
./manage.sh start     # Start the application
./manage.sh status    # Check container status
./manage.sh logs      # View application logs
./manage.sh members   # View registered members
./manage.sh stop      # Stop the application
./manage.sh clean     # Clean up resources
```

## 🧪 Testing

### Manual Testing Scenarios

1. **Valid Registration**:
   - Fill all fields with valid data
   - Should show success message and clear form

2. **Validation Errors**:
   - Leave fields empty → Required field errors
   - Invalid email → Email format error
   - Mobile not 8 digits → Format error

3. **Duplicate Prevention**:
   - Register same email twice → Duplicate email error
   - Register same mobile twice → Duplicate mobile error

4. **Mobile Number Formats**:
   - `12345678` → Valid
   - `1234-5678` → Valid (cleaned to `12345678`)
   - `1234 5678` → Valid (cleaned to `12345678`)
   - `123456789` → Invalid (9 digits)

## 🔧 Technologies Used

- **Python 3.12**: Programming language
- **NiceGUI**: Modern Python web UI framework
- **SQLite**: Embedded database
- **FastAPI**: Web framework (via NiceGUI)
- **uv**: Fast Python package manager
- **Podman/Docker**: Containerization

## 📊 Database Operations

### View All Members
```bash
uv run view_members.py
```

### Database File Location
- **Local**: `members.db` (project root)
- **Container**: `/app/data/members.db` (persistent volume)

### Backup Database
```bash
# Local
cp members.db backup-$(date +%Y%m%d).db

# Container
podman cp member-app:/app/data/members.db backup-$(date +%Y%m%d).db
```

## 🚀 Production Deployment

### Security Considerations
- Use reverse proxy (nginx) for SSL/TLS
- Set up firewall rules for port 8085
- Configure log rotation
- Use secrets for sensitive configuration
- Set resource limits for containers

### Monitoring
```bash
# Check application logs
./manage.sh logs

# Monitor container resources
podman stats member-app

# Check database size
ls -lh members.db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

## 🔗 Related Files

- [CONTAINER_DEPLOYMENT.md](CONTAINER_DEPLOYMENT.md) - Complete container deployment guide
- [manage.sh](manage.sh) - Container management script
- [Dockerfile](Dockerfile) - Container configuration