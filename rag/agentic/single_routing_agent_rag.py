
from typing import Dict
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from rag.agentic.utils.data_classes import RagState, Grade
from langchain.chat_models import init_chat_model
from rag.agentic.utils.prompt import *
from rag.knowledge_sources.abstract_datasource import AbstractDataSource
from rag.knowledge_sources.vector_db import VectorDBSource
from rag.knowledge_sources.llm_source import LLMSource
from rag.knowledge_sources.web_source import WebSource
import logging

logging.basicConfig(level=logging.INFO) # Set the root logger level to INFO

class SingleRoutingAgentRAG:
    
    def __init__(self):

        self.llm = init_chat_model(model=os.getenv("OPENAI_MODEL"))
        self.grading_model = init_chat_model(model=os.getenv("OPENAI_MODEL"), temperature=0).with_structured_output(Grade)

        self.datasources: Dict[str, AbstractDataSource] = {}
    

    def add_datasource(self, datasource: AbstractDataSource):
        logging.info(f"Registering datasource {datasource.short_name()}")
        self.datasources[datasource.short_name()] = datasource


    def user_input(self, state: RagState):
        """Get user input from console."""
        user_input=  input("Enter your question (type 'exit' to quit): ")
        while not user_input.strip():
            user_input=  input("Please enter a non-empty question (type 'exit' to quit): ")
        return {"query": user_input}
    

    def shall_exit(self, state: RagState) -> bool:
        """Ask user if they want to continue."""
        cont = state["query"]
        if cont.strip().lower() == "exit":
            print("Exiting...")
            return False
        return True


    def datasource_router(self, state: RagState):
        
        if not self.datasources:
            return {"datasource_map": "No datasources registered."}

        lines = []
        for name, ds in self.datasources.items():
            lines.append(f"{name}: {ds.about()}")
        datasource_map =  str({"datasource_map": "\n".join(lines)})
        logging.info(f"datasource_map: {datasource_map}")

        prompt = ROUTER_PROMPT.format(question=state["query"], datasources=datasource_map)
        response = self.llm.invoke([{"role": "user", "content": prompt}])       
        logging.info(f"Routed to datasource {response.content.strip().lower()}")
        return {"selected_datasource": response.content.strip().lower()}


    def search(self, state: RagState):
        
        query = state["query"]
        datasource = self.datasources.get(state["selected_datasource"])
        logging.info(f"Routing to datasource {datasource.short_name()} for query '{query}'")
        responses = datasource.search(query)               
        return {"retreived_docs": responses}


    def grade_documents(self, state: RagState):
        
        docs = state["retreived_docs"]

        #print(f"retreievd doc {docs}")
        
        relevant_docs = []
        for doc in docs:
            prompt  = GRADE_PROMPT.format(question=state["query"], context=doc)
            response = self.grading_model.invoke(
                 [{"role": "user", "content": prompt}]
            )
            print(f"Graded {doc[:50]} :: {response.binary_score} \n\n")
            if response.binary_score == "yes":
                relevant_docs.append(doc)

        return {"graded_docs": relevant_docs}
    

    def has_relevant_docs(self, state: RagState):
        relevant_docs = state.get("graded_docs", [])
        if relevant_docs:
            return "call_llm"
        return "rewrite_question"


    def rewrite_question(self, state: RagState):
        """Rewrite the original user question."""
        
        question = state["query"]
        prompt = REWRITE_PROMPT.format(question=question)
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        logging.info(f"Rewritten question: {response.content}")
        rewrite_count = state.get("question_rewrite_count", 0)
        return {"query": response.content, "orignal_query": question, "question_rewrite_count": rewrite_count+1}
    

    def shall_continue(self, state: RagState):
        rewrite_count = state.get("question_rewrite_count", 0)
        if rewrite_count > 2:
            return END
        return "search"


    def call_llm(self, state: RagState):
        """Call the LLM with system prompt, contexts and user query and return the assistant reply."""
        # Build a simple prompt where we pass context first

        contexts = state["graded_docs"]
        context_text = "\n\n--- Retrieved Context ---\n\n" + "\n\n".join([d for d in contexts])

        print(f"\n\ncontext_text: {context_text}\n\n")

        messages = [
            SystemMessage(content=RAG_PROMPT + context_text),
            HumanMessage(content=state["query"]),
        ]

        prompt = ChatPromptTemplate.from_messages(messages)
        prompt_llm = prompt | self.llm
        result = prompt_llm.invoke({})
        
        # result may be an object depending on the binding; try to extract text
        return {"llm_response": str(result.content)}


    def print_response(self, state: RagState):
        """Print the LLM response to console."""
        if state.get("llm_response"):
            print("\n--- Assistant Response ---\n")
            print(state["llm_response"])
            print("\n--------------------------\n")
        else:
            print("no context found!!")


    def run(self):
        """Interactive loop wired as a LangGraph StateGraph to show conditional edges.

        If the user types 'exit' we stop. Otherwise we search and call the LLM then print.
        """

        workflow = StateGraph(RagState)

        workflow.add_node("get_query", self.user_input)
        workflow.add_node("search", self.search)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("datasource_router", self.datasource_router)
        workflow.add_node("rewrite_question", self.rewrite_question)
        workflow.add_node("call_llm", self.call_llm)
        workflow.add_node("print_response", self.print_response)

        workflow.add_edge(START, "get_query")
        workflow.add_conditional_edges("get_query", self.shall_exit, {True: "datasource_router", False: END})

        workflow.add_edge("datasource_router", "search")        
        workflow.add_edge("search", "grade_documents")
        
        workflow.add_conditional_edges("grade_documents", self.has_relevant_docs, {"call_llm": "call_llm", "rewrite_question": "rewrite_question"})


        workflow.add_conditional_edges("rewrite_question", self.shall_continue, {END: END, "search": "search"})

        workflow.add_edge("call_llm", "print_response")
        workflow.add_edge("print_response", "get_query")

        
        app = workflow.compile()
        app.get_graph().print_ascii()
        app.invoke(input={})


if __name__ == "__main__":
    # Example usage
    load_dotenv(override=True)
    rag = SingleRoutingAgentRAG()    
    
    rag.add_datasource(VectorDBSource(".\\rag\\data\\Chapter_10_Model_Context_Protocol_MCP.pdf"))        
    rag.add_datasource(WebSource())    
    rag.add_datasource(LLMSource())
    
    rag.run()