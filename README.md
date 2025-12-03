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
 │    ├─ app.py
 │    ├─ build_index.py  
 │    ├─ chat_cli.py
 │    ├─ embeddings.py     
 │    ├─ extract_sections.py
 │    ├─ llm_groq.py
 │    ├─ parse_pdf.py
 │    ├─ rag_pipeline.py
 ├─ requirements.txt
 └─ README.md
 └── .gitignore
```

## How to Run (Local Demo)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Ensure Groq key is visible
```bash
source ~/.zshrc
echo $GROQ_API_KEY
```

### 3. Build the pipeline
```bash
cd src
python parse_pdf.py
python extract_sections.py
python build_index.py
```

### 4. Test CLI (Optional)
```bash
python chat_cli.py
```

### 5. Run Streamlit
```bash
python streamlit run app.py
```
