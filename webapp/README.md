
# PhytoDiscover Web Application

This directory contains the full-stack web application, including the FastAPI backend and the Next.js frontend.

## 1. Backend Setup (FastAPI)

The backend serves the scientific analysis engine via a REST API.

### Prerequisites
- Python 3.9+
- pip

### Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd webapp/backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Backend Server

From the `webapp/backend` directory, run the following command:

```bash
python main.py
```

The API server will start, typically on `http://127.0.0.1:8001`.

## 2. Frontend Setup (Next.js)

The frontend provides an interactive user interface for the platform.

### Prerequisites
- Node.js (v18+)
- npm or yarn

### Installation

1.  **Navigate to the frontend directory:**
    ```bash
    cd webapp/frontend
    ```

2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```

### Running the Frontend Server

From the `webapp/frontend` directory, run the following command:

```bash
npm run dev
```

The application will be accessible at `http://localhost:3000`.

## 3. How to Use the Web Application

1.  Open your browser and navigate to `http://localhost:3000`.
2.  **Select an Analysis Module**: Use the radio buttons to choose between `Clinical Diagnostics`, `Food Safety`, or `Forensic Toxicology`.
3.  **Select a Sample File**: Use the dropdown menu to select the sample data file you want to analyze.
4.  **Enter a Compound Name**: Type the name of the compound you want to search for (e.g., "Aspirin", "Caffeine").
5.  **Click Search**: The application will send the request to the backend, and a table of the top matching spectra will be displayed, ranked by similarity score.
