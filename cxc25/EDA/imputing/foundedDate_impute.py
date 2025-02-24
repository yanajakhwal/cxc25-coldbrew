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