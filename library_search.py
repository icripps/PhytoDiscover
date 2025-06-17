import sqlite3
import pymzml.run
from matchms import Spectrum
from matchms.similarity import ModifiedCosine
import numpy as np
import argparse
import sys
import json
import csv
import os

def load_reference_library_from_db():
    """Loads all reference spectra from the knowledge base."""
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, precursor_mz, mz_values, intensity_values FROM compounds WHERE precursor_mz IS NOT NULL")
    
    reference_spectra = []
    for row in cursor.fetchall():
        name, precursor_mz, mz_values_json, intensity_values_json = row
        if not mz_values_json or not intensity_values_json:
            continue
        
        mz_values = np.array(json.loads(mz_values_json), dtype='float64')
        intensity_values = np.array(json.loads(intensity_values_json), dtype='float64')
        
        spectrum_obj = Spectrum(
            mz=mz_values,
            intensities=intensity_values,
            metadata={'precursor_mz': float(precursor_mz), 'compound_name': name}
        )
        reference_spectra.append(spectrum_obj)
        
    conn.close()
    print(f"Successfully loaded {len(reference_spectra)} reference spectra from the database.")
    return reference_spectra

def load_query_spectrum_from_mzml(file_path, query_id):
    """Loads a single query spectrum from an mzML file by its ID."""
    try:
        run = pymzml.run.Reader(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    for spec in run:
        if str(spec.ID) == str(query_id):
            if spec.ms_level == 2 and spec.selected_precursors:
                precursor_mz = spec.selected_precursors[0].get('mz')
                mz_array = np.array(spec.mz, dtype='float64')
                intensity_array = np.array(spec.i, dtype='float64')
                
                query_spectrum = Spectrum(
                    mz=mz_array,
                    intensities=intensity_array,
                    metadata={'precursor_mz': float(precursor_mz), 'id': str(spec.ID)}
                )
                print(f"Successfully loaded query spectrum ID {query_id} from {file_path}.")
                return query_spectrum
    
    print(f"Error: Could not find MS2 spectrum with ID '{query_id}' in {file_path}.")
    return None

def write_results_to_csv(output_file, query_spectrum, sorted_matches):
    """Writes the top search results to a CSV file."""
    header = ['query_id', 'query_mz', 'rank', 'match_compound_name', 'match_mz', 'similarity_score']
    query_meta = query_spectrum.metadata
    
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for i, (score, match) in enumerate(sorted_matches[:10]): # Write top 10 matches
                if score < 0.1: continue # Filter out very low scores
                match_meta = match.metadata
                row = [
                    query_meta['id'],
                    f"{query_meta['precursor_mz']:.4f}",
                    i + 1,
                    match_meta['compound_name'],
                    f"{match_meta['precursor_mz']:.4f}",
                    f"{score:.4f}"
                ]
                writer.writerow(row)
        print(f"\nResults successfully saved to {os.path.abspath(output_file)}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PhytoDiscover Library Search - Identify an unknown spectrum and save results.')
    parser.add_argument('-f', '--mzml_file', required=True, help='Path to the input .mzML file.')
    parser.add_argument('-i', '--query_id', required=True, help='The ID of the unknown spectrum to identify.')
    parser.add_argument('-o', '--output', default='search_results.csv', help='Path to the output CSV file (default: search_results.csv).')
    
    args = parser.parse_args()

    print('--- Starting Library Search ---')
    reference_library = load_reference_library_from_db()
    if not reference_library:
        print("Library is empty. Cannot perform search.")
        sys.exit(1)

    query_spectrum = load_query_spectrum_from_mzml(args.mzml_file, args.query_id)
    if not query_spectrum:
        sys.exit(1)

    print(f"\n--- Searching for matches for query spectrum ID {query_spectrum.metadata['id']} (m/z: {query_spectrum.metadata['precursor_mz']:.4f}) ---")
    modified_cosine = ModifiedCosine()
    scores_tuples = modified_cosine.matrix(queries=[query_spectrum], references=reference_library)
    scores = np.array([score_tuple[0] for score_tuple in scores_tuples[0]])

    sorted_matches = sorted(zip(scores, reference_library), key=lambda x: x[0], reverse=True)

    print('\n--- Top Library Hits (Console Preview) ---')
    if not any(s > 0.1 for s, m in sorted_matches):
        print("No significant matches found in the library.")
    else:
        for i, (score, match) in enumerate(sorted_matches[:5]):
            print(f"{i+1}. Compound: {match.metadata['compound_name']} --> Score: {score:.4f}")
    
    write_results_to_csv(args.output, query_spectrum, sorted_matches)
    
    print('\n--- Library Search Finished ---')
