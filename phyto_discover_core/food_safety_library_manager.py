import sqlite3
import torch
import torch.nn as nn
from matchms.importing import load_from_mgf
import numpy as np
import pickle

# --- 1. Define the Neural Network for Embeddings ---
class SpectrumEncoder(nn.Module):
    def __init__(self, input_size=1024, embedding_dim=128):
        super(SpectrumEncoder, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(512, 256)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(256, embedding_dim)

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

# --- 2. Function to Preprocess and Generate Embeddings ---
def get_embedding(spectrum, model, max_mz=1024):
    if spectrum is None or spectrum.peaks.mz is None or len(spectrum.peaks.mz) == 0:
        return None

    binned_spectrum = np.zeros(max_mz)
    for mz, intensity in zip(spectrum.peaks.mz, spectrum.peaks.intensities):
        if 0 <= mz < max_mz:
            binned_spectrum[int(mz)] += intensity

    if np.sum(binned_spectrum) > 0:
        binned_spectrum = binned_spectrum / np.max(binned_spectrum)

    spectrum_tensor = torch.FloatTensor(binned_spectrum).unsqueeze(0)
    with torch.no_grad():
        embedding = model(spectrum_tensor)
    return embedding.squeeze().numpy()

# --- 3. Main Function to Build the Library ---
def build_food_safety_library(mgf_file, db_file):
    print(f'Building food safety library from {mgf_file} into {db_file}...')

    torch.manual_seed(42)
    model = SpectrumEncoder()
    model.eval()

    spectrums = list(load_from_mgf(mgf_file))
    print(f'Loaded {len(spectrums)} spectra from MGF file.')

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reference_spectra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spectrum_id TEXT,
            compound_name TEXT,
            precursor_mz REAL,
            serialized_spectrum BLOB,
            embedding BLOB
        )
    ''')
    print("Database table 'reference_spectra' created or already exists.")

    for i, spectrum in enumerate(spectrums):
        if spectrum is None:
            continue

        spectrum_id = spectrum.get('spectrumid', f'spectrum_{i}')
        compound_name = spectrum.get('name', 'Unknown') # .mgf files often use 'name' instead of 'compound_name'
        precursor_mz = spectrum.get('pepmass')[0] if spectrum.get('pepmass') else 0.0

        embedding = get_embedding(spectrum, model)
        if embedding is None:
            print(f'Skipping spectrum {spectrum_id} due to missing data.')
            continue

        serialized_spectrum = pickle.dumps(spectrum)
        serialized_embedding = pickle.dumps(embedding)

        cursor.execute('''
            INSERT INTO reference_spectra (spectrum_id, compound_name, precursor_mz, serialized_spectrum, embedding)
            VALUES (?, ?, ?, ?, ?)
        ''', (spectrum_id, compound_name, precursor_mz, serialized_spectrum, serialized_embedding))

        if (i + 1) % 20 == 0:
            print(f'Processed {i + 1}/{len(spectrums)} spectra...')

    conn.commit()
    conn.close()
    print(f'Successfully built food safety library with {len(spectrums)} entries.')

# --- 4. Execute the Build Process ---
if __name__ == '__main__':
    MGF_FILE_PATH = 'data/pesticides.mgf'
    DB_FILE_PATH = 'data/food_safety.db'
    build_food_safety_library(MGF_FILE_PATH, DB_FILE_PATH)
