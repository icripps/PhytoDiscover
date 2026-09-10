"""Supabase auth swap — replace JWT secret with live DB verification."""
import os

def get_supabase_client():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        return create_client(url, key)
    except Exception:
        return None

def verify_supabase_token(token: str):
    client = get_supabase_client()
    if not client:
        return None
    try:
        user = client.auth.get_user(token)
        return {"user_id": user.user.id, "email": user.user.email, "tenant_id": user.user.app_metadata.get("tenant_id") if hasattr(user.user, 'app_metadata') else None}
    except Exception:
        return None
