#!/bin/bash

# ============================================================================
# FitCoach Database Restore Script
# ============================================================================
# Description: Production-ready PostgreSQL restore script with safety checks,
#              error handling, and logging
# Usage: ./restore.sh BACKUP_FILE [OPTIONS]
# Options:
#   -c, --container NAME    Docker container name (default: fitcoach-postgres)
#   -f, --force            Skip confirmation prompt
#   -h, --help             Show this help message
# ============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ============================================================================
# Configuration
# ============================================================================

# Default values
CONTAINER_NAME="${CONTAINER_NAME:-fitcoach-postgres}"
LOG_FILE="${LOG_FILE:-./backups/restore.log}"
FORCE=false
BACKUP_FILE=""

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
    sed -n '2,9p' "$0" | sed 's/^# //'
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

# Validate backup file
validate_backup_file() {
    if [ -z "$BACKUP_FILE" ]; then
        log_error "No backup file specified"
        show_help
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    # Check if file is gzipped
    if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
        log_error "Backup file is not a valid gzip file or is corrupted"
        exit 1
    fi

    local file_size=$(du -h "$BACKUP_FILE" | cut -f1)
    log_info "Backup file validated: $BACKUP_FILE (${file_size})"
}

# Create pre-restore backup
create_pre_restore_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local pre_restore_backup="./backups/pre_restore_${timestamp}.sql.gz"

    log_warn "Creating pre-restore backup as safety measure"
    log_info "Pre-restore backup: $pre_restore_backup"

    mkdir -p ./backups

    if docker exec "$CONTAINER_NAME" pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=plain \
        --no-owner \
        --no-acl \
        | gzip > "$pre_restore_backup"; then

        local backup_size=$(du -h "$pre_restore_backup" | cut -f1)
        log_info "Pre-restore backup created successfully (${backup_size})"
        echo "$pre_restore_backup"
        return 0
    else
        log_error "Failed to create pre-restore backup"
        return 1
    fi
}

# Terminate active connections
terminate_connections() {
    log_info "Terminating active database connections"

    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" \
        >/dev/null 2>&1 || true

    log_info "Active connections terminated"
}

# Perform database restore
perform_restore() {
    log_info "Starting database restore"
    log_info "Database: ${DB_NAME}"
    log_info "Backup file: ${BACKUP_FILE}"

    # Decompress and restore
    if gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" psql \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --single-transaction \
        --set ON_ERROR_STOP=on \
        >/dev/null 2>&1; then

        log_info "Database restore completed successfully"
        return 0
    else
        log_error "Database restore failed"
        return 1
    fi
}

# Verify database after restore
verify_restore() {
    log_info "Verifying database after restore"

    # Check if database is accessible
    if docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        log_info "Database is accessible"

        # Get table count
        local table_count=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c \
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        log_info "Tables in database: $(echo $table_count | tr -d ' ')"

        return 0
    else
        log_error "Database verification failed"
        return 1
    fi
}

# Confirmation prompt
confirm_restore() {
    if [ "$FORCE" = true ]; then
        return 0
    fi

    log_warn "========================================="
    log_warn "WARNING: This will overwrite the current database!"
    log_warn "Database: ${DB_NAME}"
    log_warn "Backup file: ${BACKUP_FILE}"
    log_warn "========================================="
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Restore cancelled by user"
        exit 0
    fi
}

# ============================================================================
# Parse command line arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
                shift
            else
                log_error "Unknown option: $1"
                show_help
            fi
            ;;
    esac
done

# ============================================================================
# Main execution
# ============================================================================

main() {
    log_info "========================================="
    log_info "FitCoach Database Restore Started"
    log_info "========================================="

    # Pre-flight checks
    check_docker
    check_container
    validate_backup_file

    # Confirmation
    confirm_restore

    # Create pre-restore backup
    local pre_restore_backup
    if pre_restore_backup=$(create_pre_restore_backup); then
        log_info "Pre-restore backup saved: $pre_restore_backup"
    else
        log_error "Failed to create pre-restore backup. Aborting."
        exit 1
    fi

    # Terminate connections
    terminate_connections

    # Perform restore
    if perform_restore; then
        # Verify restore
        if verify_restore; then
            log_info "========================================="
            log_info "Restore completed successfully"
            log_info "Pre-restore backup: $pre_restore_backup"
            log_info "========================================="
            exit 0
        else
            log_error "Restore verification failed"
            log_error "Pre-restore backup available at: $pre_restore_backup"
            exit 1
        fi
    else
        log_error "========================================="
        log_error "Restore failed"
        log_error "Database may be in inconsistent state"
        log_error "Pre-restore backup available at: $pre_restore_backup"
        log_error "========================================="
        exit 1
    fi
}

# Run main function
main
