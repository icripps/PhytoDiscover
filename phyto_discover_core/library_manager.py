import sqlite3
import numpy as np
import io

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)

def create_database(db_path='phytodiscover_core.db'):
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS spectra")
    cursor.execute('''
        CREATE TABLE spectra (
            id INTEGER PRIMARY KEY,
            compound_name TEXT NOT NULL UNIQUE,
            precursor_mz REAL NOT NULL,
            embedding array
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{db_path}' created successfully with 'spectra' table.")

def add_spectrum(db_path, compound_name, precursor_mz, embedding):
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO spectra (compound_name, precursor_mz, embedding) VALUES (?, ?, ?)",
                       (compound_name, precursor_mz, embedding))
        conn.commit()
        print(f"Added '{compound_name}' to the library.")
    except sqlite3.IntegrityError:
        print(f"Compound '{compound_name}' already exists in the library. Skipping.")
    finally:
        conn.close()

if __name__ == '__main__':
    DB_FILE = 'phytodiscover_core.db'
    print("Initializing database and library...")
    create_database(DB_FILE)
    
    # Add some example compounds
    add_spectrum(DB_FILE, 'Caffeine', 194.08, np.random.rand(1, 1024).astype(np.float32))
    add_spectrum(DB_FILE, 'Aspirin', 180.04, np.random.rand(1, 1024).astype(np.float32))
    add_spectrum(DB_FILE, 'Metformin', 129.1, np.random.rand(1, 1024).astype(np.float32))
    add_spectrum(DB_FILE, 'LSD', 323.19, np.random.rand(1, 1024).astype(np.float32))
    
    print("Library setup complete.")
