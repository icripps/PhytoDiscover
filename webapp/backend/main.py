
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Add project root to the Python path to allow importing from phyto_discover_core
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from phyto_discover_core import core_search, library_manager

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The origin of the frontend app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models for request and response
class SearchRequest(BaseModel):
    compound_name: str

class SearchResult(BaseModel):
    query_id: str
    match_id: str
    score: float
    mz_query: float
    mz_match: float

# Define paths relative to the project root
DB_PATH = os.path.join(project_root, 'data', 'phyto_discover_core.db')
DATA_FILE_PATH = os.path.join(project_root, 'data', 'small.pwiz.1.1.mzML')

@app.on_event("startup")
def startup_event():
    # Ensure the library and database exist on startup
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Creating and populating...")
        library_manager.build_database(DB_PATH)
        # Add some default compounds for demonstration
        library_manager.add_compound_to_db(DB_PATH, 'Aspirin', 'C9H8O4')
        library_manager.add_compound_to_db(DB_PATH, 'Metformin', 'C4H11N5')
        print("Database created.")
    else:
        print(f"Database found at {DB_PATH}.")

@app.post("/api/search", response_model=list[SearchResult])
def search_compound(request: SearchRequest):
    print(f"Received search request for: {request.compound_name}")
    try:
        results_df = core_search.search_for_compound(
            db_path=DB_PATH,
            compound_name=request.compound_name,
            mzml_file=DATA_FILE_PATH,
            tolerance=0.1
        )

        if results_df is None or results_df.empty:
            return []

        # Convert DataFrame to list of Pydantic models
        results_list = results_df.to_dict(orient='records')
        return [SearchResult(**item) for item in results_list]

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from the PhytoDiscover Backend!"}

