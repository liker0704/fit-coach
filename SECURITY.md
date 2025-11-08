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

6. **API Security**
   - Rate limiting recommended (see below)
   - Request size limits
   - File upload validation (size, type)
   - No debug endpoints in production ✅

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

### 2. Production Checklist

Before deploying to production:

#### Backend
- [ ] Change `SECRET_KEY` from default (use 32+ character random string)
- [ ] Change `POSTGRES_PASSWORD` from default
- [ ] Set `POSTGRES_SERVER` to production database host
- [ ] Update `CORS_ORIGINS` to **only** your production frontend domain
- [ ] Enable HTTPS/TLS (disable HTTP)
- [ ] Set up rate limiting (see recommendations below)
- [ ] Enable HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] Review file upload limits and storage
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Remove any debug/development endpoints
- [ ] Set `docs_url=None` and `redoc_url=None` in production

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

## ⚠️ Known Limitations (MVP)

The following features are **NOT** implemented in MVP but should be added for production:

### High Priority

1. **Rate Limiting**
   - No rate limiting on auth endpoints (brute force risk)
   - **Recommendation**: Add `slowapi` or similar
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter

   @router.post("/login")
   @limiter.limit("5/minute")
   def login(...):
       ...
   ```

2. **Email Verification**
   - Password reset tokens returned in API response (MVP only)
   - Email verification tokens returned in API response (MVP only)
   - **In Production**: Integrate email service (SendGrid, AWS SES, etc.)

3. **Account Lockout**
   - No account lockout after failed login attempts
   - **Recommendation**: Add lockout after 5 failed attempts

4. **Audit Logging**
   - No audit trail for sensitive operations
   - **Recommendation**: Log auth events, profile changes, etc.

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

**Last Updated**: 2025-11-08
**Version**: 1.0.0
