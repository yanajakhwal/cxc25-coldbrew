import pandas as pd
import numpy as np
import requests
import re
import time
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import timedelta
from googlesearch import search

# Configuration for Google AI API
genai.configure(api_key="YOUR_API_KEY")

### Load Datasets

def load_csv(filepath):
    return pd.read_csv(filepath)

dealInvestor_df = load_csv("data/dealInvestor_updated.csv")
investors_df = load_csv("data/investors_updated.csv")
deals_df = load_csv("data/deals_updated.csv")
companies_df = load_csv("data/companies_updated.csv")

### Standardizing Column Values

def standardize_column(df, column):
    df[column] = df[column].str.strip().str.lower()
    return df

dealInvestor_df = standardize_column(dealInvestor_df, "investorName")
investors_df = standardize_column(investors_df, "investorName")
companies_df = standardize_column(companies_df, "companyName")
deals_df = standardize_column(deals_df, "companyName")

deals_df["date"] = pd.to_datetime(deals_df["date"], errors="coerce")

def infer_round_type(amount):
    if pd.isnull(amount):
        return "Unknown"
    if amount < 500000:
        return "Pre-Seed"
    elif amount < 2000000:
        return "Seed"
    elif amount < 15000000:
        return "Series A"
    elif amount < 50000000:
        return "Series B"
    elif amount < 100000000:
        return "Series C"
    else:
        return "Series D+"

deals_df["roundType"] = deals_df.apply(lambda row: row["roundType"] if row["roundType"] != "Series ?" else infer_round_type(row["amount"]), axis=1)

deals_df.to_csv("data/deals_updated.csv", index=False)
print("✅ `roundType` inferred where missing and saved in `deals_updated.csv`.")

### Imputing Missing Investor Country

investor_country_map = investors_df.set_index("investorName")["country"].dropna().to_dict()
dealInvestor_df["investorCountry"] = dealInvestor_df["investorCountry"].fillna(dealInvestor_df["investorName"].map(investor_country_map))
dealInvestor_df.to_csv("data/dealInvestor_final.csv", index=False)
print("✅ `investorCountry` imputed where possible and saved in `dealInvestor_final.csv`.")

### Imputing Missing Founding Date Using First Funding Date

deals_df = deals_df.sort_values(by=["companyName", "date"], ascending=[True, True])
first_funding = deals_df.drop_duplicates(subset=["companyName"], keep="first")[["companyName", "date", "roundType"]]

def estimate_founded_date(row):
    if pd.isnull(row["date"]):
        return pd.NaT
    return row["date"] - pd.DateOffset(years=1 if row["roundType"] in ["Pre-Seed", "Seed", "Series A", "Series B"] else 2)

first_funding["estimatedFounded"] = first_funding.apply(estimate_founded_date, axis=1)
companies_df = companies_df.merge(first_funding[["companyName", "estimatedFounded"]], on="companyName", how="left")
companies_df["dateFounded"] = companies_df["dateFounded"].fillna(companies_df["estimatedFounded"])
companies_df.drop(columns=["estimatedFounded"], inplace=True, errors="ignore")
companies_df.to_csv("data/companies_final.csv", index=False)
print("✅ `dateFounded` imputed using first funding date and saved in `companies_final.csv`.")

### Scraping Missing Founding Dates from Google Search

def get_google_search_results(company_name, location):
    query = f"{company_name} {location} founded date"
    search_results = list(search(query, num_results=15))
    valid_results = [url for url in search_results if url.startswith("http") and "linkedin" not in url]
    return valid_results

def scrape_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser").get_text()
    except requests.exceptions.RequestException:
        return None

def format_founded_date(date_str):
    return f"{date_str}-01-01" if re.fullmatch(r"\d{4}", date_str) else date_str

def get_founded_date(company_name, location):
    search_results = get_google_search_results(company_name, location)
    scraped_texts = [scrape_webpage(url)[:2000] for url in search_results if scrape_webpage(url)][:5]
    if not scraped_texts:
        return "Not Found"
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Extract the founding date for {company_name} in {location}. Only return the date in YYYY-MM-DD format.\nSources:\n" + "\n".join(scraped_texts)
        response = model.generate_content(prompt)
        return format_founded_date(response.text.strip() if response else "Not Found")
    except:
        return "Error: AI Failure"

missing_companies = companies_df[companies_df["dateFounded"].isna()][["companyName", "ecosystemName"]].dropna().values.tolist()

for company, location in missing_companies:
    founded_date = get_founded_date(company, location)
    companies_df.loc[(companies_df["companyName"] == company) & (companies_df["ecosystemName"] == location), "dateFounded"] = founded_date
    time.sleep(2)

print("✅ Web scraping & AI-assisted date imputation completed!")

### Save Cleaned Companies Data
date_cols = ["dateFounded", "latestRoundDate", "dateAcqusition", "ipoDate", "peDate"]
valid_date_pattern = r"^\d{4}-\d{2}-\d{2}$"
for col in date_cols:
    companies_df[col] = companies_df[col].astype(str)
    companies_df[col] = companies_df[col].where(companies_df[col].str.match(valid_date_pattern), np.nan)

companies_df.to_csv("data/companies_final.csv", index=False)
print("✅ Cleaned company data saved in `companies_final.csv`.")
