from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import numpy as np

# Add the parent directory (backend) to the Python path
# This allows us to import from core_search and library_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_search import run_search
from library_manager import create_database, add_spectrum

app = FastAPI(
    title="PhytoDiscover API",
    description="API for searching and analyzing phytochemical mass spectra.",
    version="1.0.0",
)

# Configure CORS to allow requests from the frontend (running on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The address of your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = 'phytodiscover_core.db'

@app.on_event("startup")
def on_startup():
    """
    Initialize the database and populate it with some data if it doesn't exist.
    This runs once when the server starts.
    """
    if not os.path.exists(DB_FILE):
        print(f"Database not found at {DB_FILE}. Creating and populating...")
        create_database(DB_FILE)
        # Add some example compounds with random embeddings for demonstration
        add_spectrum(DB_FILE, 'Caffeine', 194.08, np.random.rand(1000).astype(np.float32))
        add_spectrum(DB_FILE, 'Aspirin', 180.04, np.random.rand(1000).astype(np.float32))
        add_spectrum(DB_FILE, 'Metformin', 129.1, np.random.rand(1000).astype(np.float32))
        add_spectrum(DB_FILE, 'LSD', 323.19, np.random.rand(1000).astype(np.float32))
        print("Database initialized.")
    else:
        print("Database already exists.")

@app.get("/api/search")
def search(compound_name: str, file_path: str):
    """
    API endpoint to perform a search.
    It takes a compound name and a file path as query parameters.
    """
    # The file path is relative to the project's root directory (PhytoDiscover_App)
    # The backend runs from the 'backend' directory, so we need to go up one level.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_file_path = os.path.join(project_root, '..', file_path)

    if not os.path.exists(full_file_path):
        raise HTTPException(status_code=404, detail=f"File not found at the specified path: {full_file_path}")
        
    results = run_search(compound_name, full_file_path, DB_FILE)
    if "error" in results:
        raise HTTPException(status_code=400, detail=results["error"])
    
    return results

@app.get("/")
def read_root():
    return {"message": "Welcome to the PhytoDiscover API"}

