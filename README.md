# AIforHelp: Healthcare AI Assistant

## Overview
AIforHelp is an open-source AI assistant designed to help patients, doctors, and nurses with medical Q&A, symptom checking, and drug information lookup. Built with Python, Hugging Face Transformers, and Flask, it is modular and ready for future expansion.

## Features
- Medical Q&A (patients, doctors, nurses)
- Symptom checker (patients)
- Drug info lookup (doctors, nurses)
- Modular and extensible codebase

## Setup
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd aiforhelp
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Download or expand medical datasets in `data/`.

## Running the App
```bash
python app.py
```

The API will be available at `http://localhost:5000`.

## Project Structure
```
aiforhelp/
│
├── app.py                # Flask API
├── requirements.txt      # Dependencies
├── ai/
│   ├── __init__.py
│   ├── qa.py             # Medical Q&A logic
│   ├── symptom_checker.py# Symptom checker logic
│   └── drug_info.py      # Drug info logic
├── data/
│   └── medquad.json      # Medical Q&A dataset (sample)
└── README.md
```

## Extending
- Add new endpoints in `app.py` and corresponding logic in `ai/` modules.
- Integrate more datasets in `data/`.

## License
MIT 