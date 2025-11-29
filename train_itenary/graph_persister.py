import pickle
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

def save_graph(graph: Dict[Tuple[str, str], List[Dict[str, Any]]], filename: str) -> bool:
    """
    Save the train graph to a file using pickle.
    
    Args:
        graph: The dictionary graph to save.
        filename: The path to the file where the graph will be saved.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        with open(filename, 'wb') as f:
            pickle.dump(graph, f)
        logger.info(f"Graph saved successfully to {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to save graph to {filename}: {e}")
        return False

def load_graph(filename: str) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
    """
    Load the train graph from a pickle file.
    
    Args:
        filename: The path to the file to load the graph from.
        
    Returns:
        The loaded graph dictionary, or an empty dictionary if loading fails.
    """
    try:
        with open(filename, 'rb') as f:
            graph = pickle.load(f)
        logger.info(f"Graph loaded successfully from {filename}")
        return graph
    except FileNotFoundError:
        logger.error(f"Graph file not found: {filename}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load graph from {filename}: {e}")
        return {}
