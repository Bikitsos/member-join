#!/bin/bash

# Member Registration App - Container Management Script
# Usage: ./manage.sh [build|start|stop|restart|status|logs|clean|help]

set -e  # Exit on any error

# Configuration
IMAGE_NAME="member-registration"
CONTAINER_NAME="member-app"
VOLUME_NAME="member-data"
PORT="8085"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if podman is installed
check_podman() {
    if ! command -v podman &> /dev/null; then
        log_error "Podman is not installed. Please install Podman first."
        exit 1
    fi
}

# Build the container image
build_image() {
    log_info "Building container image: $IMAGE_NAME"
    
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile not found in current directory"
        exit 1
    fi
    
    podman build -t "$IMAGE_NAME" .
    log_success "Image built successfully: $IMAGE_NAME"
}

# Create volume if it doesn't exist
create_volume() {
    if ! podman volume exists "$VOLUME_NAME" 2>/dev/null; then
        log_info "Creating volume: $VOLUME_NAME"
        podman volume create "$VOLUME_NAME"
        log_success "Volume created: $VOLUME_NAME"
    else
        log_info "Volume already exists: $VOLUME_NAME"
    fi
}

# Start the container
start_container() {
    log_info "Starting container: $CONTAINER_NAME"
    
    # Check if container already exists
    if podman ps -a --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        # Container exists, just start it
        if podman ps --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
            log_warning "Container is already running"
            return
        else
            log_info "Starting existing container"
            podman start "$CONTAINER_NAME"
        fi
    else
        # Create and start new container
        create_volume
        log_info "Creating and starting new container"
        podman run -d \
            --name "$CONTAINER_NAME" \
            -p "$PORT:8085" \
            -v "$VOLUME_NAME:/app/data" \
            "$IMAGE_NAME"
    fi
    
    log_success "Container started successfully"
    log_info "Application available at: http://localhost:$PORT"
}

# Stop the container
stop_container() {
    log_info "Stopping container: $CONTAINER_NAME"
    
    if podman ps --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        podman stop "$CONTAINER_NAME"
        log_success "Container stopped successfully"
    else
        log_warning "Container is not running"
    fi
}

# Restart the container
restart_container() {
    log_info "Restarting container: $CONTAINER_NAME"
    stop_container
    sleep 2
    start_container
}

# Show container status
show_status() {
    log_info "Container Status:"
    echo ""
    
    # Check if container exists
    if podman ps -a --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        podman ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "Container '$CONTAINER_NAME' does not exist"
    fi
    
    echo ""
    log_info "Volume Status:"
    if podman volume exists "$VOLUME_NAME" 2>/dev/null; then
        podman volume ls --filter "name=$VOLUME_NAME"
    else
        echo "Volume '$VOLUME_NAME' does not exist"
    fi
}

# Show container logs
show_logs() {
    log_info "Showing logs for container: $CONTAINER_NAME"
    
    if podman ps -a --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        podman logs -f "$CONTAINER_NAME"
    else
        log_error "Container '$CONTAINER_NAME' does not exist"
    fi
}

# View registered members
view_members() {
    log_info "Viewing registered members"
    
    if podman ps --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        podman exec -it "$CONTAINER_NAME" python view_members.py
    else
        log_error "Container is not running. Start it first with: $0 start"
    fi
}

# Clean up (remove container, image, and optionally volume)
clean_up() {
    log_warning "This will remove the container and image"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Stop container if running
        if podman ps --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
            stop_container
        fi
        
        # Remove container
        if podman ps -a --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
            log_info "Removing container: $CONTAINER_NAME"
            podman rm "$CONTAINER_NAME"
        fi
        
        # Remove image
        if podman images --format "{{.Repository}}" | grep -q "^$IMAGE_NAME$"; then
            log_info "Removing image: $IMAGE_NAME"
            podman rmi "$IMAGE_NAME"
        fi
        
        # Ask about volume
        read -p "Also remove data volume? This will delete all member data! (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if podman volume exists "$VOLUME_NAME" 2>/dev/null; then
                log_info "Removing volume: $VOLUME_NAME"
                podman volume rm "$VOLUME_NAME"
            fi
        fi
        
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Show help
show_help() {
    echo "Member Registration App - Container Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the container image"
    echo "  start     Start the container (creates if doesn't exist)"
    echo "  stop      Stop the container"
    echo "  restart   Restart the container"
    echo "  status    Show container and volume status"
    echo "  logs      Show container logs (follow mode)"
    echo "  members   View registered members"
    echo "  clean     Remove container, image, and optionally data"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 start    # Build and start"
    echo "  $0 restart              # Restart the app"
    echo "  $0 members              # View member data"
    echo "  $0 logs                 # Monitor logs"
}

# Main script
main() {
    check_podman
    
    case "${1:-help}" in
        build)
            build_image
            ;;
        start)
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            restart_container
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        members)
            view_members
            ;;
        clean)
            clean_up
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"