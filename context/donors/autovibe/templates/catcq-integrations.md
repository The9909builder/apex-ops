# CATCQ TEMPLATE — INTEGRATIONS

> Use this template in P3 (CATCQ-FILL) for `06-integrations.md`.
> Covers third-party API clients, webhooks, OAuth-with-third-party, sync jobs.

---

```
# CONTEXT
Project:         <PROJECT_NAME>
Stack:           <STACK — pull from 00-PROJECT.md>
Integrations:    <LIST — e.g. "Apple Health (HKHealthStore via Expo), Stripe (payments + webhooks), Resend (transactional email)">
Secrets:         <SECRETS_MGMT — e.g. ".env.local in dev; Vercel env vars in prod; never committed">
Webhook strategy:<WEBHOOK — e.g. "verify signature → enqueue job → 200 OK within 1s">
User persona:    <ONE-LINE FROM 00-PROJECT.md>
Existing state:  <e.g. "no integrations wired yet">

# ACTION
INTEGRATE the third-party services listed in CONTEXT, with one module per integration.

# TARGET
Files to create — one set per integration:
  src/integrations/<vendor>/client.ts        (typed client wrapper; injects auth)
  src/integrations/<vendor>/schemas.ts       (zod schemas for vendor request + response shapes)
  src/integrations/<vendor>/errors.ts        (typed error classes; map vendor codes)
  src/integrations/<vendor>/index.ts         (public API of the integration module)
  src/integrations/<vendor>/README.md        (which env vars, how to test locally, link to docs)

Webhook handlers (if applicable):
  src/app/api/webhooks/<vendor>/route.ts     (signature verify + dispatch)
  src/integrations/<vendor>/webhook-events.ts(typed event union + handler map)

Background sync jobs (if applicable):
  src/jobs/<vendor>-sync.ts                  (periodic sync job)

Env vars (document in 00-PROJECT.md):
  <VENDOR>_API_KEY
  <VENDOR>_WEBHOOK_SECRET
  <VENDOR>_API_BASE_URL    (allows pointing at sandbox vs prod)

Do NOT modify:
  Other integration modules (each vendor isolated)
  src/lib/auth/*           (auth is separate concern)
  Database schema          (additive only — new tables/columns require separate CATCQ)

# CONSTRAINTS
- One module per vendor; no shared "API helper" file across vendors
- All vendor calls go through the typed client (no raw fetch from app code)
- Vendor secrets ONLY read from env vars; never hardcoded; never logged
- All vendor responses zod-parsed before consumption (vendors lie; trust nothing)
- Errors mapped to typed app errors (don't leak vendor error shapes upward)
- Idempotency: any write to vendor uses idempotency key (vendor-supported) OR app-side dedup
- Retries: exponential backoff with jitter; max 3 attempts; capped at 30s total
- Timeouts: every vendor call has explicit timeout (default 10s for sync, 30s for batch)
- Webhooks: verify signature at line 1; reject before any work; return 200 within 5s
- Webhooks: enqueue heavy work to a job — handler does NOT do business logic synchronously
- Sandbox-aware: every vendor module supports a TEST_MODE flag pointing at sandbox

# QUALITY
- Full TypeScript types — vendor response types inferred from zod schemas
- Structured logging at every vendor call (vendor name, endpoint, duration, status, request_id)
- Never log: API keys, full PII payloads, full card numbers, OAuth tokens
- Retry/timeout/error behavior documented in README per integration
- Test: client happy path (mocked vendor response)
- Test: client error path for each typed app error
- Test: webhook with valid signature → handler dispatched
- Test: webhook with invalid signature → 401
- Test: webhook replay (same idempotency key twice) → handled once
- E2E test against sandbox (manual or in CI with sandbox creds) documented in README

# QUALITY WRAP

## Scope limiters
- Do not modify other integration modules
- Do not add a vendor without first updating 00-PROJECT.md with rationale
- Do not skip signature verification on webhooks under any circumstance
- Do not log secrets or PII

## Anti-pattern guards
- AVOID: silent failures — every vendor error path logs + maps to typed app error
- AVOID: untyped boundaries — every vendor response zod-parsed
- AVOID: missing context — README per vendor explains: env vars, sandbox setup, common errors
- AVOID: god functions — client wrapper exposes one function per vendor endpoint, each < 30 lines
- AVOID: vague names — banned: handleStripe, doSync, callApi

## VERIFY
After implementation, run:
- `pnpm typecheck && pnpm lint` — all green
- `pnpm test src/integrations/<vendor>` — all pass
- Manual: trigger one happy-path call against sandbox → verify expected vendor-side state
- Manual: trigger webhook from vendor sandbox → verify handler runs + idempotent on replay
- Inspect logs: no secrets, no PII, structured fields present (vendor, endpoint, duration, status)
```

---

## VARIANT: OAuth-with-third-party (e.g. Google Drive, GitHub)

Add to TARGET:
- `src/integrations/<vendor>/oauth.ts` (auth-code flow handlers)
- `src/app/api/integrations/<vendor>/connect/route.ts` (start OAuth)
- `src/app/api/integrations/<vendor>/callback/route.ts` (handle callback)
- DB table: `<vendor>_connections (user_id, access_token, refresh_token, expires_at, scopes)`

Add to CONSTRAINTS:
- Tokens encrypted at rest (use Supabase Vault or app-level KMS)
- Refresh token rotation enforced — old token invalidated on refresh
- Scope minimization — request narrowest scopes possible
- Disconnect flow revokes vendor-side AND deletes app-side connection row

## VARIANT: Polling sync vs webhook

If the vendor doesn't support webhooks:
- Replace webhook handler section with a polling job in `src/jobs/<vendor>-poll.ts`
- Document polling interval + cursor strategy in README
- Cursor persisted per user (or per resource); stale cursor recovers by full re-sync
