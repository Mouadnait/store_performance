# Security Documentation - Store Performance Platform

## 🛡️ Security Features Implemented

### 1. Authentication & Authorization
- ✅ Secure login with rate limiting (5 attempts per minute)
- ✅ No user enumeration (generic error messages)
- ✅ Comprehensive input validation
- ✅ Password strength requirements (8+ characters, not common, not numeric)
- ✅ Session management with 24-hour expiry
- ✅ CSRF protection enabled
- ✅ Login/logout event logging

### 2. Middleware Protection

#### SecurityHeadersMiddleware
```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

#### RateLimitMiddleware
- API endpoints: 60 requests/minute
- Login/Signup: 5 requests/minute
- General pages: 120 requests/minute
- Automatic IP blocking for suspicious activity

#### SecurityEventMiddleware
- Tracks suspicious request patterns
- Monitors access to sensitive paths
- Automatic blocking after 10 suspicious requests

### 3. Input Validation & Sanitization

**All forms include:**
- Length validation (e.g., client name max 100 chars)
- Type validation (prices must be positive decimals)
- Email format validation
- Phone number format validation
- XSS prevention with HTML escaping
- SQL injection prevention (Django ORM)

**Limits to prevent abuse:**
- Maximum 1000 items per bill
- Maximum 500 products displayed
- Maximum 100 categories loaded
- Field truncation to prevent buffer overflow

### 4. Production Security Settings

**HTTPS Enforcement:**
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
```

**Cookie Security:**
```python
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
```

### 5. Logging & Monitoring

**Log Files:**
- `logs/app.log` - Application events
- `logs/security.log` - Security events (rate limits, failed logins, suspicious activity)
- `logs/error.log` - Error tracking

**Logged Events:**
- User login/logout
- Failed login attempts
- Rate limit violations
- Suspicious request patterns
- Slow requests (> 2 seconds)
- All errors (4xx, 5xx responses)

### 6. Security Decorators

**Available decorators:**
```python
from core.decorators import rate_limit, require_https, log_access

@rate_limit(requests=10, window=60)
@require_https
@log_access
def sensitive_view(request):
    ...
```

## 🔒 Security Best Practices

### For Developers

1. **Always validate user input:**
   ```python
   # Good
   client_name = request.POST.get('clientName', '').strip()[:100]
   
   # Bad
   client_name = request.POST.get('clientName')
   ```

2. **Use Django ORM (prevents SQL injection):**
   ```python
   # Good
   Client.objects.filter(user=request.user)
   
   # Bad
   cursor.execute(f"SELECT * FROM client WHERE user_id={user.id}")
   ```

3. **Escape output in templates:**
   ```django
   <!-- Good -->
   {{ user.name|escape }}
   
   <!-- Bad -->
   {{ user.name|safe }}
   ```

4. **Use CSRF tokens:**
   ```django
   <form method="POST">
       {% csrf_token %}
       ...
   </form>
   ```

### For System Administrators

1. **Environment Variables (Required):**
   ```bash
   SECRET_KEY=your-secret-key-here-50plus-characters
   DJANGO_ENV=production
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DB_PASSWORD=strong-database-password
   REDIS_URL=redis://localhost:6379/0
   ```

2. **Optional but Recommended:**
   ```bash
   SENTRY_DSN=https://your-sentry-dsn
   SENDGRID_API_KEY=your-sendgrid-key
   ```

3. **Run Security Audit:**
   ```bash
   python manage.py security_audit
   ```

4. **Check for vulnerabilities:**
   ```bash
   pip install safety
   safety check
   ```

## 🚨 Incident Response

### Failed Login Attempts
- Monitored automatically
- Logs stored in `logs/security.log`
- IP blocked after 5 failures within 15 minutes

### Rate Limit Violations
- Automatically enforced by middleware
- Offending IPs logged
- Returns 429 status code

### Suspicious Activity
- Tracked by SecurityEventMiddleware
- Examples: accessing /phpmyadmin, /.env, /wp-admin
- IP blocked after 10 suspicious requests within 1 hour

## 📊 Security Monitoring

### Manual Checks
```bash
# Check security logs
tail -f logs/security.log

# Check error logs
tail -f logs/error.log

# Run security audit
python manage.py security_audit
```

### Automated Monitoring (if Sentry enabled)
- Real-time error tracking
- Performance monitoring
- Security event tracking
- Email alerts for critical issues

## 🔄 Regular Maintenance

### Daily
- Monitor log files for unusual activity
- Check error rates

### Weekly
- Review security logs
- Run security audit command
- Check for failed login patterns

### Monthly
- Update dependencies: `pip list --outdated`
- Check for security updates: `safety check`
- Review and rotate logs
- Audit user permissions

## 📝 Compliance Notes

**GDPR/Privacy:**
- User data access restricted to owner only
- No user enumeration
- Secure password storage (Django's PBKDF2)
- Session data encrypted

**OWASP Top 10 Coverage:**
- ✅ A01 Broken Access Control - Implemented
- ✅ A02 Cryptographic Failures - Implemented
- ✅ A03 Injection - Prevented (ORM, validation)
- ✅ A04 Insecure Design - Secure by design
- ✅ A05 Security Misconfiguration - Configured
- ✅ A06 Vulnerable Components - Regular updates
- ✅ A07 Authentication Failures - Protected
- ✅ A08 Data Integrity Failures - Validated
- ✅ A09 Logging Failures - Comprehensive logging
- ✅ A10 SSRF - Protected

## 🆘 Emergency Contacts

**Security Issue Found?**
1. Document the issue
2. Check logs immediately
3. If data breach suspected:
   - Disable affected accounts
   - Rotate credentials
   - Review access logs
   - Notify affected users (if required by law)

**Need Help?**
- Run: `python manage.py security_audit`
- Check documentation
- Review logs

## 📚 Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---
**Last Updated:** January 28, 2026
**Version:** 2.0.0
