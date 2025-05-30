
import os
import time
import pandas as pd
from typing import List, Dict, Any
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# -- Constants --
CSV_PATH = "companies.csv"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"  # Change if needed
CHROME_USER_DATA_DIR = "/tmp/chrome_screener_session"

# -- Selenium scraping function --
def get_company_data_screener(ticker: str) -> Dict[str, Any]:
    url = f"https://www.screener.in/company/{ticker}/"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    time.sleep(2)

    try:
        mc = driver.find_element(By.XPATH, "//li[b[contains(text(),'Market Cap')]]").text
        pg = driver.find_element(By.XPATH, "//li[b[contains(text(),'Profit growth')]]").text
        spg = driver.find_element(By.XPATH, "//li[b[contains(text(),'Return over 1 year')]]").text
        ratings = driver.find_elements(By.CLASS_NAME, "rating__score")

        data = {
            "Ticker": ticker,
            "Market_Cap_Cr": float(mc.split(":")[1].replace("Cr", "").replace(",", "").strip()),
            "YoY_Profit_Growth": float(pg.split(":")[1].replace("%", "").strip()),
            "YoY_Stock_Growth": float(spg.split(":")[1].replace("%", "").strip()),
            "Quality": float(ratings[0].text),
            "Growth": float(ratings[1].text),
            "Valuation": float(ratings[2].text),
            "Momentum": float(ratings[3].text),
        }

    except Exception as e:
        print(f"Error with {ticker}: {e}")
        data = {}

    driver.quit()
    return data

# -- LangChain Tool Definitions --

def scrape_companies(tickers: List[str]) -> List[Dict[str, Any]]:
    return [get_company_data_screener(ticker) for ticker in tickers]

def filter_companies(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        c for c in data
        if c and c["YoY_Profit_Growth"] > 20 and
           c["Market_Cap_Cr"] < 5000 and
           c["YoY_Stock_Growth"] > 15
    ]

def rank_companies(data: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df["Score"] = (
            0.3 * df["Quality"] +
            0.3 * df["Growth"] +
            0.2 * df["Valuation"] +
            0.2 * df["Momentum"]
    )
    return df.sort_values(by="Score", ascending=False)

# Define LangChain Tools
tools = [
    Tool(
        name="ScrapeCompanyData",
        func=lambda q: scrape_companies(q.split(",")),
        description="Scrape financial data from Screener.in for comma-separated tickers"
    ),
    Tool(
        name="FilterCompanies",
        func=filter_companies,
        description="Filter companies with >20% YoY profit, <5000Cr market cap, and >15% YoY stock growth"
    ),
    Tool(
        name="RankCompanies",
        func=rank_companies,
        description="Rank companies based on quality, growth, valuation, and momentum"
    )
]

# Initialize Agent
llm = ChatOpenAI(temperature=0.3, model="gpt-4")  # or "gpt-3.5-turbo"
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Load companies from CSV
company_df = pd.read_csv(CSV_PATH)
tickers = ",".join(company_df["Company"].dropna().unique())

# Start agent with a prompt
prompt = f"""
Here are some NSE tickers: {tickers}.
Your goal is to:
1. Scrape data for them.
2. Filter companies based on profit > 20%, market cap < 5000Cr, and stock growth > 15%.
3. Rank them by quality, growth, valuation, and momentum.
Then explain your top 3 picks.
"""

agent.run(prompt)
