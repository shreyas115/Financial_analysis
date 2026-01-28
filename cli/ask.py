#!/usr/bin/env python
# coding: utf-8

import argparse
import sys
import os
import json

import warnings
warnings.filterwarnings("ignore")


PROJECT_ROOT = os.path.abspath("")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.retriever import FinancialRetriever, load_vectorstore, companies_list
from rag.engine import FinancialQAEngine
from data.company_registry import CANONICAL_COMPANIES

def print_fact(fact):
    value = fact.get("value", fact.get("yoy_growth_pct", "N/A"))
    units = fact.get("units", "")
    citation = fact.get("citation", {})
    print(f"{value} {units} "
          f"({citation.get('source','N/A')}, {citation.get('form','N/A')}, filed {citation.get('filing_date','N/A')})")

def normalize_company_input(user_input: str):
    user_input = user_input.upper()
    for entry in CANONICAL_COMPANIES.values():
        if entry["canonical"] in user_input:
            return entry["canonical"]
    return user_input

def main():
    parser = argparse.ArgumentParser(description="Financial RAG CLI")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--question", required=True, help="Financial question, e.g., 'total assets'")
    parser.add_argument("--year", type=int, help="Single fiscal year")
    parser.add_argument("--start_year", type=int, help="Start fiscal year for trend")
    parser.add_argument("--end_year", type=int, help="End fiscal year for trend")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")


    args = parser.parse_args()
    company = normalize_company_input(args.company)

    # Load vector store
    vectorstore = load_vectorstore()
    companies = companies_list()
    retriever = FinancialRetriever(vectorstore, companies)
    engine = FinancialQAEngine(retriever)

    # Determine query type
    if args.start_year and args.end_year:
        # Multi-year trend query
        answer = engine.answer_trend_question(
            query=args.question,
            company=company,
            start_year=args.start_year,
            end_year=args.end_year
        )
    elif args.year:
        query = args.question.lower()
        if "growth" in query or "yoy" in query:
            answer = engine.answer_yoy_growth(
                query=args.question,
                company=company,
                year=args.year
            )
        else:
            answer = engine.answer_single_year(
                query=args.question,
                company=company,
                fiscal_year=args.year
            )
    else:
        raise ValueError("You must specify either --year or both --start_year and --end_year")
    
    print("\nANSWER:\n")

    if isinstance(answer, list):
        for fact in answer:
            if args.json:
                print(json.dumps(fact, indent=2))
            else:
                print_fact(fact)
    else:
        if args.json:
            print(json.dumps(answer, indent=2))
        else:
            print(answer)


if __name__ == "__main__":
    main()
