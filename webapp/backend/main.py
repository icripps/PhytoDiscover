import sys
import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- Path Setup ---
# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# --- Core PhytoDiscover Imports ---
from phyto_discover_core import core_search, library_manager

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class SearchRequest(BaseModel):
    compound_name: str

class SearchResult(BaseModel):
    query_id: str
    match_id: str
    score: float
    mz_query: float
    mz_match: float

class ClinicalSearchResult(BaseModel):
    name: str
    precursor_mz: float

# --- Database and File Paths ---
DB_PATH = os.path.join(project_root, 'data', 'phyto_discover_core.db')
DATA_FILE_PATH = os.path.join(project_root, 'data', 'small.pwiz.1.1.mzML')
CLINICAL_DB_PATH = os.path.join(project_root, 'phyto_discover_clinical', 'data', 'clinical_knowledge_base.db')

# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    # Ensure the original database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Creating...")
        library_manager.build_database(DB_PATH)
        library_manager.add_compound_to_db(DB_PATH, 'Aspirin', 'C9H8O4')
        print("Database created.")
    else:
        print(f"Original database found at {DB_PATH}.")
    
    # Check for the clinical database
    if not os.path.exists(CLINICAL_DB_PATH):
        print(f"CRITICAL: Clinical database not found at {CLINICAL_DB_PATH}. The /api/clinical_search endpoint will fail.")
    else:
        print(f"Clinical database found at {CLINICAL_DB_PATH}.")

# --- NEW: Clinical Search Logic ---
def search_clinical_db_by_mz(query_mz: float, tolerance: float):
    """Searches the clinical database for a precursor m/z within a given tolerance."""
    conn = sqlite3.connect(CLINICAL_DB_PATH)
    cursor = conn.cursor()
    min_mz = query_mz - tolerance
    max_mz = query_mz + tolerance
    cursor.execute(
        "SELECT name, precursor_mz FROM spectra WHERE precursor_mz BETWEEN ? AND ?",
        (min_mz, max_mz)
    )
    results = cursor.fetchall()
    conn.close()
    # Convert list of tuples to list of dicts to match Pydantic model
    return [{"name": row[0], "precursor_mz": row[1]} for row in results]

# --- API Endpoints ---

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from the PhytoDiscover Backend!"}

@app.post("/api/search", response_model=list[SearchResult])
def search_compound(request: SearchRequest):
    print(f"Received original search request for: {request.compound_name}")
    try:
        results_df = core_search.search_for_compound(
            db_path=DB_PATH,
            compound_name=request.compound_name,
            mzml_file=DATA_FILE_PATH,
            tolerance=0.1
        )
        if results_df is None or results_df.empty:
            return []
        results_list = results_df.to_dict(orient='records')
        return [SearchResult(**item) for item in results_list]
    except Exception as e:
        print(f"An error occurred during original search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clinical_search", response_model=list[ClinicalSearchResult])
def search_clinical(
    mz: float = Query(..., description="The query m/z value to search for."),
    tolerance: float = Query(0.1, description="The search tolerance (+/-).")
):
    print(f"Received clinical search for m/z: {mz} +/- {tolerance}")
    try:
        matches = search_clinical_db_by_mz(query_mz=mz, tolerance=tolerance)
        return matches
    except Exception as e:
        print(f"An error occurred during clinical search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

