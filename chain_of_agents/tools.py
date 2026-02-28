from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dataclasses import InformationChunk
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from dotenv import load_dotenv
import os


class Chunker:
    def __init__(self, chunk_size: int, start_page: int = 0):
        load_dotenv(override=True)
        self.chunk_size = chunk_size
        self.start_page = start_page
        self.text_splitter = SemanticChunker(OpenAIEmbeddings(),
                                            breakpoint_threshold_type="percentile",
                                            min_chunk_size=self.chunk_size,)


    def _read(self, file_path: str) -> str:
        
        # """Reads the content of a text file."""
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     return file.read()
        
        loader = PyPDFLoader(file_path)
        pages = []
        page_count = 0
        for page in loader.lazy_load():
            pages.append(page.page_content)
            page_count += 1

        return pages


    def chunk(self, file_path: str) -> list[InformationChunk]:
        """Splits the input text into chunks of specified size."""

        pages = self._read(file_path)

        print(f"total pages in document: {len(pages)}")

        docs = self.text_splitter.create_documents(pages[self.start_page: self.start_page + 5],)
        
        doc_chunks= []
        start_index = 0
        end_index = 0
        
        for doc in docs:
            start_index = end_index
            end_index = start_index + len(doc.page_content)
            chunk = InformationChunk(doc.page_content, start_index , end_index)
            doc_chunks.append(chunk)
            print(f"\nCreated chunk: {chunk}")
        
        return doc_chunks


class LLM:

    def __init__(self, structured_output_class: type = None):
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"))
        self.llm = self.llm if not structured_output_class else self.llm.with_structured_output(structured_output_class)

    def invoke(self, system_prompt: str, user_prompt: str) -> str:

        messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
        
        prompt_template = ChatPromptTemplate.from_messages(messages)

       
        prompt_llm = prompt_template | self.llm

        result = prompt_llm.invoke({})
            
        # Placeholder for actual LLM API call
        return result
