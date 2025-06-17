import sqlite3
import pymzml.run
import argparse
import sys
import json

def find_and_load_spectrum(file_path, target_mz, tolerance=0.02):
    """Finds a specific spectrum in an mzML file and returns its data."""
    try:
        run = pymzml.run.Reader(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    for spec in run:
        if spec.ms_level == 2 and spec.selected_precursors:
            try:
                precursor_mz = spec.selected_precursors[0].get('mz')
                if abs(precursor_mz - target_mz) <= tolerance:
                    print(f"Found matching spectrum: ID {spec.ID} with m/z {precursor_mz:.4f}")
                    mz_array = [float(mz) for mz in spec.mz]
                    intensity_array = [float(i) for i in spec.i]
                    return {
                        'precursor_mz': float(precursor_mz),
                        'mz_values': json.dumps(mz_array),
                        'intensity_values': json.dumps(intensity_array)
                    }
            except (IndexError, TypeError, KeyError, ValueError):
                continue
    print(f"Error: Could not find a spectrum matching m/z {target_mz:.4f}")
    return None

def update_compound_in_db(compound_name, spectral_data):
    """Updates a compound record in the database with spectral data."""
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM compounds WHERE name = ?", (compound_name,))
        if not cursor.fetchone():
            print(f"Error: Compound '{compound_name}' not found in the database.")
            return

        print(f"Updating '{compound_name}' in the database...")
        cursor.execute("""
            UPDATE compounds 
            SET precursor_mz = ?, mz_values = ?, intensity_values = ?
            WHERE name = ?
        """, (spectral_data['precursor_mz'], spectral_data['mz_values'], spectral_data['intensity_values'], compound_name))
        conn.commit()
        print("Database update successful.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PhytoDiscover Library Builder - Add reference spectra to the knowledge base.')
    parser.add_argument('-c', '--compound_name', required=True, help='The name of the compound to update in the database.')
    parser.add_argument('-f', '--mzml_file', required=True, help='Path to the source .mzML file containing the spectrum.')
    parser.add_argument('-m', '--target_mz', type=float, required=True, help='The target precursor m/z of the spectrum to add.')
    
    args = parser.parse_args()

    print('--- Starting Library Builder ---')
    spectrum_data = find_and_load_spectrum(args.mzml_file, args.target_mz)
    if spectrum_data:
        update_compound_in_db(args.compound_name, spectrum_data)
    print('--- Library Builder Finished ---')
