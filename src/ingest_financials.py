import pandas as pd

BANK_KEYWORDS = [
    "JPMORGAN",
    "BANK OF AMERICA",
    "GOLDMAN SACHS",
    "MORGAN STANLEY",
    "CITIGROUP",
    "WELLS FARGO"
]

def is_bank(entity_name):
    name = str(entity_name).upper()
    return any(bank in name for bank in BANK_KEYWORDS)

FINAL_LINE_ITEMS = pd.read_csv(
    "../data/processed/selected_line_items.csv"
)['0'].tolist()

chunks = pd.read_csv(
    "../data/raw/companyfacts.csv",
    chunksize=500_000
)

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

financial_facts = pd.read_csv("../data/processed/financial_facts_clean.csv")
financial_facts.head()

financial_facts.shape

financial_facts["fy"] = financial_facts["fy"].astype(int)
financial_facts["val"] = pd.to_numeric(financial_facts["val"], errors="coerce")
financial_facts["units"] = financial_facts["units"].fillna("UNKNOWN")

financial_facts = financial_facts.dropna(subset=["val"])

financial_facts.to_csv("../data/processed/financial_facts_clean.csv", index=False)

