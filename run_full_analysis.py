import re
import csv
import argparse
import pymzml.run
from matchms import Spectrum
from matchms.similarity import ModifiedCosine
import numpy as np

def get_lsd_spectrum(record_file):
    with open(record_file, 'r') as f:
        content = f.read()
    precursor_match = re.search(r'PRECURSOR_M/Z (\d+\.\d+)', content)
    peak_matches = re.findall(r'(\d+\.\d+)\s+(\d+\.?\d*)\s+(\d+)', content)
    if not precursor_match or not peak_matches:
        return None
    precursor_mz = float(precursor_match.group(1))
    mzs = [float(match[0]) for match in peak_matches]
    intensities = [float(match[1]) for match in peak_matches]
    return Spectrum(mz=np.array(mzs), intensities=np.array(intensities), metadata={'precursor_mz': precursor_mz, 'compound_name': 'LSD'})

def get_reference_peptide_spectrum(mzml_file, target_mz=725.36, tolerance=0.02):
    run = pymzml.run.Reader(mzml_file)
    for spec in run:
        if spec.ms_level == 2 and spec.selected_precursors:
            precursor_mz = float(spec.selected_precursors[0].get('mz'))
            if abs(precursor_mz - target_mz) <= tolerance:
                return Spectrum(mz=np.array(spec.mz), intensities=np.array(spec.i), metadata={'precursor_mz': precursor_mz, 'compound_name': 'Reference_Peptide_725'})
    return None

def load_query_spectra(mzml_file):
    run = pymzml.run.Reader(mzml_file)
    queries = []
    for spec in run:
        if spec.ms_level == 2 and len(spec.mz) > 0 and spec.selected_precursors:
            try:
                queries.append(Spectrum(mz=np.array(spec.mz), intensities=np.array(spec.i), metadata={'precursor_mz': float(spec.selected_precursors[0].get('mz')), 'id': str(spec.ID)}))
            except (IndexError, TypeError):
                continue
    return queries

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a full, in-memory analysis.')
    parser.add_argument('-f', '--mzml_file', required=True, help='Path to the input mzML file.')
    parser.add_argument('-o', '--output', default='final_report.csv', help='Path for the output CSV report.')
    parser.add_argument('-t', '--threshold', type=float, default=0.85, help='Similarity score threshold.')
    args = parser.parse_args()

    print("--- Building In-Memory Reference Library ---")
    reference_spectra = []
    lsd_spec = get_lsd_spectrum('lsd_record.txt')
    if lsd_spec: reference_spectra.append(lsd_spec); print("Loaded LSD spectrum.")
    ref_pep_spec = get_reference_peptide_spectrum(args.mzml_file)
    if ref_pep_spec: reference_spectra.append(ref_pep_spec); print("Loaded Reference_Peptide_725 spectrum.")

    print(f"\n--- Loading Query Spectra from {args.mzml_file} ---")
    query_spectra = load_query_spectra(args.mzml_file)
    print(f"Loaded {len(query_spectra)} query spectra.")

    if not reference_spectra or not query_spectra:
        print("\nError: Could not build library or load queries. Exiting.")
        exit()

    print(f"\n--- Searching for matches with score > {args.threshold} ---")
    similarity = ModifiedCosine()
    scores = similarity.matrix(query_spectra, reference_spectra)
    hits = []
    for i, query_spec in enumerate(query_spectra):
        # Corrected logic for handling the 2D array of tuples
        similarity_scores = [s[0] for s in scores[i, :]]
        if not similarity_scores:
            continue
        best_match_idx = np.argmax(similarity_scores)
        best_score = similarity_scores[best_match_idx]
        
        if best_score >= args.threshold:
            best_match_ref = reference_spectra[best_match_idx]
            hits.append({
                'query_id': query_spec.get('id'),
                'query_mz': f"{query_spec.get('precursor_mz'):.4f}",
                'match_compound_name': best_match_ref.get('compound_name'),
                'match_mz': f"{best_match_ref.get('precursor_mz'):.4f}",
                'similarity_score': f"{best_score:.4f}"
            })

    print(f"Found {len(hits)} high-confidence hits.")

    if hits:
        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=hits[0].keys())
            writer.writeheader()
            writer.writerows(hits)
        print(f"--- Final report saved to {args.output} ---")
    else:
        print("--- No significant matches found. ---")
