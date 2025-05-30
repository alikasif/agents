# agent.py
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from typing import List, Dict
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate

# Use functions from screener_scraper.py
from screener_scraper import get_company_data_screener

def scrape_companies(tickers: List[str]) -> List[Dict]:
    return [get_company_data_screener(ticker) for ticker in tickers]

def filter_companies(data: List[Dict]) -> List[Dict]:
    return [
        c for c in data
        if c and c["YoY_Profit_Growth"] > 10 and
           c["Market_Cap_Cr"] < 100 and
           c["YoY_Stock_Growth"] > 10
    ]

def rank_companies(data: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df["Score"] = (
            0.3 * df["Quality"] +
            0.3 * df["Growth"] +
            0.2 * df["Valuation"] +
            0.2 * df["Momentum"]
    )
    return df.sort_values(by="Score", ascending=False)

def explain_top_picks(df: pd.DataFrame, top_n=3) -> str:
    top = df.head(top_n).to_dict(orient="records")
    llm = ChatOpenAI(temperature=0.3, model="gpt-4")
    company_summary = "\n".join([f"{i+1}. {d['Ticker']} - Score: {d['Score']:.2f}" for i, d in enumerate(top)])
    prompt = f"Given these ranked companies:\n{company_summary}\nExplain why they are good investment candidates based on quality, growth, valuation, and momentum."
    return llm.predict(prompt)

def analyze_data(data: List[Dict]) :

    open_api_key='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'

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=open_api_key)

    prompt_template = ChatPromptTemplate.from_template("""
        You are a financial analyst. Analyze the following company based on its financial metrics and performance history.
        
        Company Name: {company_name}
        Business Overview: {about}
        Key Metrics: {key_metrics}
        Recent Quarterly Sales: {quarterly_sales}
        Recent Net Profits: {quarterly_profits}
        Annual Revenue Trend: {annual_revenue}
        Annual Profit Trend: {annual_profits}
        Balance Sheet Highlights: {balance_sheet}
        
        Give a reasoned summary of whether this company shows improving performance, signs of profitability, and long-term viability. Be specific and provide a conclusion.
        
        Analysis:
    """)

    chain = LLMChain(llm=llm, prompt=prompt_template)
    for company_data in data:

        quarterly = company_data['tables']['Quarterly Results']
        sales = [row for row in quarterly['rows'] if row[''] == 'Sales\xa0+'][0]
        profits = [row for row in quarterly['rows'] if row[''] == 'Net Profit\xa0+'][0]

        annual = company_data['tables']['Profit & Loss']
        annual_sales = [row for row in annual['rows'] if row[''] == 'Sales\xa0+'][0]
        annual_profits = [row for row in annual['rows'] if row[''] == 'Net Profit\xa0+'][0]

        balance_sheet = company_data['tables']['Balance Sheet']
        # optionally pull reserves, debt, equity, etc.

        response = chain.run({
            "company_name": company_data['company_name'],
            "about": company_data['about'],
            "key_metrics": str(company_data['key_metrics']),
            "quarterly_sales": str(sales),
            "quarterly_profits": str(profits),
            "annual_revenue": str(annual_sales),
            "annual_profits": str(annual_profits),
            "balance_sheet": "some summary of equity, reserves, borrowings",
        })

        print(response)
