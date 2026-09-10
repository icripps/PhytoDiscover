#!/usr/bin/env python3
"""Build the Plant / Botanical (Phyto) spectral library database for PhytoDiscover."""
import sqlite3
import os
import sys
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

# Plant / Botanical compound library
PLANTS = {
    'Quercetin': 'C15H10O7',
    'Rutin': 'C27H30O16',
    'Curcumin': 'C21H20O6',
    'Chlorophyll a': 'C55H72O5N4Mg',
    'Theobromine': 'C7H8N4O2',
    'Resveratrol': 'C14H12O3',
    'Caffeine': 'C8H10N4O2',
    'Apigenin': 'C15H10O5',
}

# Approximate monoisotopic masses (from literature / formula)
MASS_MAP = {
    'Quercetin': 302.0423,
    'Rutin': 610.1534,
    'Curcumin': 368.1260,
    'Chlorophyll a': 893.4790,
    'Theobromine': 180.0647,
    'Resveratrol': 228.0786,
    'Caffeine': 194.0804,
    'Apigenin': 270.0528,
}

def generate_plant_embedding(compound_name, precursor_mz):
    """Generate a synthetic binned spectral embedding (1000 bins, 0-1000 m/z)."""
    bins = np.arange(0, 1001, 1)
    # Synthetic peaks near precursor and a few fragment zones
    peaks = [
        max(0, int(precursor_mz * 0.7)),
        max(0, int(precursor_mz * 0.5)),
        max(0, int(precursor_mz * 0.3)),
        max(0, int(precursor_mz * 0.1)),
    ]
    intensities = np.zeros(len(bins) - 1, dtype=np.float32)
    for p in peaks:
        if p < len(intensities):
            intensities[p] += 1.0
            # Small neighborhood spread
            for offset in range(-2, 3):
                idx = p + offset
                if 0 <= idx < len(intensities):
                    intensities[idx] += 0.3
    # Normalize
    norm = np.linalg.norm(intensities)
    if norm > 0:
        intensities = intensities / norm
    return intensities

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(project_root, 'data', 'plant_library.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Compound reference table (compatible with library_manager)
    cursor.execute('''
        CREATE TABLE compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            formula TEXT NOT NULL,
            mass REAL NOT NULL
        )
    ''')

    # Spectral embeddings table (compatible with core_search.py)
    cursor.execute('''
        CREATE TABLE spectra (
            compound_name TEXT NOT NULL,
            precursor_mz REAL NOT NULL,
            embedding array NOT NULL
        )
    ''')

    # Insert compound references and synthetic spectral embeddings
    for name, formula in PLANTS.items():
        mass_val = MASS_MAP.get(name, 300.0)
        cursor.execute(
            "INSERT INTO compounds (name, formula, mass) VALUES (?, ?, ?)",
            (name, formula, mass_val)
        )

        # Synthetic spectral embedding using precursor mass
        embedding = generate_plant_embedding(name, mass_val)
        cursor.execute(
            "INSERT INTO spectra (compound_name, precursor_mz, embedding) VALUES (?, ?, ?)",
            (name, mass_val, embedding)
        )

    conn.commit()
    conn.close()
    print(f"Plant / Botanical library built at {db_path}")
    print(f"  Compounds: {len(PLANTS)}")
    print(f"  Spectral entries: {len(PLANTS)}")
