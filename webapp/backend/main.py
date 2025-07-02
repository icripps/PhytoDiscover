
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import numpy as np
import os

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models ---
class SearchQuery(BaseModel):
    module: str
    compound_name: str

# --- Database Paths ---
DB_PATHS = {
    "Clinical Diagnostics": "clinical_library.db",
    "Food Safety": "food_safety_library.db",
    "Forensic Toxicology": "forensic_library.db"
}

# --- Helper Functions ---
def get_db_connection(module: str):
    db_file = DB_PATHS.get(module)
    if not db_file:
        raise HTTPException(status_code=404, detail="Module not found")

    db_path = os.path.join(os.path.dirname(__file__), db_file)
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail=f"Database file not found for module: {module}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "PhytoDiscover Backend is running"}

@app.post("/search")
def search_spectra(query: SearchQuery):
    conn = None
    try:
        # 1. Get reference embedding from the selected library
        conn = get_db_connection(query.module)
        cursor = conn.cursor()
        cursor.execute("SELECT embedding FROM spectra WHERE name = ?", (query.compound_name,))
        ref_row = cursor.fetchone()
        if not ref_row:
            raise HTTPException(status_code=404, detail=f"Compound '{query.compound_name}' not found in {query.module} library.")

        ref_embedding = np.frombuffer(ref_row['embedding'], dtype=np.float32)

        # 2. Get all embeddings from the same library to search against
        cursor.execute("SELECT id, name, precursor_mz, embedding FROM spectra")
        all_spectra = cursor.fetchall()

        # 3. Calculate similarities
        results = []
        for spectrum in all_spectra:
            target_embedding = np.frombuffer(spectrum['embedding'], dtype=np.float32)
            score = cosine_similarity(ref_embedding, target_embedding)

            # Add to results if score is high enough (e.g., > 0.7)
            if score > 0.7:
                results.append({
                    "id": spectrum['id'],
                    "name": spectrum['name'],
                    "mz": spectrum['precursor_mz'],
                    "score": score
                })

        # 4. Sort results by score (descending)
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

        return {"results": sorted_results[:10]} # Return top 10 matches

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)

