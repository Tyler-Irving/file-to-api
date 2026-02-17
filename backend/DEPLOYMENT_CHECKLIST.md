# Production Deployment Checklist

Complete checklist for deploying File-to-API Platform to production.

---

## Pre-Deployment

### Security

- [ ] Generate new `SECRET_KEY` (never use development key in production)
- [ ] Generate new `API_KEY_SALT`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Set `CORS_ALLOWED_ORIGINS` to your frontend domain only
- [ ] Review all `.env` variables
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Remove any test/debug code
- [ ] Review file upload limits (`MAX_UPLOAD_SIZE`)

### Database

- [ ] Decide: SQLite or PostgreSQL?
- [ ] If PostgreSQL:
  - [ ] Install PostgreSQL server
  - [ ] Create database user
  - [ ] Create database
  - [ ] Set `DATABASE_URL` in `.env`
  - [ ] Update `settings.py` to use `dj-database-url`
- [ ] If SQLite:
  - [ ] Ensure disk space for growth
  - [ ] Configure backup strategy
  - [ ] WAL mode enabled in settings

### Static Files

- [ ] Run `python manage.py collectstatic`
- [ ] Verify static files collected to `staticfiles/`
- [ ] Configure Nginx/Apache to serve static files
- [ ] Test static file access

### Dependencies

- [ ] Review `requirements.txt`
- [ ] Check for security vulnerabilities: `pip audit` or `safety check`
- [ ] Pin all dependency versions
- [ ] Update outdated packages

---

## Server Setup

### System Requirements

- [ ] Python 3.10+ installed
- [ ] pip and virtualenv installed
- [ ] Nginx or Apache installed
- [ ] UFW/firewall configured
- [ ] SSL certificate obtained (Let's Encrypt)

### Application Deployment

- [ ] Clone repository to `/var/www/file-to-api/`
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Set correct file permissions
- [ ] Create `.env` file with production values
- [ ] Run migrations
- [ ] Collect static files
- [ ] Test application starts: `python manage.py check`

### Process Manager

- [ ] Create systemd service file (or use Supervisor)
- [ ] Configure Gunicorn with 2-4 workers per CPU core
- [ ] Set restart policy (always restart on failure)
- [ ] Enable service on boot
- [ ] Start service
- [ ] Verify service status

### Web Server

- [ ] Configure Nginx/Apache virtual host
- [ ] Set up proxy pass to Gunicorn socket
- [ ] Configure static file serving
- [ ] Set client_max_body_size (for file uploads)
- [ ] Enable gzip compression
- [ ] Configure request timeouts
- [ ] Test Nginx config: `nginx -t`
- [ ] Reload Nginx

### SSL/TLS

- [ ] Install Certbot
- [ ] Obtain SSL certificate
- [ ] Configure automatic renewal
- [ ] Test certificate renewal: `certbot renew --dry-run`
- [ ] Force HTTPS redirect in Nginx
- [ ] Test HTTPS access

---

## Security Hardening

### Application Level

- [ ] Set secure session cookie settings
- [ ] Configure CSRF protection
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Configure `SECURE_HSTS_SECONDS`
- [ ] Review rate limiting settings
- [ ] Test file upload validation
- [ ] Test API key authentication

### Server Level

- [ ] Disable root SSH login
- [ ] Use SSH keys only (disable password auth)
- [ ] Configure UFW firewall:
  - [ ] Allow SSH (22)
  - [ ] Allow HTTP (80)
  - [ ] Allow HTTPS (443)
  - [ ] Deny all other incoming
- [ ] Install fail2ban
- [ ] Keep system packages updated
- [ ] Configure automatic security updates

### Database

- [ ] Use strong database password
- [ ] Restrict database access to localhost only
- [ ] Regular backups configured
- [ ] Test backup restoration

---

## Monitoring & Logging

### Application Monitoring

- [ ] Configure Django logging to file
- [ ] Set up log rotation (logrotate)
- [ ] Monitor error rates
- [ ] Set up alerting (email/Slack/PagerDuty)
- [ ] Optional: Install Sentry for error tracking

### Server Monitoring

- [ ] Monitor disk space
- [ ] Monitor memory usage
- [ ] Monitor CPU usage
- [ ] Monitor network traffic
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)

### Performance Monitoring

- [ ] Enable query logging (temporarily)
- [ ] Identify slow endpoints
- [ ] Add database indexes as needed
- [ ] Monitor API response times
- [ ] Set performance baselines

---

## Backup Strategy

### Database Backups

- [ ] Set up automated daily backups
- [ ] Store backups off-server (S3, Dropbox, etc.)
- [ ] Test backup restoration
- [ ] Configure backup retention policy (e.g., keep 30 days)

### File Backups

- [ ] Backup uploaded files (`media/uploads/`)
- [ ] Backup database file if using SQLite
- [ ] Backup `.env` file (securely)

### Backup Script Example

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/filetoapi"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
python manage.py dumpdata > "$BACKUP_DIR/db_$DATE.json"

# Backup uploaded files
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" media/

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/db_$DATE.json" s3://your-bucket/backups/
aws s3 cp "$BACKUP_DIR/media_$DATE.tar.gz" s3://your-bucket/backups/

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete
```

- [ ] Create backup script
- [ ] Add to cron: `0 2 * * * /path/to/backup.sh`
- [ ] Test backup script execution

---

## Testing

### Functional Testing

- [ ] Test API key generation
- [ ] Test file upload (CSV)
- [ ] Test file upload (Excel)
- [ ] Test schema detection accuracy
- [ ] Test dynamic API access
- [ ] Test CRUD operations
- [ ] Test pagination
- [ ] Test filtering
- [ ] Test sorting
- [ ] Test OpenAPI docs access

### Security Testing

- [ ] Test authentication (valid key)
- [ ] Test authentication (invalid key)
- [ ] Test rate limiting
- [ ] Test file size limit
- [ ] Test file type validation
- [ ] Test SQL injection attempts
- [ ] Test XSS attempts
- [ ] Test CORS policy

### Load Testing

- [ ] Run load tests with expected traffic
- [ ] Identify bottlenecks
- [ ] Optimize slow queries
- [ ] Test concurrent file uploads
- [ ] Test concurrent API requests

---

## DNS & Domain

- [ ] Purchase domain name
- [ ] Configure DNS A record → server IP
- [ ] Configure DNS AAAA record (IPv6)
- [ ] Wait for DNS propagation (up to 48 hours)
- [ ] Test domain resolution: `nslookup yourdomain.com`

---

## Documentation

- [ ] Update README with production URL
- [ ] Document deployment process
- [ ] Document backup/restore procedure
- [ ] Document emergency procedures
- [ ] Create runbook for common issues
- [ ] Document API usage with examples

---

## Launch

### Pre-Launch

- [ ] Announce maintenance window (if replacing existing system)
- [ ] Notify users of new API endpoints
- [ ] Prepare rollback plan

### Launch

- [ ] Deploy to production
- [ ] Run smoke tests
- [ ] Monitor logs for errors
- [ ] Check resource usage

### Post-Launch

- [ ] Monitor error rates for 24 hours
- [ ] Check backup job execution
- [ ] Verify SSL auto-renewal scheduled
- [ ] Update status page (if any)
- [ ] Send launch announcement

---

## Post-Deployment Maintenance

### Daily

- [ ] Check error logs
- [ ] Monitor disk space
- [ ] Check backup job status

### Weekly

- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Review API usage patterns

### Monthly

- [ ] Update dependencies
- [ ] Review and rotate API keys if needed
- [ ] Audit user-uploaded datasets
- [ ] Check database size growth
- [ ] Review and optimize slow queries

### Quarterly

- [ ] Security audit
- [ ] Performance optimization review
- [ ] Backup restoration test
- [ ] Disaster recovery drill

---

## Emergency Procedures

### Application Down

1. Check systemd service status: `systemctl status filetoapi`
2. Check logs: `journalctl -u filetoapi -n 100`
3. Check Nginx status: `systemctl status nginx`
4. Check disk space: `df -h`
5. Restart services if needed
6. Investigate root cause

### Database Issues

1. Check database connection
2. Check disk space
3. Check database logs
4. Restore from backup if corrupted

### High Load

1. Check server resources: `htop`
2. Identify slow queries
3. Scale horizontally (add servers)
4. Enable caching layer

### Security Breach

1. Rotate all API keys
2. Change all passwords
3. Review access logs
4. Identify vulnerability
5. Apply security patch
6. Notify affected users

---

## Performance Optimization

### Database

- [ ] Add indexes on frequently queried columns
- [ ] Enable query caching
- [ ] Use connection pooling
- [ ] Consider read replicas

### Application

- [ ] Enable Django caching (Redis/Memcached)
- [ ] Cache frequently accessed datasets
- [ ] Use CDN for static files
- [ ] Optimize file parsing (async processing)

### Server

- [ ] Tune Gunicorn worker count
- [ ] Configure Nginx caching
- [ ] Enable HTTP/2
- [ ] Optimize database queries

---

## Scaling Strategy

### Vertical Scaling (Single Server)

- Upgrade CPU
- Add more RAM
- Use faster disk (SSD)

### Horizontal Scaling (Multiple Servers)

- Load balancer (HAProxy, AWS ALB)
- Shared file storage (NFS, S3)
- Shared database (PostgreSQL cluster)
- Redis for session storage
- Celery for async tasks

---

## Cost Estimation

### Server (VPS)

- Small: $5-10/month (1 CPU, 1GB RAM) - Development/testing
- Medium: $20-40/month (2 CPU, 4GB RAM) - Production (<1000 users)
- Large: $80-160/month (4 CPU, 8GB RAM) - High traffic

### Additional Costs

- Domain name: $10-15/year
- SSL certificate: Free (Let's Encrypt)
- Backups: $5-20/month (depending on storage)
- Monitoring: Free-$50/month (depending on service)
- CDN: Free-$50/month (Cloudflare, AWS CloudFront)

**Total Estimate:** $20-100/month for production deployment

---

## Rollback Plan

If deployment fails:

1. Revert code to previous commit
2. Restore database from backup
3. Restore uploaded files from backup
4. Restart services
5. Verify functionality
6. Investigate failure cause

```bash
# Quick rollback script
git checkout <previous-commit>
python manage.py migrate
systemctl restart filetoapi
```

---

## Sign-Off

**Deployment completed by:** _______________  
**Date:** _______________  
**Verified by:** _______________  
**Date:** _______________  

---

**Status:** ☐ Not Started | ☐ In Progress | ☐ Completed | ☐ Verified

