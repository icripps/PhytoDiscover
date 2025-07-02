
# PhytoDiscover: A Full-Stack Molecular Identification Platform

PhytoDiscover is a powerful, full-stack application designed for molecular identification using mass spectrometry data. It combines a sophisticated Python backend for scientific analysis with an interactive Next.js web interface, enabling researchers to rapidly identify compounds by comparing their spectral fingerprints against curated reference libraries.

## 🌟 Key Features

- **Multi-Domain Analysis**: Comes pre-loaded with modules for Clinical Diagnostics, Food Safety, and Forensic Toxicology.
- **Interactive Web UI**: A modern, user-friendly interface for selecting analysis modules, running searches, and viewing results.
- **Powerful Search Engine**: Utilizes the `matchms` library to perform robust spectral similarity searches.
- **Modular Architecture**: A clean and scalable project structure that separates core logic, web application, and command-line tools.
- **Extensible**: Easily add new analysis modules by creating new spectral libraries.

## 📂 Project Structure

The project is organized into the following directories to ensure a clean separation of concerns:

```
/PhytoDiscover
├── cli/                      # Command-Line Interface tools
│   ├── README.md             # Instructions for the CLI
│   └── ...
├── data/                     # Data files (e.g., SQLite spectral libraries)
│   └── ...
├── phyto_discover_core/      # Core shared Python logic for analysis
│   └── ...
├── reports/                  # Default output directory for generated reports
├── webapp/                   # The full-stack web application
│   ├── README.md             # Instructions for the Web App
│   ├── backend/              # FastAPI backend server
│   └── frontend/             # Next.js frontend UI
└── README.md                 # This file: High-level project overview
```

## 🚀 Getting Started

For detailed instructions on how to set up and run the different components of the application, please refer to the `README.md` files within the `webapp/` and `cli/` directories.

## Background and Inspiration

This project is inspired by the concepts presented in the DreaMS project, which demonstrated the power of learning molecular representations directly from mass spectrometry data. PhytoDiscover implements a similar core principle: every molecule has a unique spectral "fingerprint," and by comparing these fingerprints using algorithms like `ModifiedCosine`, we can rapidly identify unknown compounds in a sample.
