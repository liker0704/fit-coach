# FitCoach Database Backup & Restore Guide

## Overview

This document describes the backup and restore strategy for the FitCoach PostgreSQL database. The solution includes automated backup scripts with compression, rotation, error handling, and comprehensive logging.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Backup Strategy](#backup-strategy)
- [Backup Script Usage](#backup-script-usage)
- [Restore Script Usage](#restore-script-usage)
- [Automated Backups](#automated-backups)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Recovery Scenarios](#recovery-scenarios)

---

## Prerequisites

### Required Software

- Docker and Docker Compose installed and running
- Bash shell (Linux/macOS/WSL)
- PostgreSQL client tools (included in Docker container)
- Sufficient disk space for backups

### Required Files

- `.env.docker` - Environment variables for database credentials
- `docker-compose.yml` - Docker Compose configuration
- `scripts/backup.sh` - Backup script
- `scripts/restore.sh` - Restore script

### Permissions

Ensure backup scripts are executable:

```bash
chmod +x scripts/backup.sh scripts/restore.sh
```

---

## Quick Start

### Create a Backup

```bash
cd /home/user/fit-coach
./scripts/backup.sh
```

### Restore from Backup

```bash
cd /home/user/fit-coach
./scripts/restore.sh backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## Backup Strategy

### Design Principles

1. **Automation**: Scheduled automated backups via cron
2. **Compression**: gzip compression to save disk space
3. **Rotation**: Automatic deletion of backups older than 30 days (configurable)
4. **Verification**: Integrity checks after backup creation
5. **Logging**: Comprehensive logging for audit and troubleshooting
6. **Safety**: Pre-restore backups before any restore operation

### Backup Frequency

Recommended backup schedule:

- **Production**: Every 6 hours + daily full backup
- **Staging**: Daily
- **Development**: Weekly or before major changes

### Retention Policy

Default retention: **30 days**

This can be customized using the `--retention` flag or `RETENTION_DAYS` environment variable.

### Storage Requirements

Estimate your storage needs:

- Typical compressed backup: 10-100 MB (depends on data volume)
- 30 days of backups (4x daily): ~12-120 GB
- Recommendation: Provision 2x estimated storage for safety

---

## Backup Script Usage

### Basic Usage

```bash
./scripts/backup.sh
```

### Command-Line Options

```bash
./scripts/backup.sh [OPTIONS]

Options:
  -d, --destination DIR   Backup destination directory (default: ./backups)
  -r, --retention DAYS    Retention period in days (default: 30)
  -c, --container NAME    Docker container name (default: fitcoach-postgres)
  -h, --help             Show help message
```

### Examples

#### Custom backup directory

```bash
./scripts/backup.sh --destination /mnt/backups/fitcoach
```

#### Custom retention period

```bash
./scripts/backup.sh --retention 60
```

#### Different container name

```bash
./scripts/backup.sh --container my-postgres-container
```

#### Combined options

```bash
./scripts/backup.sh \
  --destination /mnt/backups/fitcoach \
  --retention 60 \
  --container fitcoach-postgres
```

### Environment Variables

You can also configure via environment variables:

```bash
export BACKUP_DIR=/mnt/backups/fitcoach
export RETENTION_DAYS=60
export CONTAINER_NAME=fitcoach-postgres
./scripts/backup.sh
```

### Backup Process

The backup script performs the following steps:

1. **Verification**: Checks Docker is running and container is accessible
2. **Directory Setup**: Creates backup directory if it doesn't exist
3. **Backup Execution**: Runs `pg_dump` inside the container
4. **Compression**: Compresses output with gzip
5. **Verification**: Validates backup file integrity
6. **Rotation**: Removes backups older than retention period
7. **Logging**: Records all operations to log file

### Backup File Format

Backup files are named with timestamps:

```
fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz
```

Example:
```
fitcoach_backup_20251118_143022.sql.gz
```

---

## Restore Script Usage

### Basic Usage

```bash
./scripts/restore.sh BACKUP_FILE
```

### Command-Line Options

```bash
./scripts/restore.sh BACKUP_FILE [OPTIONS]

Options:
  -c, --container NAME    Docker container name (default: fitcoach-postgres)
  -f, --force            Skip confirmation prompt
  -h, --help             Show help message
```

### Examples

#### Interactive restore (with confirmation)

```bash
./scripts/restore.sh backups/fitcoach_backup_20251118_143022.sql.gz
```

#### Force restore (skip confirmation)

```bash
./scripts/restore.sh backups/fitcoach_backup_20251118_143022.sql.gz --force
```

#### Different container name

```bash
./scripts/restore.sh \
  backups/fitcoach_backup_20251118_143022.sql.gz \
  --container my-postgres-container
```

### Restore Process

The restore script performs the following steps:

1. **Verification**: Checks Docker, container, and backup file
2. **Pre-Restore Backup**: Creates safety backup of current database
3. **Confirmation**: Asks for user confirmation (unless `--force` used)
4. **Connection Termination**: Closes active database connections
5. **Restore Execution**: Restores database from backup file
6. **Verification**: Validates database accessibility after restore
7. **Logging**: Records all operations to log file

### Safety Features

- **Pre-Restore Backup**: Automatically creates a backup before restore
- **Confirmation Prompt**: Requires explicit confirmation (unless forced)
- **Transaction Safety**: Uses `--single-transaction` for atomic restore
- **Error Handling**: Stops on first error to prevent partial restores

---

## Automated Backups

### Setting Up Cron Jobs

#### Production Schedule (Every 6 hours)

```bash
# Edit crontab
crontab -e

# Add the following line (backs up at 00:00, 06:00, 12:00, 18:00)
0 */6 * * * cd /home/user/fit-coach && ./scripts/backup.sh >> /var/log/fitcoach-backup.log 2>&1
```

#### Daily Backup (1 AM)

```bash
# Edit crontab
crontab -e

# Add the following line
0 1 * * * cd /home/user/fit-coach && ./scripts/backup.sh >> /var/log/fitcoach-backup.log 2>&1
```

#### Weekly Backup (Sunday at 2 AM)

```bash
# Edit crontab
crontab -e

# Add the following line
0 2 * * 0 cd /home/user/fit-coach && ./scripts/backup.sh >> /var/log/fitcoach-backup.log 2>&1
```

### Systemd Timer (Alternative to Cron)

Create a systemd service and timer for more control:

#### Service File: `/etc/systemd/system/fitcoach-backup.service`

```ini
[Unit]
Description=FitCoach Database Backup
After=docker.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/home/user/fit-coach
ExecStart=/home/user/fit-coach/scripts/backup.sh
StandardOutput=journal
StandardError=journal
```

#### Timer File: `/etc/systemd/system/fitcoach-backup.timer`

```ini
[Unit]
Description=FitCoach Database Backup Timer
Requires=fitcoach-backup.service

[Timer]
OnCalendar=*-*-* 00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

#### Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable fitcoach-backup.timer
sudo systemctl start fitcoach-backup.timer

# Check status
sudo systemctl status fitcoach-backup.timer
```

---

## Best Practices

### 1. Off-Site Backups

**Critical**: Always maintain off-site backups for disaster recovery.

```bash
# Example: Copy to remote server via rsync
rsync -avz --delete \
  /home/user/fit-coach/backups/ \
  user@remote-server:/backup/fitcoach/

# Example: Upload to cloud storage (AWS S3)
aws s3 sync \
  /home/user/fit-coach/backups/ \
  s3://my-backup-bucket/fitcoach-backups/
```

### 2. Test Restore Regularly

Test your restore process monthly to ensure backups are valid:

```bash
# 1. Create a test environment
docker-compose -f docker-compose.test.yml up -d

# 2. Restore to test database
./scripts/restore.sh backups/latest_backup.sql.gz --force

# 3. Verify data integrity
# 4. Clean up test environment
```

### 3. Monitor Backup Success

Set up monitoring and alerts:

```bash
# Check last backup age
find backups/ -name "fitcoach_backup_*.sql.gz" -mtime -1 -type f | wc -l

# Alert if no backup in last 24 hours
if [ $(find backups/ -name "fitcoach_backup_*.sql.gz" -mtime -1 -type f | wc -l) -eq 0 ]; then
  echo "WARNING: No backup in last 24 hours!" | mail -s "Backup Alert" admin@fitcoach.com
fi
```

### 4. Secure Backup Storage

- Store backups on encrypted file systems
- Restrict file permissions: `chmod 600 backups/*.gz`
- Use separate storage volumes/disks
- Implement access control (IAM, RBAC)

### 5. Document Recovery Procedures

- Keep this document accessible
- Document custom configurations
- Maintain contact list for emergencies
- Practice recovery drills

---

## Troubleshooting

### Common Issues

#### 1. Docker Not Running

**Error**: `Docker is not running or not accessible`

**Solution**:
```bash
# Check Docker status
docker info

# Start Docker (if stopped)
sudo systemctl start docker

# Check container status
docker ps
```

#### 2. Container Not Found

**Error**: `Container 'fitcoach-postgres' is not running`

**Solution**:
```bash
# List running containers
docker ps

# Start container
docker-compose up -d postgres

# Check container name
docker ps --format '{{.Names}}'
```

#### 3. Backup File Corrupted

**Error**: `Backup file is not a valid gzip file or is corrupted`

**Solution**:
```bash
# Test gzip integrity
gzip -t backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz

# If corrupted, use a different backup
ls -lth backups/
```

#### 4. Insufficient Disk Space

**Error**: Backup fails with no error message

**Solution**:
```bash
# Check disk space
df -h

# Clean up old backups manually
find backups/ -name "fitcoach_backup_*.sql.gz" -mtime +30 -delete

# Increase retention period
./scripts/backup.sh --retention 15
```

#### 5. Permission Denied

**Error**: `Permission denied` when running scripts

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/backup.sh scripts/restore.sh

# Check file ownership
ls -l scripts/

# Fix ownership if needed
sudo chown $USER:$USER scripts/*.sh
```

### Log Files

Check log files for detailed error information:

```bash
# Backup logs
cat backups/backup.log

# Restore logs
cat backups/restore.log

# Docker logs
docker logs fitcoach-postgres

# Tail logs in real-time
tail -f backups/backup.log
```

---

## Recovery Scenarios

### Scenario 1: Accidental Data Deletion

**Situation**: User accidentally deleted data

**Recovery Steps**:

1. Identify the last good backup (before deletion)
2. Stop the application to prevent further changes
3. Restore from backup
4. Verify data integrity
5. Restart application

```bash
# Stop application
docker-compose down

# Restore backup
./scripts/restore.sh backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz --force

# Verify data
docker-compose up -d postgres
# Connect and check data...

# Start application
docker-compose up -d
```

### Scenario 2: Database Corruption

**Situation**: Database files are corrupted

**Recovery Steps**:

1. Stop the database container
2. Remove corrupted data volume
3. Restore from latest backup
4. Restart services

```bash
# Stop all services
docker-compose down

# Remove corrupted volume
docker volume rm fitcoach_postgres_data

# Recreate database
docker-compose up -d postgres

# Wait for database to initialize
sleep 30

# Restore from backup
./scripts/restore.sh backups/latest_backup.sql.gz --force

# Start all services
docker-compose up -d
```

### Scenario 3: Server Failure / Migration

**Situation**: Moving to a new server or recovering from hardware failure

**Recovery Steps**:

1. Install Docker and dependencies on new server
2. Copy docker-compose.yml and .env.docker
3. Copy backup files
4. Start database container
5. Restore from backup
6. Start application

```bash
# On new server
# 1. Install Docker
sudo apt-get update && sudo apt-get install docker.io docker-compose

# 2. Clone repository or copy files
git clone <repository>

# 3. Copy backup files
scp -r user@old-server:/home/user/fit-coach/backups ./

# 4. Start database
docker-compose up -d postgres

# 5. Restore
./scripts/restore.sh backups/latest_backup.sql.gz --force

# 6. Start application
docker-compose up -d
```

### Scenario 4: Point-in-Time Recovery

**Situation**: Need to recover to a specific point in time

**Recovery Steps**:

1. Identify backup closest to desired time
2. Create test environment
3. Restore backup
4. Verify data matches expected state
5. Apply to production if correct

```bash
# List available backups
ls -lth backups/

# Restore to test environment
docker-compose -f docker-compose.test.yml up -d
./scripts/restore.sh backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz --force --container fitcoach-postgres-test

# Verify data, then apply to production
```

---

## Security Considerations

### Backup Security

1. **Encryption**: Encrypt backups at rest
   ```bash
   # Encrypt backup
   gpg --symmetric --cipher-algo AES256 backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz

   # Decrypt backup
   gpg --decrypt backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz.gpg > backup.sql.gz
   ```

2. **Access Control**: Restrict access to backup files
   ```bash
   chmod 600 backups/*.gz
   chown backup-user:backup-group backups/*.gz
   ```

3. **Secure Transfer**: Use encrypted channels for backup transfers
   ```bash
   # Use SCP or SFTP instead of FTP
   scp backups/*.gz user@backup-server:/secure/location/
   ```

### Credential Management

- Never hardcode credentials in scripts
- Use `.env.docker` for all sensitive variables
- Ensure `.env.docker` is in `.gitignore`
- Rotate credentials regularly
- Use strong passwords (minimum 16 characters)

---

## Monitoring & Alerts

### Backup Monitoring Script

Create a monitoring script to check backup health:

```bash
#!/bin/bash
# backup-monitor.sh

BACKUP_DIR="/home/user/fit-coach/backups"
MAX_AGE_HOURS=24

latest_backup=$(find "$BACKUP_DIR" -name "fitcoach_backup_*.sql.gz" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2)

if [ -z "$latest_backup" ]; then
    echo "CRITICAL: No backups found!"
    exit 2
fi

backup_age_seconds=$(( $(date +%s) - $(stat -c %Y "$latest_backup") ))
backup_age_hours=$(( backup_age_seconds / 3600 ))

if [ $backup_age_hours -gt $MAX_AGE_HOURS ]; then
    echo "WARNING: Latest backup is $backup_age_hours hours old (threshold: $MAX_AGE_HOURS hours)"
    exit 1
else
    echo "OK: Latest backup is $backup_age_hours hours old"
    exit 0
fi
```

### Integration with Monitoring Tools

- **Prometheus**: Export backup metrics
- **Nagios/Icinga**: Use backup-monitor.sh as check script
- **Email Alerts**: Send notifications on backup failures
- **Slack/Discord**: Integrate with chat platforms for notifications

---

## Additional Resources

### Related Documentation

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [FitCoach Architecture](./architecture/)

### Support

For issues or questions:

- GitHub Issues: [Repository URL]
- Documentation: [Wiki URL]
- Team Contact: [Email]

---

## Changelog

### Version 1.0.0 (2025-11-18)

- Initial backup and restore scripts
- Automated rotation policy
- Comprehensive documentation
- Security best practices
- Recovery scenarios

---

## License

This backup strategy is part of the FitCoach project and subject to the project's license.
