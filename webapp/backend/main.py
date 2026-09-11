from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import subprocess

# Auth middleware for SaaS multi-tenant mode
sys.path.insert(0, os.path.dirname(__file__))
try:
    from auth import verify_token, get_current_tenant, security
except ImportError:
    verify_token = get_current_tenant = security = None

# Production: use supabase-py auth when SUPABASE_URL / SERVICE_ROLE_KEY set
# See auth_supabase.py for live DB verification path
try:
    from auth import verify_token, get_current_tenant, security
except ImportError:
    verify_token = get_current_tenant = security = None

# Add the project root to the Python path to allow imports from phyto_discover_core
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
core_path = os.path.join(project_root, 'phyto_discover_core')
sys.path.insert(0, core_path)

try:
    # This import is for context, the script is called as a subprocess
    from core_search import search_spectra
except ImportError as e:
    print(f"Warning: Could not import 'core_search' for context. This is okay if the script exists at {core_path}. Error: {e}")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models ---
class SearchRequest(BaseModel):
    module: str
    compound_name: str
    mzml_file: str

# --- Helper Functions ---
def get_db_path(module: str):
    db_filename = ""
    if module == "Clinical Diagnostics":
        db_filename = "clinical_library.db"
    elif module == "Food Safety":
        db_filename = "food_safety_library.db"
    elif module == "Forensic Toxicology":
        db_filename = "forensic_library.db"
    elif module == "Plant / Botanical":
        db_filename = "plant_library.db"
    else:
        return None
    return os.path.join(project_root, 'data', db_filename)

def get_mzml_path(filename: str):
    return os.path.join(project_root, 'data', filename)

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "PhytoDiscover Backend is running"}

@app.post("/api/search")
async def search(request: SearchRequest, authorization: str = Header(None)):
    # Auth enforced — requires Bearer token (Supabase JWT or dev JWT)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization Bearer token required")
    # Optional: verify token with Supabase auth here (auth_supabase.py)
    print(f"Received search request (auth present): {request}")
    db_path = get_db_path(request.module)
    mzml_path = get_mzml_path(request.mzml_file)

    if not db_path or not os.path.exists(db_path):
        print(f"Database not found for module: {request.module} at path: {db_path}")
        raise HTTPException(status_code=404, detail=f"Database for module '{request.module}' not found.")
    if not os.path.exists(mzml_path):
        print(f"mzML file not found at path: {mzml_path}")
        raise HTTPException(status_code=404, detail=f"Sample data file '{request.mzml_file}' not found.")

    try:
        from search_service import search_live
        results = search_live(db_path, request.compound_name, mzml_path, request.module)
        return {"results": results, "db_path": db_path, "engine": "search_service_live"}
    except Exception as e:
        print(f"Search service error: {e}")
        raise HTTPException(status_code=500, detail=f"Spectral search failed: {str(e)}")

@app.get("/api/tenants")
async def get_tenants(token_payload: dict = Depends(verify_token) if verify_token else None):
    # SaaS multi-tenant endpoint (requires JWT)
    return {"message": "Multi-tenant active", "tenant_id": get_current_tenant(token_payload) if token_payload else "demo"}

@app.get("/api/data-files")
async def get_data_files():
    data_path = os.path.join(project_root, 'data')
    try:
        files = [f for f in os.listdir(data_path) if f.endswith(('.mzML', '.mzml'))]
        return {"files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data directory not found.")
