import pandas as pd
import re
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document

import warnings
warnings.filterwarnings("ignore")


DATA_PATH = "data/processed/financial_facts_clean.csv"

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def resolve_company(user_company: str, companies: list[str]) -> str | None:
    user_norm = normalize(user_company)

    matches = [
        c for c in companies
        if user_norm in normalize(c)
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        return sorted(matches, key=len)[0]

    return None

def financial_row_to_doc(row):
    content = (
        f"In fiscal year {row['fy']}, {row['entityName']} reported "
        f"{row['companyFact']} of {row['val']} {row['units']}, "
        f"as disclosed in its {row['form']} filing."
    )

    metadata = {
        "cik": row["cik"],
        "company": row["entityName"],
        "line_item": row["companyFact"],
        "fiscal_year": int(row["fy"]),
        "value": float(row["val"]),
        "units": row["units"],
        "form": row["form"],
        "filing_date": row["filed"],
        "source": "SEC Filing"
    }
    return Document(page_content=content, metadata=metadata)


def load_vectorstore():
    """Loads data, builds embeddings, and returns a FAISS vectorstore."""
    df = pd.read_csv(DATA_PATH)

    documents = [
        financial_row_to_doc(row)
        for _, row in df.iterrows()
    ]

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    return FAISS.from_documents(documents, embeddings)

def companies_list():
    df = pd.read_csv(DATA_PATH)
    all_companies = sorted(set(df["entityName"].str.upper()))
    return all_companies

class FinancialRetriever:
    def __init__(self, vectorstore, all_companies: list[str]):
        self.vectorstore = vectorstore
        self.all_companies = all_companies

    def retrieve(
        self,
        query: str,
        company: str | None = None,
        fiscal_year: int | None = None,
        k: int = 5,
    ):
        # Resolve company FIRST
        resolved_company = resolve_company(company, self.all_companies)

        if not resolved_company:
            return []
        # Filter documents by company
        company_docs = [
            d for d in self.vectorstore.docstore._dict.values()
            if str.lower(d.metadata.get("company")) == str.lower(resolved_company)
        ]
        if not company_docs:
            return []
        
        query_lower = query.lower()
        matched_docs = [
            d for d in company_docs
            if query_lower in str(d.metadata.get("line_item")).lower()
        ]
        # 5Optional year filter
        if fiscal_year:
            matched_docs = [
                d for d in matched_docs
                if d.metadata.get("fiscal_year") == fiscal_year
            ]
        
        if not matched_docs:
        # create temporary FAISS index for company docs
            sub_vectorstore = FAISS.from_documents(company_docs, self.vectorstore.embedding_function)
            matched_docs = sub_vectorstore.similarity_search(query, k=k)
        
        return matched_docs


if __name__ == "__main__":
    print("Retriever module sanity check OK")
