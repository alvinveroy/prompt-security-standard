#!/bin/sh
# PostgreSQL Backup Script for UPSS
# Supports both WAL archiving and full database backups

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DB_NAME="${POSTGRES_DB:-upss}"
DB_USER="${POSTGRES_USER:-upss}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR/wal" "$BACKUP_DIR/full" "$BACKUP_DIR/logs"

# Function: WAL Archive
archive_wal() {
    WAL_FILE="$1"
    WAL_NAME="$2"
    
    if [ -z "$WAL_FILE" ] || [ -z "$WAL_NAME" ]; then
        echo "ERROR: WAL file and name required"
        return 1
    fi
    
    # Copy WAL file to archive
    cp "$WAL_FILE" "$BACKUP_DIR/wal/$WAL_NAME"
    
    # Verify copy
    if [ -f "$BACKUP_DIR/wal/$WAL_NAME" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Archived WAL: $WAL_NAME" >> "$BACKUP_DIR/logs/wal_archive.log"
        return 0
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Failed to archive WAL: $WAL_NAME" >> "$BACKUP_DIR/logs/wal_archive.log"
        return 1
    fi
}

# Function: Full Database Backup
full_backup() {
    BACKUP_FILE="$BACKUP_DIR/full/upss_backup_${TIMESTAMP}.sql.gz"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting full backup..." >> "$BACKUP_DIR/logs/backup.log"
    
    # Create compressed backup
    if pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists | gzip > "$BACKUP_FILE"; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Full backup completed: $BACKUP_FILE ($BACKUP_SIZE)" >> "$BACKUP_DIR/logs/backup.log"
        
        # Create backup metadata
        cat > "${BACKUP_FILE}.meta" <<EOF
timestamp: $TIMESTAMP
database: $DB_NAME
size: $BACKUP_SIZE
type: full
EOF
        return 0
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Full backup failed" >> "$BACKUP_DIR/logs/backup.log"
        return 1
    fi
}

# Function: Schema-only backup
schema_backup() {
    BACKUP_FILE="$BACKUP_DIR/full/upss_schema_${TIMESTAMP}.sql"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting schema backup..." >> "$BACKUP_DIR/logs/backup.log"
    
    if pg_dump -U "$DB_USER" -d "$DB_NAME" --schema-only --schema=upss > "$BACKUP_FILE"; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Schema backup completed: $BACKUP_FILE" >> "$BACKUP_DIR/logs/backup.log"
        return 0
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Schema backup failed" >> "$BACKUP_DIR/logs/backup.log"
        return 1
    fi
}

# Function: Cleanup old backups
cleanup_old_backups() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleaning up backups older than $RETENTION_DAYS days..." >> "$BACKUP_DIR/logs/backup.log"
    
    # Remove old full backups
    find "$BACKUP_DIR/full" -name "upss_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/full" -name "upss_backup_*.sql.gz.meta" -mtime +$RETENTION_DAYS -delete
    
    # Remove old WAL files
    find "$BACKUP_DIR/wal" -type f -mtime +$RETENTION_DAYS -delete
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup completed" >> "$BACKUP_DIR/logs/backup.log"
}

# Function: Verify backup integrity
verify_backup() {
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "ERROR: Backup file not found: $BACKUP_FILE"
        return 1
    fi
    
    # Test decompression
    if gzip -t "$BACKUP_FILE" 2>/dev/null; then
        echo "Backup verification passed: $BACKUP_FILE"
        return 0
    else
        echo "ERROR: Backup verification failed: $BACKUP_FILE"
        return 1
    fi
}

# Function: List available backups
list_backups() {
    echo "=== Available Backups ==="
    echo ""
    echo "Full Backups:"
    ls -lh "$BACKUP_DIR/full"/upss_backup_*.sql.gz 2>/dev/null || echo "  No full backups found"
    echo ""
    echo "WAL Archives:"
    WAL_COUNT=$(find "$BACKUP_DIR/wal" -type f | wc -l)
    echo "  $WAL_COUNT WAL files archived"
}

# Main script logic
case "${1:-full}" in
    wal)
        # Called by PostgreSQL archive_command
        archive_wal "$2" "$3"
        ;;
    full)
        full_backup
        cleanup_old_backups
        ;;
    schema)
        schema_backup
        ;;
    verify)
        verify_backup "$2"
        ;;
    list)
        list_backups
        ;;
    cleanup)
        cleanup_old_backups
        ;;
    *)
        echo "Usage: $0 {wal|full|schema|verify|list|cleanup}"
        echo ""
        echo "Commands:"
        echo "  wal <file> <name>  - Archive WAL file (called by PostgreSQL)"
        echo "  full              - Create full database backup"
        echo "  schema            - Create schema-only backup"
        echo "  verify <file>     - Verify backup integrity"
        echo "  list              - List available backups"
        echo "  cleanup           - Remove old backups"
        exit 1
        ;;
esac
