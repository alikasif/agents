from fastapi import FastAPI, HTTPException
from langchain_community.utilities import GoogleSerperAPIWrapper
from typing import Optional, Union
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Web Search API",
    description="API for searching the web using Google Serper API"
)

class SearchResponse(BaseModel):
    query: str
    results: dict

@app.get("/search/", response_model=SearchResponse)
async def search_web(query: str):
    try:
        print(f"Received search query: {query}")
        
        # Initialize the Serper API wrapper
        search = GoogleSerperAPIWrapper()
        
        # Perform the search
        results = search.run(query)
        
        # If results is a string, wrap it in a dictionary
        if isinstance(results, str):
            results = {"text": results}
        
        return SearchResponse(
            query=query,
            results=results
        )
    except Exception as e:
        print(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8882)