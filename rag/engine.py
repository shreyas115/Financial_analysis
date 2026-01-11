#!/usr/bin/env python
# coding: utf-8

# In[13]:

import warnings
warnings.filterwarnings("ignore")

CANONICAL_METRICS = {
    "assets": ["Assets"],
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "net_income": ["NetIncomeLoss"]
}

def resolve_metric(query: str):
    query = query.lower()
    for _, aliases in CANONICAL_METRICS.items():
        for alias in aliases:
            if alias.lower() in query:
                return alias
    return None


# In[14]:


def sort_by_year(docs):
    return sorted(docs, key=lambda d: d.metadata["fiscal_year"])


def compute_yoy_growth(docs):
    docs = sorted(docs, key=lambda d: d.metadata["fiscal_year"])
    results = []

    for i in range(1, len(docs)):
        prev = docs[i - 1]
        curr = docs[i]

        prev_val = prev.metadata["value"]
        curr_val = curr.metadata["value"]

        yoy = ((curr_val - prev_val) / prev_val) * 100

        results.append({
            "year": curr.metadata["fiscal_year"],
            "yoy_growth_pct": round(yoy, 2)
        })

    return results



# In[15]:


class FinancialQAEngine:
    def __init__(self, retriever):
        self.retriever = retriever

    def answer_trend_question(self, query, company, start_year, end_year):
        metric = resolve_metric(query)
        if not metric:
            return "Unable to resolve financial metric from the question."

        docs = self.retriever.retrieve(
            query=query,
            company=company,
            k=20
        )

        docs = [
            d for d in docs
            if d.metadata["line_item"] == metric
            and start_year <= d.metadata["fiscal_year"] <= end_year
        ]

        if not docs:
            return f"No {metric} data found for {company} between {start_year} and {end_year}."

        docs = sorted(docs, key=lambda d:d.metadata["fiscal_year"])

        trend = [
            {   
                "year": d.metadata["fiscal_year"],
                "value": d.metadata["value"]
            }
            for d in docs
        ]
        return trend
    
    def answer_single_year(self, query, company, fiscal_year):
        metric = resolve_metric(query)

        docs = self.retriever.retrieve(
            query=query,
            company=company,
            fiscal_year=fiscal_year,
            k=10
        )
        docs = [
            d for d in docs
            if d.metadata["line_item"] == metric
        ]
        
        if not docs:
            return f"No {metric} data found for {company} in {fiscal_year}."

        return [
            d.page_content
            for d in docs
        ]

if __name__ == "__main__":
    print("Running engine sanity check...")
    # e = FinancialQAEngine(...)
    print("Engine module loads successfully")
