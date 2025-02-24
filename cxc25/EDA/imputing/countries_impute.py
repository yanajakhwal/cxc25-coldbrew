import pandas as pd

dealInvestor_df = pd.read_csv("data/dealInvestor_updated.csv")
investors_df = pd.read_csv("data/investors_updated.csv")

dealInvestor_df["investorName"] = dealInvestor_df["investorName"].str.strip().str.lower()
investors_df["investorName"] = investors_df["investorName"].str.strip().str.lower()

investor_country_map = investors_df.set_index("investorName")["country"].to_dict()

unmatched_investors = dealInvestor_df[
    (dealInvestor_df["investorCountry"].isnull()) & 
    (~dealInvestor_df["investorName"].isin(investor_country_map))
]["investorName"].unique()

dealInvestor_df["investorCountry"] = dealInvestor_df["investorCountry"].fillna(
    dealInvestor_df["investorName"].map(investor_country_map)
)

dealInvestor_df.to_csv("data/dealInvestor_final.csv", index=False)

print(f"❌ Remaining missing `investorCountry`: {dealInvestor_df['investorCountry'].isnull().sum()}")
print("✅ `investorCountry` updated using `investors_updated.csv` and saved as `dealInvestor_final.csv`!")