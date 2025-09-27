import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding

from semantic_kernel.connectors.in_memory import InMemoryStore
from semantic_kernel.connectors.in_memory import InMemoryCollection

from semantic_kernel.exceptions.kernel_exceptions import KernelException
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from data_classes import DataModel
import asyncio
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

class SemanticStore:

    def __init__(self):

        # Initialize the Kernel
        api_key = os.getenv("OPENAI_API_KEY")
        embedding_model_id = os.getenv("OPENAI_EMBEDDING_MODEL")      
        self.kernel = sk.Kernel()

        # Configure the embedding service
        self.kernel.add_service(
            OpenAITextEmbedding(embedding_model_id, api_key)
        )

        self.collection_name = "collection_name"
        
        #self.vector_collection = InMemoryStore.get_collection(self.collection_name, record_type=DataModel)

        self.vector_collection = InMemoryCollection(
            collection_name=self.collection_name,
            record_type=DataModel,
            embedding_generator=OpenAITextEmbedding(ai_model_id=embedding_model_id)  # Optional, if there is no embedding generator set on the record type
        )


    def split_doc(self, doc_path: str) -> list[str]:
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        loader = PyPDFLoader(doc_path)
        all_splits = loader.load_and_split(text_splitter=text_splitter)        
        texts = []
        for split in all_splits:
            texts.append(split.page_content)
        return texts


    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:

        # Generate embeddings for the provided texts
        embedding_generator = self.kernel.get_service(type=OpenAITextEmbedding)
        return asyncio.run(embedding_generator.generate_embeddings(texts))


    def store_embeddings(self, doc_path):
        splits = self.split_doc(doc_path)
        
        embeddings = self.generate_embeddings(splits)

        for i, split in enumerate(splits):
            data_model = DataModel(id=str(i), content=split)
            asyncio.run(self.vector_collection.upsert(data_model))
    

    def query(self, query_text: str, top_k: int = 2):
        try:
            results = asyncio.run(self.vector_collection.search(query_text, top=top_k))
            return results
        except KernelException as e:
            print(f"Error during query: {e}")
            return []


if __name__ == "__main__":
    load_dotenv(override=True)
    store = SemanticStore()
    store.store_embeddings("evals\\data\\Chapter_2_Routing.pdf")
    results = store.query("What is LLM based routing?")
    for result in results:
        print(f"ID: {result.record.id}, Content: {result.record.content}, Score: {result.score}")