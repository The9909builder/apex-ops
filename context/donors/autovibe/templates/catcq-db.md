# CATCQ TEMPLATE — DATABASE

> Use this template in P3 (CATCQ-FILL) for `02-db-schema.md` and any data-layer file.

---

```
# CONTEXT
Project:         <PROJECT_NAME>
Database:        <DB_ENGINE — e.g. PostgreSQL 16 via Supabase>
ORM:             <ORM — e.g. Drizzle ORM with migrations via drizzle-kit>
Auth model:      <AUTH — e.g. Supabase auth.users; app users join via auth_user_id>
RLS:             <RLS — e.g. Supabase RLS enabled on all user-data tables>
User persona:    <ONE-LINE FROM 00-PROJECT.md>
Existing tables: <CURRENT SCHEMA — e.g. "users only; everything else greenfield">

# ACTION
<ONE PRECISE VERB from vocabulary.md, e.g. IMPLEMENT> the database schema for <FEATURE_DOMAINS>.

# TARGET
Files to create:
  src/lib/db/schema/<entity>.ts              (one file per top-level entity)
  src/lib/db/schema/index.ts                 (export aggregator)
  drizzle/migrations/<timestamp>_<name>.sql  (generated migration)
  src/lib/db/seed.ts                         (optional: seed data for dev)

Supabase-specific (if Supabase):
  supabase/migrations/<timestamp>_<name>.sql (RLS policies + indexes)

Do NOT modify:
  src/lib/db/client.ts        (db connection — read-only)
  drizzle.config.ts           (toolchain config — only via npm script)
  existing migrations         (NEVER edit a shipped migration; create a new one)

# CONSTRAINTS
- All entities have: id (uuid pk) + created_at + updated_at (timestamptz)
- All user-owned data has: user_id (fk → auth.users.id) NOT NULL
- All foreign keys have indexes (composite where queries demand it)
- All enums declared at SQL level (postgres enum) not via check constraints
- All money in integer cents (never float)
- All timestamps in UTC, stored as timestamptz
- RLS enabled on every user-data table with policies for SELECT/INSERT/UPDATE/DELETE
- Cascading: deleting a user cascades soft-deletes (set user_id NULL or mark deleted_at) — NEVER hard-delete user data without explicit policy
- Migration naming: timestamp_verb_noun.sql (e.g. 20260523_add_workouts_table.sql)
- One conceptual change per migration; no kitchen-sink migrations

# QUALITY
- Schema files use Drizzle declarative syntax (pgTable, with explicit column types)
- Every entity file exports: table + insert schema (zod) + select schema (zod)
- Migrations include both up + down (or are guaranteed forward-only via policy)
- Indexes documented inline with comment: which query they serve
- RLS policies documented inline: which user-action they authorize
- Test: schema generates without error (drizzle-kit generate runs clean)
- Test: migration applies on a fresh db and rolls back cleanly
- Performance: explain-analyze the 3 hottest queries documented in 00-PROJECT.md

# QUALITY WRAP

## Scope limiters
- Do not modify existing shipped migrations — additive only
- Do not introduce a new ORM or migration tool
- Do not bypass RLS by using service-role from server unless explicitly needed (document why)
- Keep schema files single-table — one entity per file

## Anti-pattern guards
- AVOID: untyped boundaries — schema is the contract; export zod schemas for app code to import
- AVOID: vague names — table names plural lowercase (workouts not Workout); column names snake_case
- AVOID: feature creep — one migration per concept
- AVOID: missing indexes on foreign keys (every fk gets an index unless documented otherwise)

## VERIFY
After implementation, run:
- `pnpm drizzle-kit generate` — must produce expected migration with no errors
- `pnpm drizzle-kit migrate` against a test db — must apply cleanly
- Inspect generated SQL — no unexpected DROP, no missing NOT NULL where required
- Test RLS: as user A, can SELECT own rows ✅ and CANNOT SELECT user B's rows ✅
- Run query plans on hot queries — index used, no seq scans on user-scoped queries
```

---

## VARIANT: schema-evolution file (when adding to existing schema)

Swap ACTION to `MIGRATE` or `EXTRACT` (if pulling a column into its own table).

Add to CONSTRAINTS:
- Backwards compatible: existing app code must continue working through the migration window
- Three-phase if breaking: (1) add new column, (2) backfill + dual-write, (3) drop old column
- Document the rollout sequence in a comment block at top of migration

## VARIANT: seed/fixture file

Swap ACTION to `GENERATE` seed data.

Add to QUALITY:
- Seed is deterministic (same input → same output)
- Seed only runs in dev/test envs (guard with NODE_ENV check)
- Seed produces enough volume to test pagination + index hits (≥100 rows in main tables)
