import pandas as pd
import numpy as np

deals_df = pd.read_csv("raw_data/deals.csv")
deals_df["amount"] = pd.to_numeric(deals_df["amount"], errors="coerce")

def infer_round_type(row):
    if row["roundType"] != "Series ?":  
        return row["roundType"]  # Keep existing value
    
    if pd.notnull(row["amount"]):
        if row["amount"] < 500000:
            return "Pre-Seed"
        elif row["amount"] < 2000000:
            return "Seed"
        elif row["amount"] < 15000000:
            return "Series A"
        elif row["amount"] < 50000000:
            return "Series B"
        elif row["amount"] < 100000000:
            return "Series C"
        else:
            return "Series D+"

    return "Unknown"  

deals_df["roundType"] = deals_df.apply(infer_round_type, axis=1)

deals_df.to_csv("data/deals_updated.csv", index=False)

###################


import pandas as pd

companies_df = pd.read_csv("data/companies_updated.csv")  # Companies data
deals_df = pd.read_csv("data/deals_updated.csv")  # Deals data

companies_df["companyName"] = companies_df["companyName"].str.strip().str.lower()
deals_df["companyName"] = deals_df["companyName"].str.strip().str.lower()

deals_df["date"] = pd.to_datetime(deals_df["date"], errors="coerce")

deals_df = deals_df.sort_values(by=["companyName", "date"], ascending=[True, False])

latest_deals = deals_df.drop_duplicates(subset=["companyName"], keep="first")[["companyName", "roundType", "date"]]

latest_deals.rename(columns={"date": "latestRoundDate_from_deals"}, inplace=True)

companies_df = companies_df.merge(latest_deals, on="companyName", how="left")

companies_df["latestRoundType"] = companies_df["latestRoundType"].fillna(companies_df["roundType"])
companies_df["latestRoundDate"] = companies_df["latestRoundDate"].fillna(companies_df["latestRoundDate_from_deals"])

companies_df.drop(columns=["roundType", "latestRoundDate_from_deals"], inplace=True, errors="ignore")
companies_df.to_csv("data/companies_updated.csv", index=False)

print(companies_df.isnull().sum())


########################

import pandas as pd
from datetime import timedelta

companies_df = pd.read_csv("data/companies_updated.csv")
deals_df = pd.read_csv("data/deals_updated.csv") 


companies_df["companyName"] = companies_df["companyName"].str.strip().str.lower()
deals_df["companyName"] = deals_df["companyName"].str.strip().str.lower()

deals_df["date"] = pd.to_datetime(deals_df["date"], errors="coerce")

deals_df = deals_df.sort_values(by=["companyName", "date"], ascending=[True, True])

first_funding = deals_df.drop_duplicates(subset=["companyName"], keep="first")[["companyName", "date", "roundType"]]

def estimate_founded_date(row):
    if pd.isnull(row["date"]):  # If no funding date available, return NaN
        return pd.NaT

    if row["roundType"] in ["Pre-Seed", "Seed", "Series A", "Series B"]:
        return row["date"] - pd.DateOffset(years=1)  # 1 year before first funding
    else:
        return row["date"] - pd.DateOffset(years=2)  # 2 years before first funding

first_funding["estimatedFounded"] = first_funding.apply(estimate_founded_date, axis=1)

companies_df = companies_df.merge(first_funding[["companyName", "estimatedFounded"]], on="companyName", how="left")
companies_df["dateFounded"] = companies_df["dateFounded"].fillna(companies_df["estimatedFounded"])
companies_df.drop(columns=["estimatedFounded"], inplace=True, errors="ignore")
companies_df.to_csv("data/companies_updated.csv", index=False)

print(companies_df.isnull().sum())
print("✅ `dateFounded` imputed using first funding date from `deals_updated.csv` and saved as `companies_final.csv`!")