import sqlite3
import os
import json
import argparse
from matchms.importing import load_from_msp
from tqdm import tqdm

def create_database(db_path):
    """Creates a new SQLite database with the required spectra table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spectra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            precursor_mz REAL NOT NULL,
            peaks_json TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
    print(f"Database created/ensured at {db_path}")

def main(library_path, db_path):
    """Loads spectra from an MSP file and populates the SQLite database."""
    if not os.path.exists(library_path):
        print(f"Error: Library file not found at {library_path}")
        return

    create_database(db_path)

    print(f"Loading spectra from {library_path}. This may take a moment...")
    spectra = list(load_from_msp(library_path))
    print(f"Loaded {len(spectra)} spectra.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Populating database...")
    for spectrum in tqdm(spectra, desc="Building Library"):
        try:
            name = spectrum.get('name', 'Unknown')
            precursor_mz = float(spectrum.get('precursor_mz'))
            
            peaks_data = {
                'mz': spectrum.peaks.mz.tolist(),
                'intensities': spectrum.peaks.intensities.tolist()
            }
            peaks_json = json.dumps(peaks_data)

            cursor.execute('''
                INSERT INTO spectra (name, precursor_mz, peaks_json)
                VALUES (?, ?, ?)
            ''', (name, precursor_mz, peaks_json))
        except Exception as e:
            print(f"Skipping spectrum due to error: {e}")

    conn.commit()
    conn.close()
    print("Database population complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a clinical spectral library database.')
    parser.add_argument('--library', required=True, help='Path to the input .msp spectral library file.')
    parser.add_argument('--db', required=True, help='Path to the output SQLite database file.')
    args = parser.parse_args()
    main(args.library, args.db)

