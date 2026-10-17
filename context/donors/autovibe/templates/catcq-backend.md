# CATCQ TEMPLATE — BACKEND

> Use this template in P3 (CATCQ-FILL) for any backend-heavy domain file.
> Covers REST handlers, server actions, services, jobs, webhooks.

---

```
# CONTEXT
Project:         <PROJECT_NAME>
Stack:           <BACKEND_STACK — e.g. Next.js 14 Route Handlers + TypeScript + Drizzle ORM>
Runtime:         <RUNTIME — e.g. Node 20 / Vercel Edge / Bun>
Database:        <DB — e.g. Postgres via Supabase, accessed via Drizzle>
Auth:            <AUTH — e.g. Supabase auth, server-side via createServerClient>
Validation:      <VALIDATION — e.g. zod at every boundary>
Logging:         <LOGGING — e.g. pino with request-id correlation>
User persona:    <ONE-LINE FROM 00-PROJECT.md>
Current state:   <WHAT EXISTS NOW — e.g. "db schema + auth done; no business endpoints">

# ACTION
<ONE PRECISE VERB from vocabulary.md, e.g. IMPLEMENT> the <FEATURE_NAME> backend module.

# TARGET
Files to create or modify:
  src/modules/<feature>/service.ts            (business logic — pure functions)
  src/modules/<feature>/repository.ts         (data access — db queries)
  src/modules/<feature>/schemas.ts            (zod schemas — input + output DTOs)
  src/modules/<feature>/errors.ts             (typed error classes)
  src/app/api/<feature>/route.ts              (REST handler — GET/POST/PATCH/DELETE)
  src/app/api/<feature>/[id]/route.ts         (single-resource handler)

Do NOT modify:
  src/lib/db/*           (shared db client)
  src/lib/auth/*         (auth helpers — read-only)
  src/middleware.ts      (global middleware — separate concern)

# CONSTRAINTS
- Stack-strict: no new dependencies beyond those in 00-PROJECT.md
- Layer discipline: handler → service → repository. NEVER call db from handler directly.
- Service functions are PURE — no req/res objects, accept primitives + return data/errors
- Every handler: parse body → zod.parse → call service → return typed response
- Every error path logs structured (req_id, user_id, error code, stack)
- Auth-required endpoints: assert user via auth helper at top of handler; 401 on miss
- Authorization: row-level check inside service (e.g. assertOwns(userId, resource))
- Idempotency: PATCH/DELETE handle "already in desired state" without error
- Rate limit applied at middleware layer for any unauthenticated path

# QUALITY
- Full TypeScript types — no `any`; service signatures use inferred zod types
- Zod parse at every boundary (HTTP in, HTTP out, queue in/out, third-party in)
- Structured logging at every error path; never log secrets/PII/tokens
- Unit test: every service function with 1 happy + 1 sad case
- Integration test: every endpoint with auth + validation + happy + 1 error
- Performance budget: p95 < 200ms for read endpoints, < 500ms for write
- Return error responses in a consistent envelope:
    { error: { code: string, message: string, details?: unknown } }
- HTTP status codes are precise: 200/201/204/400/401/403/404/409/422/429/500

# QUALITY WRAP

## Scope limiters
- Do not modify files outside the TARGET list
- Do not introduce new dependencies beyond those in 00-PROJECT.md
- Do not bypass auth / validation / rate limits
- Do not log secrets, PII, or auth tokens
- Keep handler thin: parse → auth → call service → respond

## Anti-pattern guards (from anti-patterns.md)
- AVOID: silent failures — every catch logs OR rethrows; no empty catches
- AVOID: god functions — service functions stay < 30 lines, single responsibility
- AVOID: untyped boundaries — zod.parse on every external input
- AVOID: vague names — banned: data/result/helper/manager
- AVOID: missing context — handler comments name the user journey it serves

## VERIFY
After implementation, run:
- `pnpm typecheck` — must pass
- `pnpm lint` — must pass
- `pnpm test src/modules/<feature>` — must pass 100%
- `pnpm test:integration api/<feature>` — must pass
- Manual smoke test: curl the endpoints with valid + invalid payloads, check responses
```

---

## VARIANT: job/worker file

When generating a background-job file:

Swap ACTION to `IMPLEMENT` a job/worker.

Swap TARGET to:
- `src/jobs/<job-name>.ts` (job definition)
- `src/jobs/<job-name>.handler.ts` (execution logic)
- `src/jobs/registry.ts` (add to scheduler)

Add to CONSTRAINTS:
- Idempotent — same input twice produces same outcome
- Retry-safe — failure mid-execution leaves consistent state
- Bounded — max execution time, max memory, fail-fast on either

Add to QUALITY:
- Dead-letter queue path for poison messages
- Observability: emit job-started / job-completed / job-failed events
- Concurrency cap documented

## VARIANT: webhook handler

When generating a webhook handler:

Add to CONSTRAINTS:
- Signature verification at line 1 of handler (reject before processing)
- Return 200 within 5s — defer heavy work to a job
- Replay-safe via idempotency key from payload

Add to QUALITY:
- Test: invalid signature → 401
- Test: replay of same event → 200 no double-effect
