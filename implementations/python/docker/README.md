# UPSS PostgreSQL Docker Setup

Production-grade PostgreSQL backend for the Universal Prompt Security Standard (UPSS) with complete monitoring, backup, and security features.

## Overview

This Docker setup provides:

- **PostgreSQL 16** with optimized configuration
- **Complete database schema** with UPSS tables, indexes, and security
- **Automated backups** with WAL archiving
- **Health monitoring** with comprehensive checks
- **pgAdmin 4** for database management
- **Prometheus metrics** via PostgreSQL Exporter
- **Row-Level Security (RLS)** for fine-grained access control
- **Immutable audit logs** for compliance

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB available RAM
- 10GB available disk space

### Setup

1. **Clone the repository** (if not already done):
   ```bash
   cd implementations/python
   ```

2. **Copy environment file**:
   ```bash
   cp docker/.env.example docker/.env
   ```

3. **Edit `.env` file** and change default passwords:
   ```bash
   # REQUIRED: Change these values!
   POSTGRES_PASSWORD=your_secure_password_here
   PGADMIN_PASSWORD=your_pgadmin_password_here
   ```

4. **Start services**:
   ```bash
   cd docker
   docker-compose up -d
   ```

5. **Verify health**:
   ```bash
   docker-compose ps
   docker-compose logs postgres
   ```

6. **Check database initialization**:
   ```bash
   docker-compose exec postgres psql -U upss -d upss -c "\dt upss.*"
   ```

## Services

### PostgreSQL (port 5432)

Main database service with:
- UPSS schema and tables
- Row-level security
- Optimized configuration
- Health checks every 30s
- Automated backups

**Connect**:
```bash
psql -h localhost -p 5432 -U upss -d upss
```

**Connection string**:
```
postgresql://upss:changeme@localhost:5432/upss
```

### pgAdmin (port 5050)

Web-based database management interface.

**Access**: http://localhost:5050

**Default credentials**:
- Email: `admin@upss.local`
- Password: `admin` (change in `.env`)

### PostgreSQL Exporter (port 9187)

Prometheus metrics exporter for monitoring.

**Metrics**: http://localhost:9187/metrics

Exposes:
- Standard PostgreSQL metrics
- UPSS-specific metrics (prompts, audit events, security)
- Database performance metrics

### Backup Service

Automated daily backups at 2 AM UTC.

**Manual backup**:
```bash
docker-compose exec postgres /usr/local/bin/backup.sh full
```

**List backups**:
```bash
docker-compose exec postgres /usr/local/bin/backup.sh list
```

**Verify backup**:
```bash
docker-compose exec postgres /usr/local/bin/backup.sh verify /backups/full/upss_backup_20250130_020000.sql.gz
```

## Database Schema

### Tables

| Table | Purpose | Features |
|-------|---------|----------|
| `upss.prompts` | Prompt metadata and content references | RLS enabled, checksums, versioning |
| `upss.prompt_versions` | Version tracking | Latest version pointers |
| `upss.audit_logs` | Immutable audit trail | Append-only, automatic timestamps |
| `upss.user_roles` | User role assignments | Time-limited access support |
| `upss.role_permissions` | Role permission definitions | Resource pattern matching |
| `upss.prompt_permissions` | Fine-grained access control | Per-prompt permissions |

### Default Roles

| Role | Permissions | Description |
|------|------------|-------------|
| `reader` | read | Read-only access to prompts |
| `writer` | read, write | Create and modify prompts |
| `approver` | read, write, approve | Approve prompts for production |
| `admin` | all | Full system access |
| `auditor` | read, audit | Audit log access only |

## Configuration

### PostgreSQL Settings

Located in `docker/postgres/config/postgresql.conf`:

- **Memory**: 256MB shared buffers, 1GB effective cache
- **Connections**: Max 200 connections
- **WAL**: Replication-ready with compression
- **Logging**: Query performance tracking (>1s queries logged)
- **Security**: SCRAM-SHA-256 password encryption
- **Autovacuum**: Optimized for write-heavy workloads

### Environment Variables

See `docker/.env.example` for all configurable options.

Key variables:
```bash
POSTGRES_DB=upss                    # Database name
POSTGRES_USER=upss                  # Database user
POSTGRES_PASSWORD=changeme          # Database password (CHANGE!)
POSTGRES_PORT=5432                  # External port
BACKUP_RETENTION_DAYS=7             # Backup retention period
```

## Usage with UPSS Python Library

### Installation

```bash
pip install upss[postgresql]
```

### Configuration

```python
from upss import UPSSClient

# Connect to PostgreSQL backend
client = UPSSClient(
    mode="postgresql",
    db_url="postgresql://upss:changeme@localhost:5432/upss",
    enable_rbac=True,
    enable_checksum=True
)

# Use the client
async with client:
    prompt = await client.load("assistant", user_id="user@example.com")
    print(prompt.content)
```

### Environment Variables

```bash
export UPSS_MODE=postgresql
export UPSS_DB_URL=postgresql://upss:changeme@localhost:5432/upss
export UPSS_ENABLE_RBAC=true
```

## Security Features

### 1. Row-Level Security (RLS)

Enforces access control at the database level:

```sql
-- Example: User can only read prompts they have access to
SELECT * FROM upss.prompts WHERE name = 'secret-prompt';
-- Returns results only if user has permission
```

### 2. Immutable Audit Logs

Audit logs cannot be modified or deleted:

```sql
-- This will fail
UPDATE upss.audit_logs SET success = true WHERE id = '...';
-- ERROR: Audit logs are immutable
```

### 3. Checksum Verification

All prompts have SHA-256 checksums:

```sql
SELECT name, version, checksum FROM upss.prompts;
```

### 4. Role-Based Access Control

Granular permissions:

```sql
-- Grant reader role to user
INSERT INTO upss.user_roles (user_id, role_name, granted_by)
VALUES ('user@example.com', 'reader', 'admin@example.com');
```

### 5. SSL/TLS Support

Enable in production (uncomment in `postgresql.conf`):

```conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/root.crt'
```

## Monitoring

### Health Checks

Automated health checks run every 30 seconds:

```bash
# Manual health check
docker-compose exec postgres /usr/local/bin/healthcheck.sh
```

Checks performed:
- ✓ PostgreSQL accepting connections
- ✓ Can execute queries
- ✓ UPSS schema exists
- ✓ All required tables present
- ✓ Database writeable
- ✓ Connection usage
- ✓ Disk space
- ✓ Long-running transactions
- ✓ Lock contention

### Metrics

Prometheus-compatible metrics at http://localhost:9187/metrics

**UPSS-specific metrics**:
- `upss_prompts{category,risk_level}` - Prompt counts by category/risk
- `upss_audit_events{event_type,success}` - Audit events per hour
- `upss_user_roles{role_name}` - Active users per role
- `upss_failed_access` - Failed access attempts
- `upss_integrity_failures` - Checksum failures
- `upss_injection_attempts` - Detected injection attempts

### Logs

View logs:
```bash
# All services
docker-compose logs -f

# PostgreSQL only
docker-compose logs -f postgres

# Follow query logs
docker-compose exec postgres tail -f /var/log/postgresql/postgresql-*.log
```

## Backup and Recovery

### Automated Backups

Backups run daily at 2 AM UTC:
- Full database dump (compressed)
- Schema-only dump
- WAL continuous archiving
- 7-day retention (configurable)

### Manual Backup

**Full backup**:
```bash
docker-compose exec postgres /usr/local/bin/backup.sh full
```

**Schema only**:
```bash
docker-compose exec postgres /usr/local/bin/backup.sh schema
```

### Restore from Backup

1. **Stop the application**:
   ```bash
   docker-compose stop postgres
   ```

2. **Restore database**:
   ```bash
   # Copy backup to container
   docker-compose run postgres sh -c \
     "gunzip -c /backups/full/upss_backup_YYYYMMDD_HHMMSS.sql.gz | \
      psql -U upss -d upss"
   ```

3. **Restart services**:
   ```bash
   docker-compose start postgres
   ```

### Point-in-Time Recovery (PITR)

Uses WAL archiving for recovery to specific timestamp:

```bash
# Restore to specific time
docker-compose exec postgres pg_restore \
  --target-time='2025-01-30 14:30:00' \
  /backups/full/upss_backup_latest.sql.gz
```

## Performance Tuning

### Resource Allocation

Adjust in `docker-compose.yml`:

```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Configuration Tuning

Edit `docker/postgres/config/postgresql.conf`:

```conf
# For 4GB RAM system
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 16MB
maintenance_work_mem = 256MB
```

### Connection Pooling

For production, use PgBouncer:

```bash
# Add to docker-compose.yml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  environment:
    DATABASES_HOST: postgres
    DATABASES_PORT: 5432
    DATABASES_DATABASE: upss
    DATABASES_USER: upss
    PGBOUNCER_POOL_MODE: transaction
    PGBOUNCER_MAX_CLIENT_CONN: 1000
    PGBOUNCER_DEFAULT_POOL_SIZE: 25
```

## Troubleshooting

### Connection Refused

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Verify network
docker network ls | grep upss
```

### Disk Space Issues

```bash
# Check disk usage
docker-compose exec postgres df -h

# Clean old backups
docker-compose exec postgres /usr/local/bin/backup.sh cleanup

# Vacuum database
docker-compose exec postgres psql -U upss -d upss -c "VACUUM FULL;"
```

### Performance Issues

```bash
# Check active queries
docker-compose exec postgres psql -U upss -d upss -c \
  "SELECT pid, usename, query, state FROM pg_stat_activity WHERE state != 'idle';"

# Check locks
docker-compose exec postgres psql -U upss -d upss -c \
  "SELECT * FROM pg_locks WHERE NOT granted;"

# Analyze slow queries
docker-compose exec postgres psql -U upss -d upss -c \
  "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Reset Database

**⚠️ WARNING: This deletes all data!**

```bash
# Stop services
docker-compose down

# Remove volumes
docker volume rm upss-postgres-data upss-postgres-backups

# Restart
docker-compose up -d
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up automated backups to external storage
- [ ] Configure log rotation
- [ ] Enable monitoring and alerting
- [ ] Review and adjust resource limits
- [ ] Set up replication for high availability
- [ ] Configure regular security updates
- [ ] Document disaster recovery procedures

### Recommended Setup

1. **Use external volumes** for data persistence
2. **Enable SSL** for all connections
3. **Set up replication** for high availability
4. **Configure monitoring** (Prometheus + Grafana)
5. **Implement backup rotation** to S3/cloud storage
6. **Use secrets management** (Docker Secrets, Vault)
7. **Set resource limits** based on workload
8. **Enable query logging** for audit trail
9. **Configure automatic updates** for security patches
10. **Test disaster recovery** procedures regularly

## Support

For issues or questions:
- GitHub Issues: https://github.com/alvinveroy/prompt-security-standard/issues
- Documentation: https://github.com/alvinveroy/prompt-security-standard
- Security: See SECURITY.md

## License

MIT License - see LICENSE file for details.
