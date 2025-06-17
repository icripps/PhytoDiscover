# PhytoDiscover: A Framework for Natural Product Discovery

PhytoDiscover is a lightweight, command-line bioinformatics framework designed to accelerate the discovery of known and novel bioactive compounds from mass spectrometry data. It allows researchers to screen complex chemical mixtures (like plant extracts) against a curated spectral library to identify molecules of interest.

## Features

- **Spectral Library Management:** Build and manage a custom SQLite-based reference library of tandem mass spectra.
- **Compound Identification:** Identify unknown spectra by comparing them against the reference library using the `ModifiedCosine` similarity score.
- **Flexible & Fast:** Built with efficient, pure-Python libraries (`pymzml` and `matchms`) for compatibility and speed.
- **Command-Line Interface:** All tools are designed to be run from the command line for easy integration into automated workflows.
- **Structured Reporting:** Generates clear, analysis-ready CSV reports of all findings.

---

## Installation

To get started with PhytoDiscover, you'll need Python 3. It is highly recommended to use a virtual environment.

1.  **Clone the repository** (or download and extract the source code).

2.  **Navigate to the project directory:**
    ```bash
    cd PhytoDiscover
    ```

3.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

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

