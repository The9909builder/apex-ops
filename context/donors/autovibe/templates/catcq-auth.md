# CATCQ TEMPLATE — AUTH

> Use this template in P3 (CATCQ-FILL) for `03-auth.md`.
> Covers signup, signin, session management, password reset, RLS wiring.

---

```
# CONTEXT
Project:         <PROJECT_NAME>
Auth provider:   <AUTH — e.g. Supabase Auth (email + OAuth Google + Apple)>
Session model:   <SESSION — e.g. Supabase httpOnly cookie sessions, refresh on server>
Frontend:        <FE_FRAMEWORK — e.g. Next.js App Router>
Backend:         <BE_RUNTIME — e.g. Next.js Route Handlers>
RLS strategy:    <RLS — e.g. auth.uid() = user_id on every user-owned row>
User persona:    <ONE-LINE FROM 00-PROJECT.md>
Existing state:  <e.g. "Supabase project provisioned; auth.users table exists; no app-side wiring">

# ACTION
IMPLEMENT end-to-end authentication: signup, signin, signout, password reset, session refresh, and protected-route enforcement.

# TARGET
Files to create:
  src/lib/auth/client.ts             (browser-side Supabase client)
  src/lib/auth/server.ts             (server-side Supabase client w/ cookie reading)
  src/lib/auth/middleware.ts         (Next.js middleware for session refresh)
  src/lib/auth/get-user.ts           (server helper — returns user or null)
  src/lib/auth/require-user.ts       (server helper — returns user or throws 401)
  src/middleware.ts                  (wire auth middleware into Next.js)
  src/app/(auth)/signup/page.tsx     (signup form)
  src/app/(auth)/signin/page.tsx     (signin form)
  src/app/(auth)/reset/page.tsx      (request password reset)
  src/app/(auth)/reset/confirm/page.tsx (confirm new password)
  src/app/(auth)/callback/route.ts   (OAuth callback handler)
  src/app/(authed)/layout.tsx        (protected layout — assert user)
  src/components/auth/SigninForm.tsx (form components with react-hook-form + zod)
  src/components/auth/SignupForm.tsx
  src/components/auth/ResetForm.tsx
  src/lib/auth/schemas.ts            (zod schemas for forms)

Do NOT modify:
  Database schema    (users table managed by Supabase)
  Any feature module (auth must not leak into modules — they consume via require-user)

# CONSTRAINTS
- Use Supabase's @supabase/ssr package (cookie-based, server-component-safe)
- Never expose service-role key to client code
- Email validation via zod (proper email + max length)
- Password rules: min 12 chars, at least one digit (configurable via constant)
- Rate limit signup + signin + reset at middleware (IP-based, 5/min)
- OAuth callback validates state param and origin
- Session refresh runs in middleware on every request; no client-side refresh
- Protected routes use a layout (route groups), NOT per-page checks
- Sign-out invalidates the server session AND clears client cookies
- Errors surface as form-level messages; do not redirect on error

# QUALITY
- Full TypeScript types throughout; auth helpers return discriminated union (user | null)
- Forms via react-hook-form + zod resolvers; no manual state
- Loading states on all submit buttons (disabled + spinner)
- Empty state on protected layout while session resolves (no flash of unauth content)
- Error messages user-friendly + accessible (role=alert)
- A11y: form labels associated, errors linked via aria-describedby
- Test: signup happy path (form → server → user created → redirect)
- Test: signin happy + wrong password + locked account
- Test: protected route as unauthed → redirects to /signin with ?next=
- Test: oauth callback with invalid state → 400
- E2E (Playwright): full signup → signin → access protected → signout flow

# QUALITY WRAP

## Scope limiters
- Do not modify db schema (auth.users is managed)
- Do not introduce a new auth provider — Supabase only
- Do not handle auth in feature modules — they import require-user
- Do not store passwords or tokens in localStorage / sessionStorage

## Anti-pattern guards
- AVOID: silent failures — auth errors are user-visible AND structured-logged server-side
- AVOID: missing context — every auth helper documents which layer it runs in (server / client / edge)
- AVOID: untyped boundaries — every form payload zod-parsed before server call
- AVOID: vague names — banned: handleAuth, doSignin, processUser

## VERIFY
After implementation, run:
- `pnpm typecheck && pnpm lint && pnpm test src/lib/auth` — all green
- Manual: signup with new email → verify email lands → click link → redirected authed
- Manual: signin with wrong password 5x → 6th attempt rate-limited
- Manual: open protected route in incognito → redirected to /signin?next=...
- Manual: signout → cookie cleared → protected route redirects again
- DB check: a new user row exists in auth.users + (if used) a profiles row
```
