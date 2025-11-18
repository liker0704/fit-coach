#!/bin/bash

# ============================================================================
# FitCoach Database Backup Script
# ============================================================================
# Description: Production-ready PostgreSQL backup script with compression,
#              rotation, error handling, and logging
# Usage: ./backup.sh [OPTIONS]
# Options:
#   -d, --destination DIR   Backup destination directory (default: ./backups)
#   -r, --retention DAYS    Retention period in days (default: 30)
#   -c, --container NAME    Docker container name (default: fitcoach-postgres)
#   -h, --help             Show this help message
# ============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ============================================================================
# Configuration
# ============================================================================

# Default values
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
CONTAINER_NAME="${CONTAINER_NAME:-fitcoach-postgres}"
LOG_FILE="${LOG_FILE:-./backups/backup.log}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="fitcoach_backup_${TIMESTAMP}.sql.gz"

# Load environment variables if .env.docker exists
if [ -f .env.docker ]; then
    source .env.docker
fi

# Database configuration
DB_NAME="${POSTGRES_DB:-fitcoach}"
DB_USER="${POSTGRES_USER:-fitcoach}"

# ============================================================================
# Functions
# ============================================================================

# Print colored output
log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE" >&2
}

log_warn() {
    echo -e "\033[0;33m[WARN]\033[0m $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Show help message
show_help() {
    sed -n '2,11p' "$0" | sed 's/^# //'
    exit 0
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        exit 1
    fi
    log_info "Docker is running"
}

# Check if container exists and is running
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Container '${CONTAINER_NAME}' is not running"
        exit 1
    fi
    log_info "Container '${CONTAINER_NAME}' is running"
}

# Create backup directory if it doesn't exist
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log_info "Created backup directory: $BACKUP_DIR"
    fi
}

# Perform database backup
perform_backup() {
    local backup_path="${BACKUP_DIR}/${BACKUP_NAME}"

    log_info "Starting backup of database '${DB_NAME}'"
    log_info "Backup file: ${backup_path}"

    # Execute pg_dump inside the container and compress
    if docker exec "$CONTAINER_NAME" pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=plain \
        --no-owner \
        --no-acl \
        --clean \
        --if-exists \
        | gzip > "$backup_path"; then

        local backup_size=$(du -h "$backup_path" | cut -f1)
        log_info "Backup completed successfully"
        log_info "Backup size: ${backup_size}"

        # Verify backup file
        if [ ! -s "$backup_path" ]; then
            log_error "Backup file is empty"
            return 1
        fi

        # Test gzip integrity
        if ! gzip -t "$backup_path" 2>/dev/null; then
            log_error "Backup file is corrupted"
            return 1
        fi

        log_info "Backup verification passed"
        return 0
    else
        log_error "Backup failed"
        return 1
    fi
}

# Rotate old backups
rotate_backups() {
    log_info "Rotating backups older than ${RETENTION_DAYS} days"

    local deleted_count=0
    while IFS= read -r -d '' file; do
        rm -f "$file"
        log_info "Deleted old backup: $(basename "$file")"
        ((deleted_count++))
    done < <(find "$BACKUP_DIR" -name "fitcoach_backup_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -print0)

    if [ $deleted_count -eq 0 ]; then
        log_info "No old backups to delete"
    else
        log_info "Deleted $deleted_count old backup(s)"
    fi
}

# List existing backups
list_backups() {
    log_info "Existing backups:"
    if [ -d "$BACKUP_DIR" ]; then
        local backup_count=$(find "$BACKUP_DIR" -name "fitcoach_backup_*.sql.gz" -type f 2>/dev/null | wc -l)
        if [ "$backup_count" -gt 0 ]; then
            find "$BACKUP_DIR" -name "fitcoach_backup_*.sql.gz" -type f -printf "%T@ %p\n" | \
                sort -rn | \
                while read timestamp file; do
                    local size=$(du -h "$file" | cut -f1)
                    local date=$(date -d "@${timestamp%.*}" '+%Y-%m-%d %H:%M:%S')
                    log_info "  - $(basename "$file") (${size}, ${date})"
                done
        else
            log_info "  No backups found"
        fi
    else
        log_info "  Backup directory does not exist"
    fi
}

# Cleanup on error
cleanup_on_error() {
    local backup_path="${BACKUP_DIR}/${BACKUP_NAME}"
    if [ -f "$backup_path" ]; then
        log_warn "Cleaning up failed backup: $backup_path"
        rm -f "$backup_path"
    fi
}

# ============================================================================
# Parse command line arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--destination)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# ============================================================================
# Main execution
# ============================================================================

main() {
    log_info "========================================="
    log_info "FitCoach Database Backup Started"
    log_info "========================================="

    # Pre-flight checks
    check_docker
    check_container
    create_backup_dir

    # Perform backup
    if perform_backup; then
        # Rotate old backups
        rotate_backups

        # List all backups
        list_backups

        log_info "========================================="
        log_info "Backup completed successfully"
        log_info "========================================="
        exit 0
    else
        cleanup_on_error
        log_error "========================================="
        log_error "Backup failed"
        log_error "========================================="
        exit 1
    fi
}

# Trap errors and cleanup
trap cleanup_on_error ERR

# Run main function
main
