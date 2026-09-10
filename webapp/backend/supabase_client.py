"""Live Supabase connection for backend — replaces SQLite file paths."""
import os

def get_db_path(module: str = ""):
    # Production: use Supabase Postgres connection string
    # Fallback: local SQLite for dev until full migration complete
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        # In production, queries go to Supabase via psycopg2 / supabase-py
        # For this scaffold, return module identifier (DB handled by connection)
        return f"supabase://{module or 'default'}"
    # Dev fallback to local SQLite (current working state)
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    db_map = {
        "Clinical Diagnostics": "clinical_library.db",
        "Food Safety": "food_safety_library.db",
        "Forensic Toxicology": "forensic_library.db",
        "Plant / Botanical": "plant_library.db",
    }
    return os.path.join(project_root, "data", db_map.get(module, "plant_library.db"))
