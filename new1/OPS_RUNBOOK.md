# Cure-Link Operations Runbook (Production)

This runbook covers the non-code launch items required for handling sensitive health data safely.

## 1) Monitoring and Alerting

- Enable app error monitoring (e.g., Sentry) for Django and frontend.
- Capture:
  - unhandled exceptions
  - 5xx error rate
  - auth failures/rate-limit spikes
  - DB connectivity failures
- Configure alert channels (email + pager/chat) with on-call ownership.
- Verify by triggering a controlled test exception in staging first.

## 2) Logging

- Keep structured server logs for:
  - request path, status code, latency
  - authenticated user ID (where appropriate)
  - security events (login fail, 401, 403, 429)
- Redact sensitive fields: passwords, tokens, health payload details.
- Set log retention and access controls (least privilege).

## 3) Backups and Restore

- Database backups:
  - automated daily full backup
  - point-in-time recovery where available
  - encryption at rest and in transit
- Store backups in separate account/project from app runtime.
- Test restore monthly:
  - restore to staging
  - run smoke tests on restored data
  - record RTO/RPO results

## 4) Incident Response

- Create an incident severity matrix (SEV1-SEV3).
- Define response roles:
  - incident commander
  - communications owner
  - technical lead
- Keep a breach-response playbook with legal/compliance contacts.
- Run at least one tabletop exercise before production launch.

## 5) Access and Secrets

- Restrict production admin access by IP/VPN where possible.
- Rotate secrets and tokens on a schedule.
- Store secrets in platform secret manager (never in git).
- Enforce MFA on cloud and code-hosting accounts.

## 6) UK GDPR / Sensitive Health Data Controls

- Complete and store DPIA.
- Maintain Records of Processing Activities (RoPA).
- Define retention/deletion schedule for health data.
- Document lawful basis + explicit consent handling.
- Ensure DSAR process is documented and tested.

## 7) Pre-Go-Live Gate

Ship only when all are true:
- Security checklist complete (`DEPLOY_SECURITY_CHECKLIST.md`)
- Monitoring alerts tested
- Backup restore tested
- Incident runbook approved
- DPIA approved
