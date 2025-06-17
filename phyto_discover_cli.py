import sqlite3
import pymzml.run
from matchms import Spectrum
from matchms.similarity import ModifiedCosine
import numpy as np
import argparse
import sys

def load_spectra_from_mzml(file_path):
    """Loads all MS2 spectra from an mzML file using pymzml."""
    try:
        run = pymzml.run.Reader(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    spectra = []
    for spec in run:
        if spec.ms_level == 2 and spec.selected_precursors:
            try:
                mz_array = spec.mz
                intensity_array = spec.i
                if len(mz_array) == 0: continue
                precursor_mz = spec.selected_precursors[0].get('mz')
                spectrum_obj = Spectrum(
                    mz=np.array(mz_array, dtype='float64'),
                    intensities=np.array(intensity_array, dtype='float64'),
                    metadata={'precursor_mz': float(precursor_mz), 'id': str(spec.ID)})
                spectra.append(spectrum_obj)
            except (IndexError, TypeError, KeyError, ValueError):
                continue
    return spectra

def find_similar_spectra(query_spectrum, reference_spectra):
    """Finds and prints the most similar spectra to a query spectrum."""
    print(f"\n--- Comparing query (ID: {query_spectrum.metadata['id']}, m/z: {query_spectrum.metadata['precursor_mz']:.4f}) against {len(reference_spectra)} references ---")
    modified_cosine = ModifiedCosine()
    scores_tuples = modified_cosine.matrix(queries=[query_spectrum], references=reference_spectra)
    
    scores = np.array([score_tuple[0] for score_tuple in scores_tuples[0]])

    sorted_matches = sorted(zip(scores, reference_spectra), key=lambda x: x[0], reverse=True)
    
    print('\n--- Top 5 Most Similar Spectra ---')
    # Exclude the self-match (always first) by starting from the second result
    for i, (score, match) in enumerate(sorted_matches[1:6]):
        print(f"{i+1}. Match with Spectrum ID: {match.metadata['id']} (m/z: {match.metadata['precursor_mz']:.4f}) --> Score: {score:.4f}")

def phyto_discover_pipeline(query_name, mzml_file, target_mz, tolerance=0.02):
    """The main pipeline for the PhytoDiscover framework."""
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM compounds WHERE name = ?", (query_name,))
    if not cursor.fetchone():
        print(f"Error: Query compound '{query_name}' not found in knowledge_base.db.")
        return
    print(f"Successfully validated '{query_name}' in the knowledge base.")

    all_spectra = load_spectra_from_mzml(mzml_file)
    if not all_spectra:
        print(f"Error: No valid MS2 spectra loaded from {mzml_file}.")
        return
    print(f"Successfully loaded {len(all_spectra)} MS2 spectra from {mzml_file}.")

    query_spectrum = None
    for spec in all_spectra:
        if abs(spec.get('precursor_mz') - target_mz) <= tolerance:
            query_spectrum = spec
            print(f"Found experimental query spectrum: ID {spec.get('id')} with m/z {spec.get('precursor_mz'):.4f}")
            break
    
    if not query_spectrum:
        print(f"Error: Could not find a spectrum matching m/z {target_mz:.4f} within the tolerance.")
        return

    find_similar_spectra(query_spectrum, all_spectra)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PhytoDiscover CLI - Find similar spectra based on a query compound.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-c', '--compound_name',
        type=str,
        required=True,
        help='The name of the compound to query in the knowledge base.'
    )
    parser.add_argument(
        '-f', '--mzml_file',
        type=str,
        required=True,
        help='Path to the input .mzML file.'
    )
    parser.add_argument(
        '-m', '--target_mz',
        type=float,
        required=True,
        help='The target precursor m/z to find the query spectrum.'
    )
    parser.add_argument(
        '-t', '--tolerance',
        type=float,
        default=0.02,
        help='The m/z tolerance for finding the query spectrum (default: 0.02).'
    )
    
    args = parser.parse_args()

    print('--- Starting PhytoDiscover Pipeline (CLI Mode) ---')
    phyto_discover_pipeline(args.compound_name, args.mzml_file, args.target_mz, args.tolerance)
