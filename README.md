## CM Assistant 

This repository contains the PDF processing pipeline and Retrieval-Augmented Generation (RAG) demo for the NJDOT Construction & Materials (C&M) AI Assistant. 

The goal of phase 1 is to build an AI system that can read, index, and answer questions from the 2019 Standard Specifications for Road and Bridge Construction

## Repository Structure
```plaintext
project/
 ├─ data/
 │    └─ Standard_Specs_2019.pdf
 ├─ outputs/
 │    ├─ pages.jsonl
 │    ├─ sections.jsonl
 │    ├─ spec_metadata.jsonl
 │    └─ spec_index.faiss
 ├─ src/
 │    ├─ parse_pdf.py
 │    ├─ extract_sections.py
 │    ├─ build_index.py
 │    ├─ chat_cli.py
 ├─ requirements.txt
 └─ README.md
 └── .gitignore
```

## How to Run (Local Demo)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama
```bash
brew services start ollama
ollama pull llama3.1
```

### 3. Build the RAG pipeline
```bash
cd src
python parse_pdf.py
python extract_sections.py
python build_index.py
```

### 4. Start the chatbot
```bash
python chat_cli.py
```
