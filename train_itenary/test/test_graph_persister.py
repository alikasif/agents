import logging
from graph_persister import save_graph, load_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_persistence():
    # Create a dummy graph
    original_graph = {
        ("NDLS", "AGC"): [
            {
                "train_number": "12002",
                "train_name": "SHATABDI EXP",
                "departure_time": 1672531200,
                "arrival_time": 1672538400
            }
        ],
        ("AGC", "GWL"): [
            {
                "train_number": "12002",
                "train_name": "SHATABDI EXP",
                "departure_time": 1672538700,
                "arrival_time": 1672542000
            }
        ]
    }
    
    filename = "test_graph.pkl"
    
    # Save graph
    logger.info("Saving graph...")
    if not save_graph(original_graph, filename):
        logger.error("Failed to save graph")
        return

    # Load graph
    logger.info("Loading graph...")
    loaded_graph = load_graph(filename)
    
    # Verify
    if original_graph == loaded_graph:
        logger.info("SUCCESS: Loaded graph matches original graph.")
    else:
        logger.error("FAILURE: Loaded graph does not match original graph.")
        logger.info(f"Original: {original_graph}")
        logger.info(f"Loaded: {loaded_graph}")

if __name__ == "__main__":
    test_persistence()
