# Deployment Guide - Dave Application

## Pre-Deployment Security Checklist

### 1. Generate Secure Secrets

Before deploying to production, generate strong secrets:

```bash
# Generate JWT secret (32+ bytes recommended)
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate registration secret
python3 -c "import secrets; print('REGISTRATION_SECRET=' + secrets.token_urlsafe(32))"
```

### 2. Environment Variables

Create a `.env` file in production with the following variables:

```bash
# App Settings
DEBUG=false  # CRITICAL: Must be false in production
APP_NAME=Dave

# OpenRouter API
OPENROUTER_API_KEY=your_real_openrouter_api_key

# GitHub (Vault Access)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=yourusername/your-vault-repo
VAULT_PATH_PREFIX=David's Notes

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dave

# JWT Authentication
JWT_SECRET_KEY=<generated_secret_from_step_1>
JWT_ALGORITHM=HS256

# Registration Control
REGISTRATION_SECRET=<generated_secret_from_step_1>

# Redis
REDIS_URL=redis://redis:6379

# Qdrant Vector Store
QDRANT_URL=http://qdrant:6333

# Neo4j (if using knowledge graph)
NEO4J_URL=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_neo4j_password
```

### 3. Verify Security Settings

Run this checklist before deployment:

```bash
# Check that DEBUG is false
grep "DEBUG=false" .env

# Verify secrets are not default values
grep -v "change-this\|super-secret\|please-change" .env

# Ensure no secrets in version control
git log --all --full-history -- .env
```

---

## Registration Flow for New Users

Since registration is now protected, here's how to add new users:

### Step 1: Share Registration URL

The registration endpoint is now at:
```
POST https://dave.davidbuitrago.dev/api/v1/auth/register-secret-7x9k2m4n
```

### Step 2: Provide Registration Token

New users will need:
1. The obscured URL path: `/auth/register-secret-7x9k2m4n`
2. The `registration_token` value (from `REGISTRATION_SECRET` env var)

### Step 3: Registration Request

```bash
curl -X POST "https://dave.davidbuitrago.dev/api/v1/auth/register-secret-7x9k2m4n" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "registration_token": "YOUR_REGISTRATION_SECRET"
  }'
```

### Step 4: Login

After registration, users can log in at:
```
POST https://dave.davidbuitrago.dev/api/v1/auth/login
```

---

## Docker Deployment

### Docker Compose Setup

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
      - qdrant
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped
    volumes:
      - ./ssl:/etc/ssl/certs  # SSL certificates

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dave
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

volumes:
  postgres_data:
  qdrant_data:
```

### Deploy Commands

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

---

## SSL/TLS Configuration

### Using Certbot (Let's Encrypt)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d dave.davidbuitrago.dev

# Auto-renewal (certbot sets this up automatically)
sudo certbot renew --dry-run
```

### Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name dave.davidbuitrago.dev;

    ssl_certificate /etc/letsencrypt/live/dave.davidbuitrago.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dave.davidbuitrago.dev/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers (additional to FastAPI headers)
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name dave.davidbuitrago.dev;
    return 301 https://$server_name$request_uri;
}
```

---

## Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp   # HTTP (for certbot)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## Monitoring & Logging

### Application Logs

```bash
# View backend logs
docker-compose logs -f backend

# Search for errors
docker-compose logs backend | grep -i error

# Search for authentication attempts
docker-compose logs backend | grep -i "login\|register"
```

### Database Backups

```bash
# Automated daily backups
#!/bin/bash
# save as /opt/scripts/backup-dave.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/dave"

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U postgres dave > "$BACKUP_DIR/dave_$DATE.sql"

# Backup Qdrant
docker-compose exec -T qdrant tar czf - /qdrant/storage > "$BACKUP_DIR/qdrant_$DATE.tar.gz"

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/scripts/backup-dave.sh
```

---

## Security Monitoring

### Failed Login Attempts

```bash
# Monitor failed logins in real-time
docker-compose logs -f backend | grep "401\|Unauthorized"
```

### Set Up Alerts

Consider setting up alerts for:
- Multiple failed login attempts from same IP
- Registration attempts with invalid tokens
- Unusual API access patterns
- High error rates

---

## Post-Deployment Verification

### 1. Test Authentication Flow

```bash
# Should fail (no registration token)
curl -X POST "https://dave.davidbuitrago.dev/api/v1/auth/register-secret-7x9k2m4n" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Should return 403 Forbidden ✓
```

### 2. Verify HTTPS

```bash
curl -I https://dave.davidbuitrago.dev
# Should see Strict-Transport-Security header
```

### 3. Check API Docs are Disabled

```bash
curl https://dave.davidbuitrago.dev/docs
# Should return 404 ✓
```

### 4. Test Security Headers

```bash
curl -I https://dave.davidbuitrago.dev
# Should see:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Rollback Procedure

If issues arise:

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Restore from backup
docker-compose exec -T postgres psql -U postgres dave < /opt/backups/dave/dave_YYYYMMDD_HHMMSS.sql

# Deploy previous version
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Support & Troubleshooting

### Common Issues

**Issue**: Can't log in after deployment
- Check DEBUG=false is set
- Verify JWT_SECRET_KEY hasn't changed (would invalidate all tokens)
- Check cookies are being set (HTTPS required in production)

**Issue**: Registration endpoint not working
- Verify REGISTRATION_SECRET environment variable is set
- Check the registration token being sent matches the environment variable
- Ensure using the correct endpoint path

**Issue**: CORS errors
- Verify production domain is in allow_origins list
- Check HTTPS is being used
- Verify cookies credentials setting

---

## Security Incident Response

If you suspect a security breach:

1. **Immediately**:
   - Rotate JWT_SECRET_KEY (invalidates all sessions)
   - Change REGISTRATION_SECRET
   - Review recent logs for suspicious activity

2. **Investigate**:
   - Check application logs
   - Review database for unauthorized changes
   - Check user accounts

3. **Remediate**:
   - Reset affected user passwords
   - Update security measures
   - Document incident

---

## Maintenance Schedule

- **Daily**: Check logs for errors
- **Weekly**: Review backup integrity
- **Monthly**: Update dependencies, review security logs
- **Quarterly**: Full security audit, rotate secrets
- **Yearly**: Review and update SSL certificates (auto-renewed by certbot)

---

**Last Updated**: 2025-11-24
**Deployment Owner**: David Buitrago
