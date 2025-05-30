# screener_scraper.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import streamlit as st
import requests
from bs4 import BeautifulSoup

CHROMEDRIVER_PATH = "C:\\Users\\kasif\\chromedriver-win64\\chromedriver.exe"
CHROME_USER_DATA_DIR = "D:\\tmp1\\"

def extract_key_metrics(soup):
    metrics = {}
    # Find the 'ul' element containing key metrics
    top_ratios = soup.select("div.company-ratios ul#top-ratios li")

    for li in top_ratios:
        # Get the metric name
        label_tag = li.find("span", class_="name")
        # Get the metric value (with nested spans for numbers)
        value_tag = li.find("span", class_="value")

        if label_tag and value_tag:
            label = label_tag.get_text(strip=True)

            # Join all nested text inside value (e.g., ₹ 2.72 / 1.03 or 0.00 %)
            value = value_tag.get_text(separator=" ", strip=True)

            metrics[label] = value
    return metrics


def get_company_data_screener(ticker: str):

    CHROME_DRIVER_PATH = CHROMEDRIVER_PATH
    CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # <-- Replace if needed

    # === SETUP CHROME ===
    options = Options()
    options.binary_location = CHROME_BINARY_PATH
    options.add_argument("--headless")  # Don't open browser window
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # === LOAD PAGE ===
    url = f"https://www.screener.in/company/{ticker}/"
    driver.get(url)
    time.sleep(5)  # Let JS finish loading

    # === GET HTML ===
    html = driver.page_source
    driver.quit()

    # === PARSE HTML ===
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    data["key_metrics"] = extract_key_metrics(soup)
    st.warning(f"data with key metrics for {ticker}: {data}")


    # --- Company Name ---
    data["company_name"] = soup.find("h1").text.strip() if soup.find("h1") else "N/A"

    # --- About Section ---
    about = soup.find("div", class_="company-profile")
    data["about"] = about.text.strip() if about else "N/A"

    # --- Financial Tables ---
    tables_data = {}
    tables = soup.find_all("table")

    for table in tables:
        title_tag = table.find_previous("h2")
        title = title_tag.text.strip() if title_tag else "Unnamed Table"

        headers = [th.text.strip() for th in table.select("thead th")]
        rows = []

        for row in table.select("tbody tr"):
            cols = [td.text.strip() for td in row.find_all("td")]
            if cols:
                row_dict = dict(zip(headers, cols))
                rows.append(row_dict)

        if headers and rows:
            tables_data[title] = {
                "headers": headers,
                "rows": rows
            }

    data["tables"] = tables_data
    #st.warning(f"data for {ticker}: {data}")
    return data


def get_company_data_screener3(ticker: str):

    CHROME_DRIVER_PATH = CHROMEDRIVER_PATH
    CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Adjust if needed

    # === SETUP DRIVER ===
    options = Options()
    options.binary_location = CHROME_BINARY_PATH
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # === SCRAPE ===
    # url = "https://www.screener.in/company/542724/"
    url = f"https://www.screener.in/company/{ticker}/"
    driver.get(url)
    time.sleep(3)  # Wait for JS to render
    data = {}

    try:
        # Get financial highlights
        highlights = driver.find_elements(By.CSS_SELECTOR, ".company-ratios .row .col")
        ratings = driver.find_elements(By.CLASS_NAME, "rating__score")
        st.warning(f"Highlights for {ticker}: {highlights} {ratings}")
        for i in range(0, len(highlights), 2):
            label = highlights[i].text.strip()
            value = highlights[i + 1].text.strip() if i + 1 < len(highlights) else ""
            data[label] = value
    except Exception as e:
        st.warning(f"Error with {ticker}: {e}")
        print(f"Error with {ticker}: {e}")
        data = {}

    driver.quit()
    return data


def get_company_data_screener2(ticker: str):
    url = f"https://www.screener.in/company/{ticker}/"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"--user-data-dir={CHROME_USER_DATA_DIR}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
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
        st.warning(f"Error with {ticker}: {e}")
        print(f"Error with {ticker}: {e}")
        data = {}

    driver.quit()
    return data
