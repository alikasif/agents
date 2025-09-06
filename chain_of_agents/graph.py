from chunker import Chunker
from workers import WorkerAgent 
from manager_agent import ManagerAgent
from data_classes import ChainOfAgentState
from prompts import manager_system_message
from langgraph.graph import StateGraph, START, END


class ChainofAgentsGraph:

    def __init__(self, document_path: str, user_goal: str, chunk_size: int = 1000, start_page: int = 0):
        
        self.document_path = document_path
        self.user_goal = user_goal
        self.chunk_size = chunk_size
        self.start_page = start_page


    def create_chunks(self, state: ChainOfAgentState):
        chunker = Chunker(self.chunk_size, self.start_page)
        document_chunks = chunker.chunk(self.document_path)
        return {"chunks": document_chunks}
    
    def process_single_chunk(self, state: ChainOfAgentState):

        chunks = state["chunks"]
        chunk = chunks.pop(0)
        
        previous_result = None
        index =0
        if state.get("worker_agent_results"):
            previous_result = state["worker_agent_results"][-1].current_result
            index = len(state["worker_agent_results"])
        else:
            print(f"No previous results found".upper())

        worker = WorkerAgent(
            name=f"Worker-{index + 1}",
            goal=self.user_goal,
            system_prompt=manager_system_message,
            document_chunk=chunk,
            previous_result=previous_result
        )
        result = worker.perform_task()
        previous_worker_results = state["worker_agent_results"] if state.get("worker_agent_results") else []
        return {"worker_agent_results": previous_worker_results +[result]}

    def has_more_chunks(self, state: ChainOfAgentState):
        if state["chunks"]:
            return "process_single_chunk"
        return "summarize"

    def summarize(self, state: ChainOfAgentState):        
        last_result = state["worker_agent_results"][-1].current_result
        #print(f"finalizng with last worker result {last_result}")
        manager_agent = ManagerAgent(self.user_goal)
        result = manager_agent.finalize_results(last_result)
        return {"final_summary": result}


    def build_graph(self):
        graph = StateGraph(ChainOfAgentState)
        
        graph.add_node("create_chunks", self.create_chunks)
        graph.add_node("process_single_chunk", self.process_single_chunk)
        graph.add_node("summarize", self.summarize)

        graph.add_edge(START, "create_chunks")
        graph.add_edge("create_chunks", "process_single_chunk")
        # graph.add_edge("process_single_chunk", "summarize")  # Add direct edge for completeness

        graph.add_edge("summarize", END)

        graph.add_conditional_edges("process_single_chunk", self.has_more_chunks, 
                {
                    "process_single_chunk": "process_single_chunk",
                    "summarize": "summarize",                    
                }
        )

        app = graph.compile()
        #app.get_graph().print_ascii()
        return app
