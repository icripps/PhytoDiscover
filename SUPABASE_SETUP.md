# Supabase Setup (Project Already Connected)

1. **Apply schema:** Go to Supabase Dashboard > SQL Editor > paste contents of `db/unified_schema.sql`. Enable RLS on all exposed tables.
2. **Secrets:** Add `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` to GitHub repo Secrets (Settings > Secrets and variables > Actions) and to your hosting environment.
3. **Auth:** Replace `webapp/backend/auth.py` JWT with `supabase-py` auth verification (`supabase.auth.get_user`) once DB is live.
4. **Migrate data:** Run `python scripts/migrate_sqlite_to_postgres.py` after connecting `psql` to your Supabase DB URI (found in Supabase Dashboard > Project Settings > Database).
5. **Workflows:** `.github/workflows/ci.yml`, `db-migrate.yml`, `deploy.yml` are ready; trigger `db-migrate` after schema updates.
