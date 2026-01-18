#!/bin/bash

# Docker Management Script
# This script provides common Docker operations for development and deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        exit 1
    fi
}

# Function to build image
build_image() {
    local image_name=$1
    local dockerfile=${2:-"Dockerfile"}
    local context=${3:-"."}

    print_info "Building Docker image: $image_name"
    docker build -f "$dockerfile" -t "$image_name" "$context"
    print_success "Image built successfully: $image_name"
}

# Function to run container
run_container() {
    local image_name=$1
    local container_name=${2:-$(basename "$image_name")}
    local port_mapping=$3

    print_info "Running container: $container_name from image: $image_name"

    local cmd="docker run -d --name $container_name"
    if [ -n "$port_mapping" ]; then
        cmd="$cmd -p $port_mapping"
    fi
    cmd="$cmd $image_name"

    eval "$cmd"
    print_success "Container started: $container_name"
}

# Function to stop and remove container
cleanup_container() {
    local container_name=$1

    print_info "Stopping and removing container: $container_name"
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    print_success "Container cleaned up: $container_name"
}

# Function to show container logs
show_logs() {
    local container_name=$1
    local follow=${2:-false}

    if [ "$follow" = true ]; then
        print_info "Following logs for container: $container_name"
        docker logs -f "$container_name"
    else
        print_info "Showing logs for container: $container_name"
        docker logs "$container_name"
    fi
}

# Function to list images
list_images() {
    print_info "Docker images:"
    docker images
}

# Function to list containers
list_containers() {
    print_info "Running containers:"
    docker ps
    echo
    print_info "All containers:"
    docker ps -a
}

# Function to clean up unused resources
cleanup() {
    print_info "Cleaning up unused Docker resources..."
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show usage
usage() {
    echo "Docker Management Script"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  build IMAGE_NAME [DOCKERFILE] [CONTEXT]    Build Docker image"
    echo "  run IMAGE_NAME [CONTAINER_NAME] [PORT]     Run container"
    echo "  stop CONTAINER_NAME                        Stop and remove container"
    echo "  logs CONTAINER_NAME [follow]               Show container logs"
    echo "  images                                     List Docker images"
    echo "  containers                                 List containers"
    echo "  cleanup                                    Clean up unused resources"
    echo "  help                                       Show this help"
    echo
    echo "Examples:"
    echo "  $0 build myapp:v1.0"
    echo "  $0 build myapp:v1.0 Dockerfile.dev ./src"
    echo "  $0 run myapp:v1.0 myapp-container 3000:3000"
    echo "  $0 logs myapp-container follow"
}

# Main script logic
main() {
    check_docker

    case "${1:-help}" in
        build)
            if [ -z "$2" ]; then
                print_error "Image name is required"
                usage
                exit 1
            fi
            build_image "$2" "$3" "$4"
            ;;
        run)
            if [ -z "$2" ]; then
                print_error "Image name is required"
                usage
                exit 1
            fi
            run_container "$2" "$3" "$4"
            ;;
        stop)
            if [ -z "$2" ]; then
                print_error "Container name is required"
                usage
                exit 1
            fi
            cleanup_container "$2"
            ;;
        logs)
            if [ -z "$2" ]; then
                print_error "Container name is required"
                usage
                exit 1
            fi
            show_logs "$2" "$3"
            ;;
        images)
            list_images
            ;;
        containers)
            list_containers
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"