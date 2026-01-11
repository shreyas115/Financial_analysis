#!/usr/bin/env python
# coding: utf-8

# In[13]:


import argparse
import sys
import os

import warnings
warnings.filterwarnings("ignore")


PROJECT_ROOT = os.path.abspath("")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.retriever import FinancialRetriever, load_vectorstore
from rag.engine import FinancialQAEngine

def main():
    parser = argparse.ArgumentParser(description="Financial RAG CLI")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--question", required=True, help="Financial question, e.g., 'total assets'")
    parser.add_argument("--year", type=int, help="Single fiscal year")
    parser.add_argument("--start_year", type=int, help="Start fiscal year for trend")
    parser.add_argument("--end_year", type=int, help="End fiscal year for trend")

    args = parser.parse_args()

    # Load vector store
    vectorstore = load_vectorstore()
    retriever = FinancialRetriever(vectorstore)
    engine = FinancialQAEngine(retriever)

    # Determine query type
    if args.start_year and args.end_year:
        # Multi-year trend query
        answer = engine.answer_trend_question(
            query=args.question,
            company=args.company,
            start_year=args.start_year,
            end_year=args.end_year
        )
    elif args.year:
        # Single-year query
        answer = engine.answer_single_year(
            query=args.question,
            company=args.company,
            fiscal_year=args.year
        )
    else:
        raise ValueError("You must specify either --year or both --start_year and --end_year")

    for a in answer:
        print(a) 

if __name__ == "__main__":
    main()
