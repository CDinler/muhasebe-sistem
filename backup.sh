#!/bin/bash

# Database Backup Script for Muhasebe System
# Run this script regularly using cron (e.g., daily at 2 AM)

# Configuration
BACKUP_DIR="/var/backups/muhasebe-sistem"
DB_CONTAINER="muhasebe-db"
DB_USER="${DB_USER:-muhasebe_user}"
DB_NAME="${DB_NAME:-muhasebe_db}"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/muhasebe_backup_$TIMESTAMP.sql.gz"

# Create backup
echo "Starting database backup..."
docker exec -t "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup size: $SIZE"
else
    echo "Backup failed!"
    exit 1
fi

# Remove old backups (older than RETENTION_DAYS)
echo "Removing backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "muhasebe_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully!"

# Optional: Upload to cloud storage (uncomment if using)
# aws s3 cp "$BACKUP_FILE" s3://your-bucket/backups/
# rclone copy "$BACKUP_FILE" remote:backups/
