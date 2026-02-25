# Cure-Link Deployment Security Checklist

Use this before going live on `cure-link.uk`.

## 1) Environment and Secrets
- Set `DJANGO_DEBUG=False`.
- Set a strong `DJANGO_SECRET_KEY` (do not reuse local/dev values).
- Set `DJANGO_ALLOWED_HOSTS=cure-link.uk,www.cure-link.uk`.
- Set:
  - `CORS_ALLOWED_ORIGINS=https://cure-link.uk,https://www.cure-link.uk`
  - `CSRF_TRUSTED_ORIGINS=https://cure-link.uk,https://www.cure-link.uk`
- Keep `.env` out of git.

## 2) TLS and Domain
- Point DNS `A/AAAA` or `CNAME` records for `cure-link.uk` and `www.cure-link.uk`.
- Enable HTTPS certificate for both hostnames.
- Force HTTPS redirect at reverse proxy or app layer.

## 3) Database and Migrations
- Run migrations on production:
  - `python manage.py migrate`
- Confirm all recent migrations are applied (including API schema updates).

## 4) Django Security Settings (already coded, env-driven)
- Verify production boots with:
  - secure cookies enabled
  - HSTS enabled
  - `SESSION_COOKIE_HTTPONLY=True`

## 5) Access Control and Data Exposure
- Confirm user API responses do not expose passwords.
- Confirm non-staff users can only access their own profile APIs.
- Confirm staff-only routes/features are not visible to clients.

## 6) Operational Safety
- Add error monitoring (e.g., Sentry).
- Enable application and proxy access logs.
- Configure automated encrypted database backups.
- Test restore from backup before launch.

## 7) Abuse Protection
- Add rate limiting for login/signup and write APIs (reverse proxy or Django middleware).
- Enable brute-force protection and alerting for repeated failed logins.

## 8) Privacy and Compliance (UK GDPR special-category data)
- Complete DPIA.
- Keep privacy policy and consent text live and accurate.
- Document retention/deletion policy.
- Document incident response process.

## 9) Final Smoke Test
- Signup flow (with mandatory consent) works.
- Trial selection + answer-option flow works.
- Profile page role-based visibility works (staff vs client).
- No 4xx/5xx errors in browser console or server logs for key journeys.
