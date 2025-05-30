# financial_analysis_agent.py

from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore import InMemoryDocstore
from langchain.memory import VectorStoreRetrieverMemory
from langchain.schema import SystemMessage
import pandas as pd
import requests
from bs4 import BeautifulSoup

### --- Tool 1: Screener Scraper --- ###
class ScreenerScraperTool(BaseTool):
    name = "ScreenerScraper"
    description = "Scrapes financial data from Screener.in for a given company URL."

    def _run(self, url: str):
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            data = {}

            # Extract basic financial metrics
            ratios_table = soup.find('section', {'id': 'top-ratios'})
            if ratios_table:
                for row in ratios_table.find_all('li'):
                    key = row.find('span').text.strip()
                    value = row.find('strong').text.strip()
                    data[key] = value

            return data
        except Exception as e:
            return {"error": str(e)}

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")


### --- Tool 2: Financial Filter --- ###
def filter_companies(companies: list, metric: str, threshold: float, greater=True):
    """Filter companies based on a financial metric."""
    filtered = []
    for company in companies:
        value = company.get(metric, None)
        if value:
            try:
                val = float(value.replace('%', '').replace(',', ''))
                if (greater and val > threshold) or (not greater and val < threshold):
                    filtered.append(company)
            except:
                continue
    return filtered

class FinancialFilterTool(BaseTool):
    name = "DataFilterTool"
    description = "Filters list of company data based on a specific financial metric."

    def _run(self, companies_json: list, metric: str, threshold: float, greater: bool=True):
        return filter_companies(companies_json, metric, threshold, greater)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


### --- Tool 3: Insight Generator --- ###
class InsightGeneratorTool(BaseTool):
    name = "InsightGeneratorTool"
    description = "Generates qualitative business insights for a company based on its financial data."

    def __init__(self, llm):
        super().__init__()
        self.llm = llm

    def _run(self, company_data: dict):
        prompt = f"""
        Given the following financial data:
        {company_data}

        Generate a qualitative business summary. Include strengths, weaknesses, and risks.
        """
        return self.llm.predict(prompt)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError()


### --- Vector Memory Setup --- ###
embedding_model = OpenAIEmbeddings()
vectorstore = FAISS(embedding_model.embed_query, InMemoryDocstore({}), {})
memory = VectorStoreRetrieverMemory(retriever=vectorstore.as_retriever())

### --- Agent Setup --- ###
llm = ChatOpenAI(temperature=0, model_name="gpt-4")

tools = [
    ScreenerScraperTool(),
    FinancialFilterTool(),
    InsightGeneratorTool(llm=llm)
]

agent = initialize_agent(
    tools,
    llm,
    agent="openai-functions",
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": SystemMessage(
            content="You are a financial research analyst helping an investor evaluate companies based on financial data."
        )
    }
)

### --- Example Usage --- ###
# Example: Run this after you have scraped multiple company URLs.
# data = [ScreenerScraperTool()._run(url) for url in list_of_urls]
# filtered = FinancialFilterTool()._run(data, 'ROE', 15.0)
# for company in filtered:
#     print(InsightGeneratorTool(llm)._run(company))
