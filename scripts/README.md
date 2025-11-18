# FitCoach Backup Scripts

This directory contains production-ready backup and restore scripts for the FitCoach PostgreSQL database.

## Quick Start

### Initial Setup

```bash
# 1. Ensure Docker is running
docker-compose up -d

# 2. Configure environment variables
cp ../.env.docker.example ../.env.docker
# Edit .env.docker with secure passwords

# 3. Make scripts executable (if not already)
chmod +x backup.sh restore.sh
```

### Create a Backup

```bash
./backup.sh
```

### Restore from Backup

```bash
# List available backups
ls -lth ../backups/

# Restore (with confirmation prompt)
./restore.sh ../backups/fitcoach_backup_YYYYMMDD_HHMMSS.sql.gz
```

## Scripts

### backup.sh

Production-ready backup script with:
- gzip compression
- 30-day rotation
- Integrity verification
- Error handling
- Comprehensive logging

**Options:**
```bash
-d, --destination DIR   Backup directory (default: ./backups)
-r, --retention DAYS    Retention period (default: 30)
-c, --container NAME    Container name (default: fitcoach-postgres)
-h, --help             Show help
```

### restore.sh

Production-ready restore script with:
- Pre-restore safety backup
- Confirmation prompt
- Connection termination
- Integrity verification
- Error handling

**Options:**
```bash
-c, --container NAME    Container name (default: fitcoach-postgres)
-f, --force            Skip confirmation
-h, --help             Show help
```

## Automated Backups

### Using Cron (Recommended)

Add to crontab for automatic backups:

```bash
# Edit crontab
crontab -e

# Daily backup at 1 AM
0 1 * * * cd /home/user/fit-coach && ./scripts/backup.sh >> /var/log/fitcoach-backup.log 2>&1

# Every 6 hours
0 */6 * * * cd /home/user/fit-coach && ./scripts/backup.sh >> /var/log/fitcoach-backup.log 2>&1
```

## Documentation

For complete documentation, see [docs/BACKUP.md](../docs/BACKUP.md)

Topics covered:
- Backup strategy
- Restore procedures
- Best practices
- Troubleshooting
- Recovery scenarios
- Security considerations

## Support

- Documentation: [docs/BACKUP.md](../docs/BACKUP.md)
- Issues: [GitHub Issues]
