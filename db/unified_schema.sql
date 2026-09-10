-- PhytoDiscover Unified SaaS Schema (Postgres / Supabase)
-- Designed for multi-tenant isolation, spectral library management, and billing/submission tracking.

-- Modules define the analysis domains
CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,            -- "Plant / Botanical", "Clinical Diagnostics", etc.
    domain TEXT NOT NULL,                  -- "plant", "clinical", "food", "forensic"
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Compound reference library (unified across modules)
CREATE TABLE IF NOT EXISTS compound_library (
    id SERIAL PRIMARY KEY,
    module_id INT REFERENCES modules(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    formula TEXT NOT NULL,
    mass REAL NOT NULL,
    reference_embedding REAL[] ,            -- 1000-bin embedding array (Postgres array)
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(module_id, name)
);

-- Spectral embeddings table (real spectra from MGF/mzML)
CREATE TABLE IF NOT EXISTS spectra (
    id SERIAL PRIMARY KEY,
    compound_id INT REFERENCES compound_library(id) ON DELETE CASCADE,
    precursor_mz REAL NOT NULL,
    embedding REAL[] NOT NULL,              -- binned intensities (1000 bins)
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Tenants (multi-tenant SaaS isolation)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free','pro','enterprise')),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Users linked to tenants (use with Supabase Auth or custom JWT)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id TEXT UNIQUE NOT NULL,     -- Supabase auth.users.id or custom JWT sub
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner','admin','member')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Submissions / usage tracking (SaaS billing analytics)
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    module_id INT REFERENCES modules(id) ON DELETE SET NULL,
    compound_name TEXT,
    mzml_file TEXT,
    best_match_name TEXT,
    best_score REAL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Subscriptions / billing events
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active','canceled','past_due','unpaid')),
    tier TEXT NOT NULL DEFAULT 'free',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS: All exposed tables require row-level security
ALTER TABLE compound_library ENABLE ROW LEVEL SECURITY;
ALTER TABLE spectra ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Tenant isolation via users.tenant_id -> submissions.tenant_id
CREATE POLICY tenant_submissions_isolation ON submissions
    FOR ALL USING (tenant_id = current_setting('app.current_tenant')::UUID);

CREATE POLICY tenant_spectra_read ON spectra
    FOR SELECT USING (
        compound_id IN (
            SELECT id FROM compound_library
            WHERE module_id IN (
                SELECT id FROM modules WHERE is_active = true
            )
        )
    );

-- Note: In production, link current_tenant from JWT (app_metadata / raw_app_meta_data)
-- Never use user_metadata for authorization per Supabase security checklist.
