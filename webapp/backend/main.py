from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import subprocess

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
core_path = os.path.join(project_root, 'phyto_discover_core')
sys.path.insert(0, core_path)

try:
    from core_search import search_spectra
except ImportError as e:
    raise ImportError(f"Could not import 'core_search'. Ensure it is in the correct path: {core_path}. Error: {e}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    module: str
    compound_name: str
    mzml_file: str

def get_db_path(module: str):
    db_filename = ""
    if module == "clinical":
        db_filename = "clinical_reference.db"
    elif module == "food_safety":
        db_filename = "pesticide_library.db"
    else:
        return None
    return os.path.join(project_root, 'data', db_filename)

def get_mzml_path(filename: str):
    return os.path.join(project_root, 'data', filename)

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
            check=True
        )
        
        print("Search script stdout:", result.stdout)
        print("Search script stderr:", result.stderr)
        
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

@app.get("/")
def read_root():
    return {"message": "PhytoDiscover Backend is running"}
