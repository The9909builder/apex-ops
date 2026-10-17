# CATCQ TEMPLATE — FRONTEND

> Use this template in P3 (CATCQ-FILL) for any frontend-heavy domain file.
> Fill every section. Do not skip. Do not leave placeholder text in the output.

---

```
# CONTEXT
Project:         <PROJECT_NAME>
Stack:           <FRONTEND_STACK — e.g. Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui>
State manager:   <STATE — e.g. Zustand for client, TanStack Query for server>
Forms:           <FORMS — e.g. react-hook-form + zod>
Routing:         <ROUTER — e.g. Next.js App Router, file-based>
Auth context:    <AUTH — e.g. Supabase auth client, useUser() hook>
User persona:    <ONE-LINE FROM 00-PROJECT.md>
Current state:   <WHAT EXISTS NOW — e.g. "auth + base layout done; no feature modules yet">

# ACTION
<ONE PRECISE VERB from vocabulary.md, e.g. IMPLEMENT> the <FEATURE_NAME> UI module.

# TARGET
Files to create or modify:
  src/modules/<feature>/components/<List|Form|Detail>.tsx
  src/modules/<feature>/hooks/use<Feature>.ts
  src/modules/<feature>/schemas/<feature>.schema.ts
  src/app/(authed)/<feature>/page.tsx
  src/app/(authed)/<feature>/layout.tsx
  src/app/(authed)/<feature>/[id]/page.tsx

Do NOT modify:
  src/components/ui/*    (shadcn primitives — extend by composition, don't edit)
  src/lib/supabase/*     (auth client — read-only)
  src/app/layout.tsx     (root layout)

# CONSTRAINTS
- Stack-strict: no new dependencies beyond those in 00-PROJECT.md
- Single-responsibility: max 200 lines per file, max 30 lines per function
- Match existing patterns: copy the shape of src/modules/<existing-module>/ if any
- No prop drilling > 2 levels — use context or composition
- All async UI has loading + empty + error states (no naked `useQuery` consumers)
- Forms validate via zod schema imported from schemas/
- Server state via TanStack Query; client-only state via Zustand
- No CSS modules — Tailwind only; no inline styles
- Mobile-first responsive (start at base, add sm:/md:/lg: as needed)

# QUALITY
- Full TypeScript types — no `any`, no `unknown` without narrowing
- Every interactive element keyboard-reachable (Tab, Enter, Esc)
- ARIA labels on icon-only buttons
- Color contrast WCAG 2.1 AA
- React.memo / useCallback only where measured (not preemptively)
- Bundle size budget: <30KB added gzipped per feature module
- Unit test: every hook with renderHook + 1 happy + 1 error case
- Component test: every page-level component with 1 user-flow test (Testing Library)
- One Playwright e2e for the critical journey

# QUALITY WRAP

## Scope limiters
- Do not modify files outside the TARGET list
- Do not introduce new dependencies beyond those in 00-PROJECT.md
- Keep the public API of existing modules unchanged
- Match existing code patterns; do not introduce new ones

## Anti-pattern guards (from anti-patterns.md)
- AVOID: vague names — `data`, `helper`, `manager`, `util` banned
- AVOID: god functions/files — max 200 lines per file, 30 per function
- AVOID: prop drilling > 2 levels — use context or composition
- AVOID: premature abstraction — three similar lines beats early abstraction
- AVOID: untyped boundaries — every form submit / API call validates via zod

## VERIFY
After implementation, run:
- `pnpm typecheck` — must pass with zero errors
- `pnpm lint` — must pass with zero warnings
- `pnpm test src/modules/<feature>` — must pass 100%
- Manual smoke test: open <route>, complete the happy-path user flow, screenshot
```

---

## VARIANT: design-system file (07-design-system.md)

When generating the design-system file, swap ACTION to one of:
- `IMPLEMENT` (if building tokens + base components from scratch)
- `EXTRACT` (if pulling reusable patterns out of existing modules)
- `DOCUMENT` (if codifying conventions that already exist)

Add to TARGET:
- `src/styles/tokens.css` (CSS vars for color/spacing/type)
- `tailwind.config.ts` (theme extension)
- `src/components/ui/*` (shadcn customizations)
- `STYLEGUIDE.md` (consumer-facing doc)

Add to QUALITY:
- Tokens are the only source of color/spacing/type values — no magic numbers in modules
- Dark mode parity from day 1
- Storybook story per shipped component (or equivalent visual reference)
