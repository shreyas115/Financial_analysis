import pandas as pd
import sys
import os

PROJECT_ROOT = os.path.abspath("")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.company_registry import CANONICAL_COMPANIES

FINAL_LINE_ITEMS = pd.read_csv(
    "data/processed/selected_line_items.csv"
)['0'].tolist()

def resolve_entity(entity_name):
    name = str(entity_name).upper().strip()
    for entry in CANONICAL_COMPANIES.values():
        if name in entry["aliases"]:
            return entry["canonical"]
    return None

chunks = pd.read_csv(
    "data/raw/companyfacts.csv",
    chunksize=500_000
)

output_path = "data/processed/financial_facts_clean.csv"
first_write = True

for i, chunk in enumerate(chunks):
    chunk = chunk.drop(columns=["Unnamed: 0"], errors="ignore")

    chunk["company"] = chunk["entityName"].apply(resolve_entity)

    mask = (
        (chunk["form"] == "10-K") &
        (chunk["companyFact"].isin(FINAL_LINE_ITEMS)) &
        (chunk["company"].notna())
    )

    filtered = chunk.loc[mask]

    if not filtered.empty:
        filtered.to_csv(
            output_path,
            mode="w" if first_write else "a",
            header=first_write,
            index=False
        )
        first_write = False

    if i % 10 == 0:
        print(f"Processed chunk {i}")

# Cleanup
df = pd.read_csv(output_path)
df["fy"] = df["fy"].astype(int)
df["val"] = pd.to_numeric(df["val"], errors="coerce")
df["units"] = df["units"].fillna("UNKNOWN")
df = df.dropna(subset=["val"])

df.to_csv(output_path, index=False)