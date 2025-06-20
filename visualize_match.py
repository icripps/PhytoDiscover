import re
import argparse
import pymzml.run
from matchms import Spectrum
from matchms.similarity import ModifiedCosine
import numpy as np
import matplotlib.pyplot as plt

# --- Data Loading Functions (reused and adapted) ---

def get_lsd_spectrum(record_file='lsd_record.txt'):
    with open(record_file, 'r') as f:
        content = f.read()
    precursor_match = re.search(r'PRECURSOR_M/Z (\\d+\\.\\d+)', content)
    peak_matches = re.findall(r'(\\d+\\.\\d+)\\s+(\\d+\\.?\\d*)\\s+(\\d+)', content)
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

def get_query_spectrum_by_id(mzml_file, query_id):
    run = pymzml.run.Reader(mzml_file)
    for spec in run:
        if str(spec.ID) == query_id:
            return Spectrum(mz=np.array(spec.mz), intensities=np.array(spec.i), metadata={'precursor_mz': float(spec.selected_precursors[0].get('mz')), 'id': str(spec.ID)})
    return None

# --- Plotting Function ---

def plot_mirror(spec_top, spec_bottom, output_file):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot top spectrum (query)
    stem_top = ax.stem(spec_top.mz, spec_top.intensities, linefmt='b-', markerfmt=' ')
    plt.setp(stem_top[0], 'color', 'blue', 'linewidth', 1.5)

    # Plot bottom spectrum (reference)
    stem_bottom = ax.stem(spec_bottom.mz, -spec_bottom.intensities, linefmt='r-', markerfmt=' ')
    plt.setp(stem_bottom[0], 'color', 'red', 'linewidth', 1.5)

    # Calculate similarity score
    similarity = ModifiedCosine()
    score = similarity.pair(spec_top, spec_bottom)
    # CORRECTED LINE:
    score_val = score['score']

    # Formatting
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xlabel('m/z')
    ax.set_ylabel('Intensity')
    ax.set_title(f"Query ID: {spec_top.get('id')} vs. Ref: {spec_bottom.get('compound_name')}\nModified Cosine Score: {score_val:.4f}")
    ax.get_yaxis().set_ticks([])
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.savefig(output_file, dpi=300)
    print(f"Mirror plot saved to {output_file}")

# --- Main Execution ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a mirror plot for a spectral match.')
    parser.add_argument('--mzml_file', required=True, help='Path to the input mzML file.')
    parser.add_argument('--query_id', required=True, help='ID of the query spectrum in the mzML file.')
    parser.add_argument('--reference_name', required=True, choices=['LSD', 'Reference_Peptide_725'], help='Name of the reference compound.')
    parser.add_argument('--output', default='mirror_plot.png', help='Path for the output PNG image.')
    args = parser.parse_args()

    print("--- Loading Spectra ---")
    query_spec = get_query_spectrum_by_id(args.mzml_file, args.query_id)
    
    reference_spec = None
    if args.reference_name == 'LSD':
        reference_spec = get_lsd_spectrum()
    elif args.reference_name == 'Reference_Peptide_725':
        reference_spec = get_reference_peptide_spectrum(args.mzml_file)

    if query_spec and reference_spec:
        print("--- Generating Plot ---")
        plot_mirror(query_spec, reference_spec, args.output)
    else:
        print("Error: Could not load one or both of the specified spectra.")
