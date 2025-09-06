from chain_of_agents.workflow_manager import ManagerAgent
from dotenv import load_dotenv
from chunker import Chunker
from graph import ChainofAgentsGraph

def test_chunker():
    chunker = Chunker(10000, 45)
    chunks = chunker.chunk("chain_of_agents\data\economic_survey_2023_24.pdf")
    print(f"Total chunks created: {len(chunks)}")

def process_through_graph():
    graph = ChainofAgentsGraph(
        "chain_of_agents\data\economic_survey_2023_24.pdf",
        "Provide a consice summary of the documents with highlights on key economic indicators, trends and lowlights",
        chunk_size=10000, start_page=45
    )
    app = graph.build_graph()
    config = {"recursion_limit": 30}
    result = app.invoke(input={}, config=config)
    print(f"\n final result :: {result}")



def process_thru_manager():
    manager = ManagerAgent(
        "chain_of_agents\data\economic_survey_2023_24.pdf",
        "Provide a consice summary of the documents with highlights on key economic indicators, trends and lowlights",
        chunk_size=10000, start_page=45
    )

    final_result = manager.execute()
    print(f"\nFinal Result:\n{final_result}\n")

if __name__ == "__main__":
    load_dotenv(override=True)
    #test_chunker()
    process_through_graph()
    #process_thru_manager()

