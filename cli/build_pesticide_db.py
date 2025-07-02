import sys
import os

# Add the core logic path to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
core_path = os.path.join(project_root, 'phyto_discover_core')
sys.path.insert(0, core_path)

# Import the correct functions from the user's library manager
from library_manager import build_database, add_compound_to_db

# Define the list of pesticides to add
PESTICIDES = {
    'Glyphosate': 'C3H8NO5P',
    'Atrazine': 'C8H14ClN5',
    'Malathion': 'C10H19O6PS2',
    'Chlorpyrifos': 'C9H11Cl3NO3PS',
    'DDT': 'C14H9Cl5'
}

if __name__ == '__main__':
    db_path = os.path.join(project_root, 'data', 'pesticide_library.db')
    print(f"--- Building Food Safety Database at {db_path} ---")

    # Create a new, empty database
    build_database(db_path)

    # Add each pesticide to the database
    for name, formula in PESTICIDES.items():
        add_compound_to_db(db_path, name, formula)

    print("\n--- Food Safety database build complete. ---")
