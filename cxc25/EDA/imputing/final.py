import pandas as pd

# companies = pd.read_csv('data/companies_updated.csv')

# companies["dateAcqusition"] = companies.apply(
#     lambda row: row["latestRoundDate"] if pd.notnull(row["acquiringCompany"]) and pd.isnull(row["dateAcqusition"])
#     else row["dateAcqusition"], axis=1
# )

# companies.to_csv("data/companies_final.csv", index=False)
# print("✅ `dateAcqusition` imputed where `acquiringCompany` exists!")


# Load investors dataset
investors_df = pd.read_csv("data/investors_updated.csv")
dealInvestor_df = pd.read_csv("data/dealInvestor_updated.csv")

# Create lookup dictionary
investor_country_map = investors_df.set_index("investorName")["country"].dropna().to_dict()

# Apply to `dealInvestor.csv`
dealInvestor_df["investorCountry"] = dealInvestor_df["investorCountry"].fillna(dealInvestor_df["investorName"].map(investor_country_map))

dealInvestor_df = dealInvestor_df.iloc[:, 5:]
dealInvestor_df = dealInvestor_df.iloc[:, 5:]
# Save
dealInvestor_df.to_csv("data/dealInvestor_final.csv", index=False)
print("✅ `investorCountry` imputed where possible!")