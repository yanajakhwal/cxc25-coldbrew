import pandas as pd

# 🔹 Load datasets
investors_df = pd.read_csv("data/EDA/investors_EDA.csv")  # Investors data
deals_df = pd.read_csv("data/deals_updated.csv")  # Deals data

# 🔹 Standardize `investorName` for accurate merging
investors_df["investorName"] = investors_df["investorName"].str.strip().str.lower()
deals_df["investors"] = deals_df["investors"].str.strip().str.lower()
deals_df["leadInvestors"] = deals_df["leadInvestors"].str.strip().str.lower()

# 🔹 Explode `investors` and `leadInvestors` into separate rows
deals_df["investors"] = deals_df["investors"].str.split(", ")
deals_df["leadInvestors"] = deals_df["leadInvestors"].str.split(", ")

investors_expanded = deals_df.explode("investors")[["investors", "roundType", "primaryTag"]]
lead_investors_expanded = deals_df.explode("leadInvestors")[["leadInvestors", "roundType", "primaryTag"]]

# 🔹 Rename columns to match `investorName`
investors_expanded.rename(columns={"investors": "investorName"}, inplace=True)
lead_investors_expanded.rename(columns={"leadInvestors": "investorName"}, inplace=True)

# 🔹 Combine both investor lists into one DataFrame
all_investors = pd.concat([investors_expanded, lead_investors_expanded])

# 🔹 Group by `investorName` and collect all occurrences of `roundType` and `primaryTag`
stages_data = all_investors.groupby("investorName")["roundType"].apply(lambda x: ", ".join(set(x))).reset_index()
sectors_data = all_investors.groupby("investorName")["primaryTag"].apply(lambda x: ", ".join(set(x))).reset_index()

# 🔹 Merge `stages` and `sectors` into `investors.csv`
investors_df = investors_df.merge(stages_data, on="investorName", how="left", suffixes=("", "_from_deals"))
investors_df = investors_df.merge(sectors_data, on="investorName", how="left", suffixes=("", "_from_deals"))

# 🔹 Append new `stages` and `sectors` from `deals.csv` to existing values in `investors.csv`
investors_df["stages"] = investors_df.apply(
    lambda row: f"{row['stages']}, {row['roundType']}" if pd.notnull(row["roundType"]) and pd.notnull(row["stages"])
    else row["roundType"] if pd.notnull(row["roundType"])
    else row["stages"], axis=1
)

investors_df["sectors"] = investors_df.apply(
    lambda row: f"{row['sectors']}, {row['primaryTag']}" if pd.notnull(row["primaryTag"]) and pd.notnull(row["sectors"])
    else row["primaryTag"] if pd.notnull(row["primaryTag"])
    else row["sectors"], axis=1
)

# 🔹 Remove duplicate values within each row (optional)
investors_df["stages"] = investors_df["stages"].apply(lambda x: ", ".join(set(x.split(", "))) if pd.notnull(x) else x)
investors_df["sectors"] = investors_df["sectors"].apply(lambda x: ", ".join(set(x.split(", "))) if pd.notnull(x) else x)

# 🔹 Drop extra columns
investors_df.drop(columns=["roundType", "primaryTag"], inplace=True, errors="ignore")

# 🔹 Save updated dataset
investors_df.to_csv("data/investors_final.csv", index=False)

# 🔹 Check missing values after update
print(investors_df.isnull().sum())
print("✅ `stages` and `sectors` updated using `deals_updated.csv`, considering `investors` and `leadInvestors`, and saved as `investors_updated.csv`!")