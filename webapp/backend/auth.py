"""Simple JWT auth middleware for SaaS multi-tenant mode.
Production: replace with Supabase Auth JWT verification.
"""
import os, jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Auth middleware for SaaS multi-tenant mode
# Production swap: replace JWT secret with supabase-py auth.getUser()
# Once connected to Supabase DB via cli/connection, use:
#   from supabase import create_client
#   supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
#   user = supabase.auth.get_user(token)

secret = os.getenv("PHYTO_JWT_SECRET", "dev-secret-change-in-prod")
security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = None):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return payload  # expected: {"sub": user_id, "tenant_id": ..., "tier": ...}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_tenant(token_payload: dict) -> str:
    tenant = token_payload.get("tenant_id")
    if not tenant:
        # Fallback: derive from user record (production: query DB)
        tenant = "default-tenant"
    return tenant
