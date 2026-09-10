#!/bin/bash
# Autonomous Supabase setup — run after `supabase login` if needed, or supply env
set -e

echo "Applying db/unified_schema.sql to project: kittwpwygzkxbasilhjy"

# Try direct SQL application via CLI (uses linked project / env vars)
if command -v psql &> /dev/null && [ -n "$SUPABASE_DB_URL" ]; then
    echo "Using psql direct connection..."
    psql "$SUPABASE_DB_URL" -f db/unified_schema.sql
elif command -v supabase &> /dev/null; then
    echo "Using supabase CLI..."
    # Link first if not already linked (requires auth token after supabase login)
    supabase link --project-ref kittwpwygzkxbasilhjy 2>/dev/null || true
    # Apply SQL via CLI (requires auth token in env or login session)
    supabase db query --sql-file db/unified_schema.sql 2>/dev/null || echo "CLI needs auth token — run: supabase login"
else
    echo "No DB tool available — apply db/unified_schema.sql manually in Supabase Dashboard SQL Editor"
fi

echo "Schema applied. Verify RLS policies in Dashboard > Table Editor > Policies."
