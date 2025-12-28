
import os
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
load_dotenv(override=True)

BudgetLevel = Literal["HIGH", "MEDIUM", "LOW", "CRITICAL"]


@dataclass
class BudgetConfig:
    """Budget configuration and thresholds"""
    
    # Default budget limits
    query_budget: int = 5
    url_budget: int = 5
    
    # Budget level thresholds (percentages)
    high_threshold: float = 0.70  # >= 70%
    medium_threshold: float = 0.30  # 30-70%
    low_threshold: float = 0.10  # 10-30%
    # < 10% is CRITICAL
    
    @property
    def high_queries(self) -> tuple[int, int]:
        """Query range for HIGH budget: 3-5 queries"""
        return (3, 5)
    
    @property
    def high_urls(self) -> tuple[int, int]:
        """URL range for HIGH budget: 2-3 URLs"""
        return (2, 3)
    
    @property
    def medium_queries(self) -> tuple[int, int]:
        """Query range for MEDIUM budget: 2-3 queries"""
        return (2, 3)
    
    @property
    def medium_urls(self) -> tuple[int, int]:
        """URL range for MEDIUM budget: 1-2 URLs"""
        return (1, 2)
    
    @property
    def low_queries(self) -> tuple[int, int]:
        """Query range for LOW budget: 1 query"""
        return (1, 1)
    
    @property
    def low_urls(self) -> tuple[int, int]:
        """URL range for LOW budget: 1 URL max"""
        return (0, 1)


@dataclass
class ModelConfig:
    """Gemini model configuration"""
    
    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")  # Gemini 3 (Flash experimental)
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    temperature: float = 0.7
    max_output_tokens: int = 8192
    
    # For verification module
    verification_model: str = "gemini-3.0-flash"
    verification_temperature: float = 0.3  # Lower temp for more consistent verification


# Global configurations
DEFAULT_BUDGET_CONFIG = BudgetConfig()
DEFAULT_MODEL_CONFIG = ModelConfig()
