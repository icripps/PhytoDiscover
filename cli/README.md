## Tutorial: A Step-by-Step Workflow

This tutorial will guide you through the entire process of using PhytoDiscover, from building a library entry to identifying an unknown compound. We will use the provided `small.pwiz.1.1.mzML` as our sample data.

### Step 1: Initialize the Knowledge Base

A pre-populated `knowledge_base.db` is included. It contains a placeholder compound named `Reference_Peptide_725`. In a real-world scenario, you would add many compounds to this database.

### Step 2: Build the Reference Library

Our goal is to find the spectrum for `Reference_Peptide_725` in our sample data and add it to our library as a reference.

We know this peptide has a precursor mass-to-charge ratio (m/z) of approximately **725.36**. We use the `library_builder.py` script to find this spectrum in the `.mzML` file and save it to our database.

**Command:**
```bash
python library_builder.py --compound_name 'Reference_Peptide_725' --mzml_file 'small.pwiz.1.1.mzML' --target_mz 725.36
```

**Expected Output:**
```
--- Starting Library Builder ---
Found matching spectrum: ID 5 with m/z 725.3600
Updating 'Reference_Peptide_725' in the database...
Database update successful.
--- Library Builder Finished ---
```
Our library now contains one reference spectrum.

### Step 3: Identify an "Unknown" Compound

Now, we'll pretend that the spectrum with **ID 5** in our `.mzML` file is an unknown that we want to identify.

We use the `library_search.py` script to compare this unknown spectrum against our entire reference library and generate a report of the findings.

**Command:**
```bash
python library_search.py --mzml_file 'small.pwiz.1.1.mzML' --query_id '5' --output 'identification_report.csv'
```

**Expected Output:**
```
--- Starting Library Search ---
Successfully loaded 1 reference spectra from the database.
Successfully loaded query spectrum ID 5 from small.pwiz.1.1.mzML.

--- Searching for matches for query spectrum ID 5 (m/z: 725.3600) ---

--- Top Library Hits (Console Preview) ---
1. Compound: Reference_Peptide_725 --> Score: 1.0000

Results successfully saved to /path/to/PhytoDiscover/identification_report.csv

--- Library Search Finished ---
```

### Step 4: Analyze the Results

The script gives us a perfect match! It correctly identified our "unknown" spectrum as `Reference_Peptide_725` with a score of 1.0.

More importantly, it created a file named `identification_report.csv` with the following content:

```csv
query_id,query_mz,rank,match_compound_name,match_mz,similarity_score
5,725.3600,1,Reference_Peptide_725,725.3600,1.0000
```
This structured report is ready for further analysis.

---

## Tool Reference

### `library_builder.py`

Adds a reference spectrum to the knowledge base.

```bash
python library_builder.py -c <COMPOUND_NAME> -f <MZML_FILE> -m <TARGET_MZ>
```
- `-c`, `--compound_name`: The name of the compound in the database to update.
- `-f`, `--mzml_file`: Path to the source `.mzML` file.
- `-m`, `--target_mz`: The precursor m/z of the spectrum to add.

### `library_search.py`

Identifies an unknown spectrum by searching the library.

```bash
python library_search.py -f <MZML_FILE> -i <QUERY_ID> [-o <OUTPUT_CSV>]
```
- `-f`, `--mzml_file`: Path to the `.mzML` file containing the unknown spectrum.
- `-i`, `--query_id`: The ID of the unknown spectrum to identify.
- `-o`, `--output`: (Optional) Path for the output CSV report. Defaults to `search_results.csv`.

---

## Tips for Real-World Use

- **Expand Your Library:** The power of this tool comes from the quality of your reference library. Use `library_builder.py` to add thousands of spectra from public databases (e.g., MassBank, GNPS) or your own experimental data.
- **Automate with Scripts:** Use shell scripts (like Bash) to loop through all MS2 spectra in a file and run `library_search.py` on each one, creating a comprehensive analysis of your entire sample.
- **Interpret Scores:** A score of `> 0.9` is a very high-confidence match. A score between `0.7 - 0.85` could indicate a structurally similar but novel compound—a potential discovery!


---

### Background and Inspiration

This project was inspired by the principles outlined in the work on **DreaMS (Deep Representations Empowering the Annotation of Mass Spectra)**. The core concept is that molecules can be identified and compared based on their unique mass spectral "fingerprints."

While PhytoDiscover does not implement the same self-supervised AI model, it applies the foundational idea of spectral similarity searching to create a practical, library-based framework for identifying known compounds and discovering novel, structurally related molecules in complex natural samples.

## V2: Advanced Analysis and Visualization

The framework has been updated with a more powerful, consolidated workflow for batch analysis and result visualization.

### 1. Run a Full Analysis

The `run_full_analysis.py` script is now the primary tool for analysis. It performs the following steps in a single execution:

1.  Builds an in-memory reference library (containing a reference peptide and LSD).
2.  Processes all MS/MS spectra from a given `.mzML` file.
3.  Compares every query spectrum against every reference spectrum.
4.  Generates a `final_analysis_report.csv` file with all matches that meet a minimum similarity score.

**Usage:**

```bash
python run_full_analysis.py --mzml_file /path/to/your/data.mzML --output_csv report.csv
```

### 2. Visualize a Spectral Match

After identifying a high-scoring match in the report, you can visually confirm it using the `visualize_match.py` script. This tool generates a mirror plot comparing the query and reference spectra.

**Usage:**

```bash
python visualize_match.py --mzml_file /path/to/your/data.mzML --query_id <ID_FROM_REPORT> --reference_name <NAME_FROM_REPORT> --output plot.png
```

*   `--query_id`: The ID of the spectrum from your data file (e.g., `5`).
*   `--reference_name`: The name of the reference compound (e.g., `Reference_Peptide_725` or `LSD`).

This will save a high-quality PNG image of the mirror plot, allowing for direct visual confirmation of the match.


---

# V3: Full-Stack Web Application

The project has evolved into a full-stack web application for a more user-friendly and interactive experience.

## How to Run the Application

It is highly recommended to use a virtual environment for the Python backend.

### 1. Backend Setup (Run this first!)

```bash
# Navigate to the backend directory
cd PhytoDiscover/webapp/backend

# Create and activate a virtual environment (if you haven't already)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload --port 8001
```

The backend API will now be running at `http://localhost:8001`.

### 2. Frontend Setup

Open a **new terminal window** for this step.

```bash
# Navigate to the frontend directory
cd PhytoDiscover/webapp/frontend

# Install Node.js dependencies
npm install

# Start the frontend development server
npm run dev
```

The web application will now be accessible at `http://localhost:3000`.

## How to Use the Web App

1.  **Open your browser** and navigate to `http://localhost:3000`.
2.  **Select an Analysis Module:** Use the radio buttons to choose between "Clinical Diagnostics" or "Food Safety".
3.  **Enter a Compound Name:** Type the name of a compound you want to search for (e.g., `Aspirin` for Clinical, or `Glyphosate` for Food Safety).
4.  **Select a Sample File:** The dropdown menu will be automatically populated with available `.mzML` files from the `/data` directory.
5.  **Click Search:** The results from the analysis will appear below the form.
