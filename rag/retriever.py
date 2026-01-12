import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document

import warnings
warnings.filterwarnings("ignore")


DATA_PATH = "data/processed/financial_facts_clean.csv"


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


class FinancialRetriever:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(
        self,
        query: str,
        company: str | None = None,
        fiscal_year: int | None = None,
        k: int = 5,
    ):
        docs = self.vectorstore.similarity_search(query, k=k)

        if company:
            docs = [d for d in docs if company in d.metadata["company"]]

        if fiscal_year:
            docs = [d for d in docs if d.metadata["fiscal_year"] == fiscal_year]

        return docs


if __name__ == "__main__":
    print("Retriever module sanity check OK")
