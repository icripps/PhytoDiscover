import sqlite3
import numpy as np
import io
from matchms.importing import load_from_mzml
from matchms import Spectrum
from matchms.similarity import CosineGreedy

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)

def generate_embedding(spectrum):
    """
    Placeholder function to generate a spectral embedding.
    In a real application, this would be a trained neural network.
    """
    # Simple embedding: bin the spectrum and use bin intensities
    bins = np.arange(0, 1001, 1)
    binned_intensities, _ = np.histogram(spectrum.peaks.mz, bins=bins, weights=spectrum.peaks.intensities)
    # Normalize the vector to have a length of 1 (unit vector)
    norm = np.linalg.norm(binned_intensities)
    if norm == 0:
        return np.zeros(len(bins) - 1, dtype=np.float32) # Return zero vector if spectrum is empty
    embedding = binned_intensities / norm
    return embedding.astype(np.float32)

def search_spectrum(query_spectrum, db_path='phytodiscover_core.db'):
    """
    Searches for a single query spectrum against the library.
    """
    query_embedding = generate_embedding(query_spectrum)
    
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute("SELECT compound_name, precursor_mz, embedding FROM spectra")
    library_spectra = cursor.fetchall()
    conn.close()
    
    if not library_spectra:
        return []

    best_match = None
    highest_score = -1.0

    for name, mz, lib_embedding in library_spectra:
        # Calculate cosine similarity
        # np.dot is faster for 1D arrays
        score = np.dot(query_embedding, lib_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(lib_embedding))

        if score > highest_score:
            highest_score = score
            best_match = {
                "compound_name": name,
                "precursor_mz": mz,
                "score": float(score)
            }
            
    return [best_match] if best_match else []

def run_search(compound_name, mzml_file_path, db_path='phytodiscover_core.db'):
    """
    Main function to run the search for a compound in an mzML file.
    """
    try:
        spectra = list(load_from_mzml(mzml_file_path))
    except Exception as e:
        return {"error": f"Failed to load mzML file: {e}"}

    if not spectra:
        return {"error": "No spectra found in the provided mzML file."}
        
    # In a real app, you'd find the spectrum that best matches the compound's expected mass.
    # For this demo, we'll just use the most intense spectrum as the query.
    query_spectrum = sorted(spectra, key=lambda s: s.get('precursor_mz', 0), reverse=True)[0]
    query_spectrum.set("compound_name", compound_name)

    results = search_spectrum(query_spectrum, db_path)
    
    return {
        "query": {
            "compound_name": compound_name,
            "precursor_mz": query_spectrum.get("precursor_mz")
        },
        "matches": results
    }
