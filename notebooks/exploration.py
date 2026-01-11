#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd


# In[7]:


companyfacts_cols = pd.read_csv(
    "../data/raw/companyfacts.csv",
    nrows=0
)

companyfacts_cols.columns


# In[10]:


sample_companyfacts = pd.read_csv(
    "../data/raw/companyfacts.csv",
    nrows=1000
)

sample_companyfacts.head()


# In[12]:


lineitems_cols = pd.read_csv(
    "../data/raw/line_item_counts.csv",
    nrows=0
)

lineitems_cols.columns


# In[17]:


line_items = pd.read_csv("../data/raw/line_item_counts.csv")
line_items.head()


# In[18]:


line_items.shape


# In[24]:


top_items = line_items.sort_values("count",ascending=False).head(30)
top_items[['line_item','count']]


# In[25]:


KEYWORDS = [
    'Income',
    'Revenue',
    'Asset',
    'Liability',
    'Equity',
    'Cash',
    'Earning',
    'Expense',
    'Profit'
]

def is_relevant(item):
    return any(k.lower() in item.lower() for k in KEYWORDS)

relevant_items = top_items[top_items['line_item'].apply(is_relevant)]
relevant_items[['line_item', 'count']]


# In[26]:


selected_line_items = relevant_items['line_item'].tolist()
pd.Series(selected_line_items).to_csv("../data/processed/selected_line_items.csv",index=False)


# In[ ]:




