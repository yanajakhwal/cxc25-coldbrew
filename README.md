# Startups Analytics & Insights Dashboard

## 📌 Overview
This dashboard provides in-depth analysis and forecasting for the **Canadian startup investment ecosystem**. It leverages data on investments, funding stages, investor behavior, and sectoral trends to provide valuable insights for investors, entrepreneurs, and policymakers.

## 🚀 Features
- **Investment Trends Over Time**: Analyzes yearly and quarterly investment trends.
- **Funding Stages Analysis**: Examines the evolution of funding rounds and deal sizes.
- **Investor Demographics & Behavior**: Identifies key investors and their geographic distribution.
- **Sectoral & Regional Insights**: Compares sectoral growth and regional investment trends.
- **Forecasting**: Uses machine learning models to predict future investment trends.
- **Interactive Visualizations**: Built with **Streamlit** and **Plotly** for an intuitive user experience.

## 📂 Project Structure
```
📦 cxc25
├── 📂 dashboard
│   ├── Home.py                 # Main entry point for the Streamlit app
│   ├── 📂 pages
│   │   ├── Funding Stages Analysis.py  # Funding Stages Analysis Page
│   │   ├── Investment Trends.py   # Investor Behavior Page
│   │   ├── Investor Demographics & Behavior.py    # Investment Trends Over Time Page
│   │   ├── Sectoral & Regional Insights.py    # Sectoral & Regional Insights Page
│   ├── 📂 images               # Stores icons and other UI assets
 ###### MUST BE EXPORTED FROM RUNQL ########
├── 📂 data
│   ├── deals.csv               # Investment deals dataset
│   ├── dealInvestor.csv        # Deal-Investor mapping
│   ├── companies.csv           # Company details dataset
│   ├── investors.csv           # Investor details dataset
├── 📂 processing                 
│   ├── EDA.ipynb               # Exploratory Data Analysis
│   ├── exploring.ipynb         # Deal-Investor mapping
│   ├── forecasting.ipynb       # Company details dataset
│   ├── imputation.py           # imputes missing data
├── README.md                   # Documentation
├── requirements.txt            # Python dependencies
└── .gitignore                  # Ignoring unnecessary files
```

## 🛠️ Installation & Setup
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/yanajakhwal/cxc25.git
cd cxc25
```

### **2️⃣ Create a Virtual Environment**
```bash
python3 -m venv env
source env/bin/activate  # Mac/Linux
env\Scripts\activate     # Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Run the data preprocessing file**
```bash
python3 imputation.py
```

### **5️⃣ Run the Streamlit App**
```bash
streamlit run dashboard/Home.py
```

## 🏗️ How It Works
- The app loads investment data dynamically from **RunQL's database**, ensuring up-to-date insights.
- Users can filter data by **year, region, sector, and funding stage**.
- Forecasting models predict future investment trends based on **historical data**.

## ⚠️ Notes
- Ensure **RunQL data is used directly within the platform** (no CSV exports for final submission).

## 👥 Contributors
- **Yana Jakhwal** (Lead Developer)

## 📜 License
This project is for **educational and research purposes**. Please comply with **RunQL's data usage policies**.

---
### 🎯 Ready to explore Canadian startup investments? Run the dashboard and start analyzing!
