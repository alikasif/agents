
from data_classes import RAGState
from semantic_store import SemanticStore

class RAG:

    def __init__(self):
        self.vectore_store = SemanticStore()

    def store(self, state: RAGState):
        doc_path = state.document_path
        if not state.document_read:
            pass
        
        self.vectore_store.store_embeddings()

    def user_query(self, state: RAGState):
        pass

    def query_db(self, state: RAGState):
        pass

    def generate_response(self, state: RAGState):
        pass