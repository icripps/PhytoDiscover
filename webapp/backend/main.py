from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import subprocess

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
async def search(request: SearchRequest):
    print(f"Received search request: {request}")
    db_path = get_db_path(request.module)
    mzml_path = get_mzml_path(request.mzml_file)

    if not db_path or not os.path.exists(db_path):
        print(f"Database not found for module: {request.module} at path: {db_path}")
        raise HTTPException(status_code=404, detail=f"Database for module '{request.module}' not found.")
    if not os.path.exists(mzml_path):
        print(f"mzML file not found at path: {mzml_path}")
        raise HTTPException(status_code=404, detail=f"Sample data file '{request.mzml_file}' not found.")

    try:
        # Use the system's python interpreter to run the core search script
        command = [
            sys.executable,
            os.path.join(core_path, 'core_search.py'),
            '--db_path', db_path,
            '--mzml_file', mzml_path,
            '--compound_name', request.compound_name
        ]
        print(f"Executing command: {' '.join(command)}")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=60 # Add a timeout for safety
        )

        print("Search script stdout:", result.stdout)
        print("Search script stderr:", result.stderr)

        # The script is expected to return a JSON string or similar structured text
        return {"results": result.stdout.strip()}

    except subprocess.CalledProcessError as e:
        print(f"Error executing search script: {e}")
        print(f"Stderr: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Error during spectral search: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")

@app.get("/api/data-files")
async def get_data_files():
    data_path = os.path.join(project_root, 'data')
    try:
        files = [f for f in os.listdir(data_path) if f.endswith(('.mzML', '.mzml'))]
        return {"files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data directory not found.")
