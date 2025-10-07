import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai.embeddings import OpenAIEmbeddings
import chromadb
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from chromadb.utils import embedding_functions
from rag.agentic.utils.data_classes import RagState
from langchain.chat_models import init_chat_model


class HydeRag:
    """A minimal Retrieval-Augmented Generation implementation using LangGraph and
    an in-memory Chroma vector store. The flow:
      - read(files) -> chunks/docs
      - index() -> embedding + Chroma
      - run() -> interactive loop: get user query, if 'exit' -> stop, else search retriever
        and call LLM with system prompt + retrieved context + user query, then print response.

    This is intentionally small and depends on OpenAI credentials configured in env.
    """

    def __init__(self, doc_path: str):

        self.llm = init_chat_model(model=os.getenv("OPENAI_MODEL"))        
        
        # Create an OpenAI embedding function (requires OpenAI API key)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL")
        )

        # in-memory chroma
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("all-my-documents", embedding_function=openai_ef)
        #self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
        self.semantic_splitter = SemanticChunker(OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL")))


        # simple system prompt template
        self.system_prompt = (
            "You are a helpful assistant. Use the provided context to answer the user's question. "
            "If the answer is not contained within the context, say you don't know and do not hallucinate."
        )

        self._read_and_index(doc_path)


    def _read_and_index(self, doc_path: str):
        """Read raw text documents into in-memory Document objects."""
        loader = PyMuPDFLoader(doc_path)
        documents = loader.load()
        split_docs = self.semantic_splitter.split_documents(documents)
        self.collection.add(documents=[d.page_content for d in split_docs],
                            metadatas=[d.metadata for d in split_docs],
                            ids=[str(i) for i in range(len(split_docs))])


    def user_input(self, state: RagState):
        """Get user input from console."""
        user_input=  input("Enter your question (type 'exit' to quit): ")
        return {"query": user_input}
    

    def shall_continue(self, state: RagState) -> bool:
        """Ask user if they want to continue."""
        cont = state["query"]
        if cont.strip().lower() == "exit":
            print("Exiting...")
            return False
        return True


    def hyde_retrieve(self, state: RagState):
        """Perform HyDE: generate a hypothetical answer to the query using the LLM, then use that to retrieve documents."""
        query = state["query"]
        hyde_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a helpful assistant that generates a detailed answer to the user's question. If you don't know, make a plausible answer."),
            HumanMessage(content=f"Q: {query}\nA:")
        ])
        hyde_chain = hyde_prompt | self.llm
        hypothetical_answer = hyde_chain.invoke({})

        print(f"\n\nHypothetical Answer: {hypothetical_answer.content}\n\n")
        #print(f"state: {state}\n\n")
        return {"hyde_retreival": str(hypothetical_answer.content)}


    def search(self, state: RagState):
        """Search the vector store using LangChain retriever semantics."""
        query = state["hyde_retreival"]
        results = self.collection.query(query_texts=[query], n_results=2)
        docs = []
        for content, metadata in zip(results['documents'][0], results['metadatas'][0]):
            docs.append(Document(page_content=content, metadata=metadata))
        return {"retreived_docs": docs}


    def call_llm(self, state: RagState):
        """Call the LLM with system prompt, contexts and user query and return the assistant reply."""
        # Build a simple prompt where we pass context first

        contexts = state["retreived_docs"]
        context_text = "\n\n--- Retrieved Context ---\n\n" + "\n\n".join([d.page_content for d in contexts])

        print(f"\n\ncontext_text: {context_text}\n\n")

        messages = [
            SystemMessage(content=self.system_prompt + context_text),
            HumanMessage(content=state["query"]),
        ]

        prompt = ChatPromptTemplate.from_messages(messages)
        prompt_llm = prompt | self.llm
        result = prompt_llm.invoke({})
        
        # result may be an object depending on the binding; try to extract text
        return {"llm_response": str(result.content)}


    def print_response(self, state: RagState):
        """Print the LLM response to console."""
        print("\n--- Assistant Response ---\n")
        print(state["llm_response"])
        print("\n--------------------------\n")


    def run(self):
        """Interactive loop wired as a LangGraph StateGraph to show conditional edges.

        If the user types 'exit' we stop. Otherwise we search and call the LLM then print.
        """

        # Build a tiny LangGraph workflow to demonstrate conditional branching

        workflow = StateGraph(RagState)
        workflow.add_node("get_query", self.user_input)
        workflow.add_node("hyde_retrieve", self.hyde_retrieve)
        workflow.add_node("search", self.search)        
        workflow.add_node("call_llm", self.call_llm)
        workflow.add_node("print_response", self.print_response)

        workflow.add_edge(START, "get_query")
        workflow.add_conditional_edges("get_query", self.shall_continue, {True: "hyde_retrieve", False: END})
        workflow.add_edge("hyde_retrieve", "search")
        workflow.add_edge("search", "call_llm")        
        workflow.add_edge("call_llm", "print_response")
        workflow.add_edge("print_response", "get_query")
        
        app = workflow.compile()
        app.get_graph().print_ascii()
        app.invoke(input={})


if __name__ == "__main__":
    # Example usage
    load_dotenv(override=True)
    rag = HydeRag(".\\rag\\data\\Chapter_10_Model_Context_Protocol_MCP.pdf")    
    rag.run()


