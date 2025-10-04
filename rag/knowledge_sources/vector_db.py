from typing import List
import os

from langchain_openai import ChatOpenAI

from langchain_openai.embeddings import OpenAIEmbeddings
import chromadb
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from chromadb.utils import embedding_functions
from rag.knowledge_sources.abstract_datasource import AbstractDataSource
import logging

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class VectorDBSource(AbstractDataSource):

    """
        A vector DB source for the document to index and do semantic search
    """

    def __init__(self, doc_path: str):
        
        # Create an OpenAI embedding function (requires OpenAI API key)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL")
        )

        # in-memory chroma
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("all-my-documents", embedding_function=openai_ef)
        self.semantic_splitter = SemanticChunker(OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL")))

        self._read_and_index(doc_path)


    def _read_and_index(self, doc_path: str):
        """Read raw text documents into in-memory Document objects."""
        logging.info(f"Indexing document from {doc_path}")
        loader = PyMuPDFLoader(doc_path)
        documents = loader.load()
        split_docs = self.semantic_splitter.split_documents(documents)
        logging.info(f"adding chunks to db..")
        self.collection.add(documents=[d.page_content for d in split_docs],
                            metadatas=[d.metadata for d in split_docs],
                            ids=[str(i) for i in range(len(split_docs))])


    def search(self, query: str) -> List[str]:
        """Search the vector store using LangChain retriever semantics."""
        results = self.collection.query(query_texts=[query], n_results=2)
        docs = []
        for content, metadata in zip(results['documents'][0], results['metadatas'][0]):
            docs.append(content)
        
        return docs

    def about(self):
        return "This is a Vector DB source that has information about Model Context Protocol aka MCP"
    
    def short_name(self) -> str:
        return "vector_db"