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


### THIS IS FOR SCRAPING dateFounded IN companies.csv

import re
import google.generativeai as genai
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np

df = pd.read_csv("data/companies_cleaned.csv")
missing_companies = df[df["dateFounded"].isna()][["companyName", "ecosystemName"]].dropna().values.tolist()

genai.configure(api_key="AIzaSyCgqbcwAg0-gzrYWS3u5r4vRvOOqfntyoA")  # Replace with your actual API key

def get_google_search_results(company_name, location):
    """Search Google for the company's full founding date using name and location."""
    query = f"{company_name} {location} founded date"
    search_results = list(search(query, num_results=15))  # Get top 5 Google results

    valid_results = [
        url for url in search_results
        if url.startswith("http")
        and "imgres?" not in url
        and "youtube.com" not in url
        and "google.com" not in url
        and "crunchbase.com" not in url
        and "pitchbook.com" not in url
        and "zoominfo" not in url
        and "app.dealroom.co" not in url
        and "businesswire"  not in url
        and "dnb" not in url
        and "cmaj" not in url
        and "accessnewswire" not in url
        and "canadagoose" not in url
        and "owler" not in url
        and "linkedin" not in url
    ]
    return valid_results

def scrape_webpage(url):
    """Fetch and extract text content from a webpage."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Increased timeout
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()

    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

def format_founded_date(date_str):
    """Format year-only results as 'YYYY-01-01'."""
    if re.fullmatch(r"\d{4}", date_str):  # If only a year is found
        return f"{date_str}-01-01"
    return date_str  # Return full YYYY-MM-DD if already formatted

def get_founded_date(company_name, location):
    """Find the full founded date using Google search + web scraping + Gemini AI."""
    search_results = get_google_search_results(company_name, location)

    scraped_texts = []
    for url in search_results:
        scraped_text = scrape_webpage(url)
        if scraped_text:
            scraped_texts.append(scraped_text[:2000])  # Limit text size for API
            if len(scraped_texts) >= 10:  # Stop after getting 2 valid results
                break

    if not scraped_texts:
        return "Not Found"

    try:
        # 🔹 Use Gemini API
        model = genai.GenerativeModel("gemini-pro")

        # 🔹 Updated prompt to request a full date
        prompt = (
            f"Extract the **exact** founding date for {company_name} in {location} from these web pages.\n\n"
            f"**Only return the date in YYYY-MM-DD format.** If only the year is found, return 'YYYY'."
            f"\n\nSources:\n" + "\n\n".join(scraped_texts)
        )

        response = model.generate_content(prompt)
        founded_date = response.text.strip() if response else "Not Found"

        # 🔹 Format year-only values as 'YYYY-01-01'
        return format_founded_date(founded_date)

    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "Error: AI Failure"

# 🔹 Loop through the missing companies list
for company, location in missing_companies:
    print(f"🔍 Searching for: {company} ({location})")
    founded_date = get_founded_date(company, location)

    # 🔹 Update the original DataFrame
    df.loc[(df["companyName"] == company) & (df["ecosystemName"] == location), "dateFounded"] = founded_date

    # 🔹 Sleep to prevent API rate limits
    time.sleep(2)


# ensuring that all of the imputed data is dates
date_cols = ["dateFounded", "latestRoundDate", "dateAcqusition", "ipoDate", "peDate"]

valid_date_pattern = r"^\d{4}-\d{2}-\d{2}$"
for col in date_cols:
    df[col] = df[col].astype(str)
    df[col] = df[col].where(df[col].str.match(valid_date_pattern), np.nan)

print(df[date_cols].isnull().sum())

#######################################

import pandas as pd
from datetime import timedelta

companies_df = pd.read_csv("data/companies_updated.csv")  # Companies data
deals_df = pd.read_csv("data/deals_updated.csv")  # Deals with funding dates

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
companies_df.to_csv("data/companies_final.csv", index=False)

print(companies_df.isnull().sum())
print("✅ `dateFounded` imputed using first funding date from `deals_updated.csv` and saved as `companies_final.csv`!")


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