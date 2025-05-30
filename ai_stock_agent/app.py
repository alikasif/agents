# app.py

import streamlit as st
import pandas as pd
import time
import random
from agent import scrape_companies, filter_companies, rank_companies, explain_top_picks, analyze_data
from screener_scraper import get_company_data_screener
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# -------------------------------------------
# Cache scraper and ticker finder
# -------------------------------------------

@st.cache_resource
def get_nse_tickers(limit=200):
    url = "https://www.screener.in/screens/1/Companies-with-high-ROCE/"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    chrome_options = Options()
    chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # Adjust as needed

    service = Service("C:\\Users\\kasif\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    tickers = []

    for row in rows[:limit]:
        try:
            link = row.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            ticker = link.split("/")[-2]
            tickers.append(ticker.upper())
        except Exception as e:
            st.warning(f"⚠️ Ticker read error: {e}")

    driver.quit()
    return tickers

@st.cache_data(show_spinner="Fetching company data...")
def safe_scrape(ticker_list):
    results = []
    for i, ticker in enumerate(ticker_list):
        if ticker == 'THE-BULL-CARTEL':
            continue
        retries = 1
        for attempt in range(retries):
            try:
                st.info(f"getting company data for {ticker}")
                data = get_company_data_screener(ticker)
                st.info(f"company: {ticker} data: {data}")
                if data:
                    results.append(data)
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 + random.random() * 2)  # Backoff
                else:
                    st.warning(f"❌ Failed: {ticker} Exception: {str(e)}")
        st.progress((i + 1) / len(ticker_list), text=f"Scraping {ticker}")
    return results

# -------------------------------------------
# Streamlit App
# -------------------------------------------

st.set_page_config(page_title="📈 NSE AI Screener", layout="wide")
st.title("🤖 NSE AI Stock Screener")
st.markdown("""
This AI agent:
- Automatically finds NSE-listed companies
- Scrapes financial data from Screener.in
- Filters for companies with:
    - >20% YoY Profit Growth
    - <₹5000 Cr Market Cap
    - >15% Stock Price YoY Growth
- Ranks and explains top picks using GPT
""")

limit = st.slider("📊 Number of companies to evaluate", 3, 50, 100, step=5)

if st.button("🚀 Run AI Screener Agent"):
    with st.spinner("🔍 Discovering NSE companies..."):
        tickers = get_nse_tickers(limit=limit)

    with st.spinner("⏳ Scraping data..."):
        scraped = safe_scrape(tickers)

    #analyze_data(scraped)
    df = pd.DataFrame(scraped)
    df.to_csv("filtered_companies.csv", index=False)
    print("Saved to filtered_companies.csv")


    # with st.spinner("📉 Filtering..."):
    #     filtered = filter_companies(scraped)
    #
    # if not filtered:
    #     st.error("😢 No companies matched the criteria.")
    # else:
    #     ranked_df = rank_companies(filtered)
    #     st.success(f"✅ {len(ranked_df)} companies matched criteria.")
    #     st.dataframe(ranked_df, use_container_width=True)
    #
    #     if st.button("💡 GPT Explain Top Picks"):
    #         with st.spinner("Asking GPT..."):
    #             explanation = explain_top_picks(ranked_df)
    #         st.markdown("### 🧠 GPT Insights")
    #         st.markdown(explanation)
