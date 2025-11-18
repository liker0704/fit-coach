# Security Policy

## 🔒 Security Best Practices

This document outlines the security measures implemented in FitCoach and best practices for deployment.

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please email us at **security@fitcoach.app** (or create a private security advisory on GitHub). Do not open public issues for security vulnerabilities.

## Security Features

### Backend (FastAPI)

#### ✅ Implemented Security Measures

1. **Authentication & Authorization**
   - JWT-based authentication with access and refresh tokens
   - Bcrypt password hashing (12 rounds)
   - Refresh token rotation and revocation
   - Token expiration: 15 minutes (access), 7 days (refresh)

2. **Security Headers** ✨ NEW
   - `X-Frame-Options: DENY` - Prevents clickjacking
   - `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
   - `X-XSS-Protection: 1; mode=block` - XSS protection
   - `Content-Security-Policy` - Restricts resource loading
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Permissions-Policy` - Restricts browser features

3. **CORS Configuration**
   - Restricted to specific origins (no wildcards)
   - Limited HTTP methods (GET, POST, PUT, DELETE, OPTIONS, PATCH)
   - Specific allowed headers (no `*`)
   - 10-minute cache for preflight requests

4. **Database Security**
   - SQLAlchemy ORM (prevents SQL injection)
   - Parameterized queries
   - No raw SQL execution
   - Database credentials from environment variables only

5. **Input Validation**
   - Pydantic models for all endpoints
   - Type checking and validation
   - Max length enforcement
   - Email format validation

6. **API Security** ✅
   - Rate limiting with slowapi (10/min for auth endpoints) ✅
   - Request size limits
   - File upload validation (size, type)
   - No debug endpoints in production ✅

7. **Email Service** ✅
   - SMTP-based email delivery for password reset and verification
   - No tokens exposed in API responses (sent via email only)
   - Support for Gmail, SendGrid, AWS SES, and other SMTP providers
   - Configurable via environment variables

8. **Audit Logging** ✅
   - Comprehensive audit trail for security events
   - Logs authentication events (login, logout, registration)
   - Tracks password resets and email verifications
   - Stores IP address, user agent, and metadata
   - Database-backed with indexed queries for analysis

### Mobile App (React Native)

#### ✅ Implemented Security Measures

1. **Token Storage**
   - Expo SecureStore for JWT tokens (iOS Keychain / Android Keystore)
   - No tokens in AsyncStorage or plain text

2. **API Communication**
   - HTTPS only (enforce in production)
   - Token refresh flow with retry logic
   - Automatic logout on token expiration

3. **Input Validation**
   - Client-side validation before API calls
   - Type checking with TypeScript
   - Sanitization of user inputs

## 🔴 Critical Configuration Requirements

### 1. Environment Variables (`.env`)

**NEVER** commit `.env` file to git. Always use `.env.example` as template.

Required configuration:

```bash
# Generate strong SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in .env
SECRET_KEY=<generated-strong-random-string>
POSTGRES_PASSWORD=<strong-database-password>
GOOGLE_API_KEY=<your-api-key>  # or OPENAI_API_KEY
```

### 2. Email Service Configuration ✅

**Development (Email disabled by default):**
```bash
ENABLE_EMAIL=false  # Tokens logged to console instead
```

**Production (Email enabled):**

Option 1: Gmail SMTP
```bash
ENABLE_EMAIL=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Generate at https://myaccount.google.com/apppasswords
FRONTEND_URL=https://your-domain.com
```

Option 2: SendGrid
```bash
ENABLE_EMAIL=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
FRONTEND_URL=https://your-domain.com
```

Option 3: AWS SES
```bash
ENABLE_EMAIL=true
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_aws_smtp_username
SMTP_PASSWORD=your_aws_smtp_password
FRONTEND_URL=https://your-domain.com
```

### 3. Production Checklist

Before deploying to production:

#### Backend
- [ ] Change `SECRET_KEY` from default (use 32+ character random string)
- [ ] Change `POSTGRES_PASSWORD` from default
- [ ] Set `POSTGRES_SERVER` to production database host
- [ ] Update `CORS_ORIGINS` to **only** your production frontend domain
- [ ] Enable HTTPS/TLS (disable HTTP)
- [x] Rate limiting configured (10/min auth endpoints) ✅
- [ ] Enable HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [x] Email service configured (ENABLE_EMAIL=true, SMTP settings) ✅
- [ ] Set FRONTEND_URL to production domain
- [x] Audit logging enabled (database table created) ✅
- [ ] Run database migration: `alembic upgrade head`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Review file upload limits and storage
- [x] Set up database backups ✅
- [ ] Configure logging and monitoring
- [ ] Remove any debug/development endpoints
- [ ] Set `docs_url=None` and `redoc_url=None` in production

#### Docker & DevOps ✅ NEW
- [x] No hardcoded credentials in docker-compose.yml ✅
- [x] Environment variables in `.env.docker` (gitignored) ✅
- [x] Strong passwords (minimum 16 characters) ✅
- [x] Non-root user in Docker containers (UID 1000) ✅
- [x] Multi-stage Docker build for minimal attack surface ✅
- [x] Health checks enabled for all services ✅
- [x] Resource limits configured ✅
- [x] Restart policy set to `always` ✅
- [x] Automated backup script with compression and rotation ✅
- [x] Restore script with pre-restore safety backup ✅
- [ ] Schedule automated backups (cron or systemd timer)
- [ ] Test backup/restore procedures
- [ ] Configure off-site backup storage
- [ ] Enable backup encryption (GPG)
- [ ] Set up firewall rules (UFW/iptables)
- [ ] Configure reverse proxy with SSL (Nginx)
- [ ] Scan Docker images for vulnerabilities (Trivy)

#### Mobile App
- [ ] Update `API_BASE_URL` to production HTTPS endpoint
- [ ] Enable certificate pinning (recommended)
- [ ] Test with real API keys
- [ ] Review permissions requested
- [ ] Test offline mode edge cases

#### Desktop App
- [ ] Update API endpoint to production
- [ ] Test auto-updates security
- [ ] Review Electron security settings

## ⚠️ Known Limitations

The following features should be considered for production:

### High Priority

1. ✅ **Rate Limiting** - IMPLEMENTED
   - Rate limiting active on all auth endpoints (10/min for login/register, 5/min for password reset)
   - Using slowapi library with IP-based rate limiting
   - Returns 429 status code with retry-after header

2. ✅ **Email Service** - IMPLEMENTED
   - Password reset tokens sent via email (no longer in API response)
   - Email verification tokens sent via email
   - SMTP-based delivery with support for Gmail, SendGrid, AWS SES
   - Configurable via ENABLE_EMAIL environment variable

3. ✅ **Audit Logging** - IMPLEMENTED
   - Comprehensive audit trail for security events
   - Logs all authentication events with IP and user agent
   - Database-backed with indexed queries

4. **Account Lockout**
   - No account lockout after failed login attempts
   - **Recommendation**: Add lockout after 5 failed attempts (can use audit logs to implement)

### Medium Priority

5. **Password Policy**
   - No minimum password strength requirements
   - **Recommendation**: Enforce 8+ characters, complexity

6. **2FA/MFA**
   - No two-factor authentication
   - **Recommendation**: Add TOTP support

7. **Session Management**
   - No device/session tracking
   - **Recommendation**: Track active sessions, allow revocation

8. **API Key Rotation**
   - No automatic rotation of API keys
   - **Recommendation**: Implement key rotation policy

## 🐳 Docker & DevOps Security ✨ NEW

### Container Security

#### ✅ Implemented Measures

1. **Non-Root Containers**
   - All production containers run as non-root user (UID 1000)
   - Backend uses dedicated `fitcoach` user
   - Minimizes privilege escalation risks

2. **Multi-Stage Builds**
   - Optimized Dockerfile with multi-stage builds
   - Minimal production image (python:3.11-slim)
   - Build tools excluded from final image
   - Reduced attack surface

3. **Resource Limits**
   - CPU and memory limits configured
   - Prevents resource exhaustion attacks
   - Production limits in `docker-compose.production.yml`

4. **Health Checks**
   - All services have health checks
   - Automatic container restart on failures
   - Monitoring integration ready

### Credentials Management ✅

**CRITICAL SECURITY FIX**: All hardcoded credentials removed!

1. **Environment Variables**
   - `.env.docker` for all credentials
   - Required variables: `POSTGRES_PASSWORD`, `PGADMIN_DEFAULT_PASSWORD`
   - Validation: Docker Compose fails if variables missing
   - Template: `.env.docker.example` for setup

2. **GitIgnore Protection**
   - `.env.docker` added to `.gitignore`
   - Backup files (`.sql`, `.sql.gz`) excluded
   - `backups/` directory excluded

### Database Backup Strategy ✅

**Production-ready backup and restore solution implemented!**

#### Backup Script (`scripts/backup.sh`)
- Automated PostgreSQL backups via `pg_dump`
- gzip compression for space efficiency
- 30-day retention with automatic rotation
- Integrity verification after backup
- Comprehensive error handling
- Detailed logging to `backups/backup.log`

#### Restore Script (`scripts/restore.sh`)
- Safe restore with pre-restore backup
- Confirmation prompt (can be forced)
- Active connection termination
- Transaction-safe restore
- Post-restore verification

#### Automation Options
- **Cron**: Example schedules in `scripts/backup.cron`
- **Systemd**: Timer units in `scripts/fitcoach-backup.{service,timer}`
- Recommended: Every 6 hours for production

#### Security Features
- Backup file encryption support (GPG)
- Restrictive file permissions (600)
- Off-site backup ready (rsync, S3 sync)
- No credentials in scripts (loaded from `.env.docker`)

**Documentation**: See [docs/BACKUP.md](docs/BACKUP.md) for complete guide

### Production Dockerfile Features

**File**: `backend/Dockerfile`

- **Multi-stage build**: Separate dependency and production stages
- **Non-root user**: `fitcoach:1000` for all operations
- **Minimal base**: `python:3.11-slim` for small image size
- **Layer optimization**: Dependencies installed before code copy
- **Health check**: Built-in HTTP health endpoint check
- **Development target**: Separate stage with hot-reload
- **Security labels**: Metadata for security scanning
- **.dockerignore**: Excludes unnecessary files from build context

### Network Security

1. **Internal Network**
   - Database and Redis not exposed to host (production)
   - Backend as only entry point
   - Custom Docker network: `fitcoach-network`

2. **Port Binding**
   - Development: All ports exposed to localhost
   - Production: Only reverse proxy exposed
   - Configuration via environment variables

### Image Security

**Best Practices**:
- Official base images only
- Specific version tags (no `latest`)
- Alpine Linux for minimal attack surface
- Regular security scanning recommended

**Scan for Vulnerabilities**:
```bash
# Install Trivy
sudo apt-get install trivy

# Scan base images
trivy image postgres:15-alpine
trivy image redis:7-alpine
trivy image python:3.11-slim

# Scan custom backend image
docker build -t fitcoach-backend:latest backend/
trivy image fitcoach-backend:latest
```

### Volume Security

**Production Configuration**:
- Persistent volumes for data
- Separate volume for backups
- Restrictive permissions
- Bind mounts to specific directories

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/fitcoach/postgres
```

### Secrets Management

**Development**:
- `.env.docker` for Docker Compose variables
- `backend/.env` for application secrets
- Both files gitignored

**Production Recommendations**:
- Docker Secrets (Swarm mode)
- Kubernetes Secrets
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault

### Monitoring & Logging

**Container Logs**:
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Backup logs
cat backups/backup.log
tail -f backups/backup.log
```

**Log Rotation**:
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Production Deployment

**Using Production Compose**:
```bash
# Start with production settings
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f
```

**Features**:
- Resource limits enforced
- Optimized PostgreSQL settings
- Redis memory management
- Automatic restarts
- Health checks enabled

## 🛡️ Security Testing

### Before Deployment

1. **Dependency Scanning**
   ```bash
   # Backend
   pip install safety
   safety check --file requirements.txt

   # Mobile
   npm audit
   ```

2. **Static Analysis**
   ```bash
   # Backend
   bandit -r app/

   # TypeScript
   npm run lint
   ```

3. **Security Headers Testing**
   - Use [SecurityHeaders.com](https://securityheaders.com)
   - Use [Mozilla Observatory](https://observatory.mozilla.org)

4. **Penetration Testing**
   - Test for OWASP Top 10 vulnerabilities
   - SQL injection attempts (should be blocked by ORM)
   - XSS attempts (should be blocked by CSP)
   - CSRF attempts (should be blocked by CORS + token auth)

## 🔐 API Keys & Secrets Management

### Development
- Use `.env` file (gitignored)
- Never hardcode secrets in code

### Production
- Use environment variables
- Consider using secrets manager:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Google Secret Manager
  - Azure Key Vault

## 📝 Compliance Considerations

If handling user health data in production, consider:

- **HIPAA** (US healthcare data)
- **GDPR** (EU user data)
- **CCPA** (California user data)
- Data retention policies
- Right to deletion
- Data export capabilities
- Privacy policy
- Terms of service

## 🚨 Incident Response

In case of a security breach:

1. **Immediate Actions**
   - Rotate all secrets (SECRET_KEY, DB passwords, API keys)
   - Revoke all refresh tokens
   - Review logs for unauthorized access
   - Notify affected users

2. **Investigation**
   - Determine scope of breach
   - Identify attack vector
   - Document timeline

3. **Remediation**
   - Fix vulnerability
   - Deploy patch
   - Monitor for further attempts

4. **Post-Incident**
   - Update security measures
   - Review and improve processes
   - Conduct post-mortem

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [React Native Security](https://reactnative.dev/docs/security)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Last Updated**: 2025-11-18
**Version**: 1.1.0 - Added Docker & DevOps Security
