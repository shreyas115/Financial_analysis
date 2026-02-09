# 📊 Financial RAG System for SEC Filings

## 📌 Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)–style financial question answering system** over **SEC 10-K filings**, designed to produce **accurate, deterministic, and citation-backed financial facts**.

Unlike typical LLM-driven RAG systems, this project **prioritizes correctness and traceability**:
- No hallucinated numbers
- No paraphrasing or interpretation
- Every answer is backed by a source filing

The system supports **single-year queries**, **multi-year trends**, and **year-over-year (YoY) growth analysis** for selected companies.

---

## 🎯 Objectives

- Build a **reliable financial QA system** using structured SEC data
- Enable **company-scoped retrieval** to prevent cross-company leakage
- Support **trend analysis and growth computation**
- Provide **explicit citations** (company, filing type, filing date)
- Design a system that **scales to large datasets** without requiring an LLM

---

## 🧱 System Architecture

### 📌 High-Level Flow
---

### 🔧 Component Overview

#### **User (CLI)**
- Initiates financial queries via the command line.

#### **ask.py (CLI Entry Point)**
- Parses user input.
- Dispatches queries to the core QA engine.

#### **FinancialQAEngine**
- Central orchestration layer.
- Responsibilities:
  - **Metric Resolution**: Identifies financial metrics such as assets, revenue, and net income.
  - **Query Type Detection**: Determines the intent and structure of the user query.

#### **FinancialRetriever**
- Handles data retrieval and filtering.
- Key functions:
  - **Company Resolution**: Maps company mentions to a canonical company registry.
  - **Company-Scoped Filtering**: Restricts search space to relevant companies.
  - **Line Item Matching**: Matches resolved metrics to financial statement line items.
  - **Semantic Search (Optional)**: Uses FAISS for embedding-based retrieval when exact matches are insufficient.

---


### Key Design Choices
- **Company filtering happens before retrieval**
- **Exact line-item matching is preferred over semantic similarity**
- **FAISS is used only when appropriate**
- **LLMs are intentionally excluded** to ensure determinism

---

## 📁 Project Structure

## 🧩 Directory Breakdown

### **data/**
Stores raw and processed financial datasets.

- **raw/**
  - `companyfacts.csv`: Raw SEC company facts data.
- **processed/**
  - `financial_facts_clean.csv`: Cleaned and normalized financial facts.
  - `selected_line_items.csv`: Curated financial line items used for querying.

---

### **rag/**
Core retrieval and reasoning components (RAG-style architecture).

- `retriever.py`:  
  Implements company-scoped document retrieval and optional semantic search.
- `engine.py`:  
  Handles query interpretation, metric resolution, and financial computations.
- `company_registry.py`:  
  Maintains canonical mappings for company names, tickers, and identifiers.

---

### **cli/**
User-facing command-line interface.

- `ask.py`:  
  Entry point for submitting financial questions via CLI.

---

### **src/**
Data ingestion and preprocessing utilities.

- `ingest_financials.py`:  
  Pipeline for ingesting SEC financial data, cleaning, and storing it in processed form.

---

## 🚀 How Everything Fits Together

1. **Data Ingestion**  
   SEC financial data is ingested and normalized using `ingest_financials.py`.

2. **Query Execution**  
   Users submit queries via `ask.py`.

3. **Retrieval & Reasoning**  
   The RAG engine resolves companies, identifies metrics, retrieves relevant financial facts, and computes results.

4. **Answer Generation**  
   The system returns precise, company-specific financial answers.

---

## ▶️ How to Run

### 1️⃣ Install Dependencies
```bash
pip install pandas langchain langchain-community faiss-cpu
```
### 2️⃣ Ingest SEC Data
```bash
python src/ingest_financials.py
```

This generates:
```
data/processed/financial_facts_clean.csv
```

### 3️⃣ Ask Questions (CLI)
Single-Year Query
```bash
python cli/ask.py --company "Apple" --question "Assets" --year 2015
```
Multi-Year Trend
```bash
python cli/ask.py --company "Netflix" --question "Revenue" --start_year 2019 --end_year 2022
```
Year-over-Year Growth
```bash
python cli/ask.py --company "Amazon" --question "revenue growth" --year 2021
```

JSON Output
```bash
python cli/ask.py --company "Google" --question "Revenue" --year 2022 --json
```

## 📤 Output Format
### 📌 Single-Year Result

    806000000000 USD
    (THE GOLDMAN SACHS GROUP, INC., 10-K, filed 2012-02-28)
### 📈 Trend Output
    {
      "year": 2020,
      "value": 386064000000,
      "units": "USD",
      "citation": {
        "source": "APPLE INC.",
        "form": "10-K",
        "filing_date": "2020-10-30"
      }
    }

### 📊 YoY Growth Output
    {
      "year": 2021,
      "yoy_growth_pct": 7.42,
      "citation": {
        "source": "AMAZON.COM, INC.",
        "form": "10-K",
        "filing_date": "2022-02-03"
      }
    }

## 🚀 Future Enhancements

- Support entire SEC dataset (13GB+) via:

    - DuckDB / Parquet
    
    - Vector sharding

- Metric synonym expansion

- Time-series visualizations

- Web UI / API layer


## 🧪 Example Use Cases

- “What were Apple’s total assets in 2015?”

- “How did Netflix’s revenue change from 2019–2022?”

- “What was Amazon’s revenue growth in 2021?”

- “Compare assets across years for Goldman Sachs”

