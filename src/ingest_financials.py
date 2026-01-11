#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd


# In[ ]:


BANK_KEYWORDS = [
    "JPMORGAN",
    "BANK OF AMERICA",
    "GOLDMAN SACHS",
    "MORGAN STANLEY",
    "CITIGROUP",
    "WELLS FARGO"
]


# In[2]:


def is_bank(entity_name):
    name = str(entity_name).upper()
    return any(bank in name for bank in BANK_KEYWORDS)


# In[5]:


FINAL_LINE_ITEMS = pd.read_csv(
    "../data/processed/selected_line_items.csv"
)['0'].tolist()


# In[6]:


chunks = pd.read_csv(
    "../data/raw/companyfacts.csv",
    chunksize=500_000
)


# In[11]:


output_path = "../data/processed/financial_facts_clean.csv"
first_write = True

for i,chunk in enumerate(chunks):
    chunk = chunk.drop(columns=["Unnamed: 0"], errors="ignore")
    mask = (chunk["form"] == "10-K") & (chunk["companyFact"].isin(FINAL_LINE_ITEMS)) & (chunk["entityName"].apply(is_bank))
    filtered = chunk.loc[mask]
    if not filtered.empty:
        filtered.to_csv(output_path,
                        mode='w' if first_write else 'a',
                       header=first_write,
                       index = False)
        first_write = False
    if i % 10 == 0:
        print(f"Processed chunk {i}")


# In[13]:


financial_facts = pd.read_csv("../data/processed/financial_facts_clean.csv")
financial_facts.head()


# In[19]:


financial_facts.shape


# In[15]:


financial_facts["fy"] = financial_facts["fy"].astype(int)
financial_facts["val"] = pd.to_numeric(financial_facts["val"], errors="coerce")
financial_facts["units"] = financial_facts["units"].fillna("UNKNOWN")


# In[16]:


financial_facts = financial_facts.dropna(subset=["val"])


# In[18]:


financial_facts.to_csv("../data/processed/financial_facts_clean.csv", index=False)


# In[ ]:




