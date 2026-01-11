#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

import warnings
warnings.filterwarnings("ignore")

financial_facts = pd.read_csv(
    "../data/processed/financial_facts_clean.csv"
)


# In[2]:


financial_facts.shape
financial_facts.head()


# In[3]:


def financial_row_to_chunk(row):
    value = float(row["val"])
    value_m = round(value / 1_000_000, 2)

    text = (
        f"In fiscal year {int(row['fy'])}, {row['entityName'].title()} reported "
        f"{row['companyFact'].replace('Assets', 'total assets')} of approximately "
        f"{value_m} million USD, as disclosed in its Form {row['form']} filing "
        f"with the U.S. SEC."
    )

    metadata = {
        "cik": int(row["cik"]),
        "company": row["entityName"].title(),
        "line_item": row["companyFact"],
        "value": value,
        "value_millions": value_m,
        "unit": row["units"],
        "fiscal_year": int(row["fy"]),
        "fiscal_period": row["fp"],
        "form": row["form"],
        "filing_date": row["filed"],
        "source": "SEC"
    }

    return {"text": text, "metadata": metadata}


# In[4]:


sample_row = financial_facts.iloc[0]
chunk = financial_row_to_chunk(sample_row)

print(chunk["text"])
print(chunk["metadata"])



if __name__ == "__main__":
    print("Running chunking sanity check...")
    # e = FinancialQAEngine(...)
    print("Chunking module loads successfully")


