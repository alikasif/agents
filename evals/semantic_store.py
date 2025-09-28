import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_community.document_loaders import PyPDFLoader
from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction

class SemanticStore:

    _instance = None  # Class-level variable to hold the single instance

    def __new__(cls):
        if cls._instance is None:
            # If no instance exists, create a new one using the parent's __new__
            cls._instance = super(SemanticStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance


    def __init__(self):

        if(self._initialized):
            return
        

        self.client = chromadb.EphemeralClient()
        self.collection = self.client.create_collection(name="my_collection", 
                                                        embedding_function=OpenAIEmbeddingFunction(
                                                        api_key=os.getenv("OPENAI_API_KEY"),
                                                        model_name=os.getenv("OPENAI_EMBEDDING_MODEL"))
                    )
        self._initialized = True


    def split_doc(self, doc_path: str) -> list[str]:
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        loader = PyPDFLoader(doc_path)
        all_splits = loader.load_and_split(text_splitter=text_splitter)        
        texts = []
        for split in all_splits:
            texts.append(split.page_content)
        return texts


    def store_documents(self, doc_path: str):
        texts = self.split_doc(doc_path)
        ids = [f"doc_{i}" for i in range(len(texts))]
        metadatas = [{"source": doc_path} for _ in texts]
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Stored {len(texts)} documents from {doc_path}.")


    def query(self, query_text: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        result = results['documents']        

        
        final_result = ""
        for i in range(len(result[0])):
            final_result += (result[0][i].replace("\n", " "))

        return final_result

    
# if __name__ == "__main__":
#     load_dotenv(override=True)
#     store = SemanticStore()
#     store.store_documents("evals\\data\\Chapter_2_Routing.pdf")
#     results = store.query("What is LLM based routing?")
    