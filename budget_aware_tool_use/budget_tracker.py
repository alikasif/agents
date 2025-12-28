

from dataclasses import dataclass
from config import BudgetConfig, BudgetLevel, DEFAULT_BUDGET_CONFIG


@dataclass
class BudgetState:
    """Current budget state"""
    query_used: int = 0
    url_used: int = 0
    query_remaining: int = 0
    url_remaining: int = 0
    
    def to_dict(self) -> dict:
        return {
            "query_used": self.query_used,
            "url_used": self.url_used,
            "query_remaining": self.query_remaining,
            "url_remaining": self.url_remaining
        }


class BudgetTracker:
    """
    Tracks tool usage and provides budget-aware strategy guidance.
    
    Monitors:
    - Query budget (for search tool)
    - URL budget (for browse tool)
    - Budget levels: HIGH (≥70%), MEDIUM (30-70%), LOW (10-30%), CRITICAL (<10%)
    """
    
    def __init__(self, config: BudgetConfig = None):
        self.config = config or DEFAULT_BUDGET_CONFIG
        
        # Initialize budgets
        self.query_budget = self.config.query_budget
        self.url_budget = self.config.url_budget
        
        # Track usage
        self.query_used = 0
        self.url_used = 0
    
    def track_tool_usage(self, tool_name: str, count: int) -> None:
        """
        Track tool usage.
        
        Args:
            tool_name: 'search' or 'browse'
            count: Number of queries/URLs used
        """
        if tool_name == "search":
            self.query_used += count
        elif tool_name == "browse":
            self.url_used += count
    
    def get_remaining(self, tool_name: str) -> int:
        """Get remaining budget for a tool"""
        if tool_name == "search":
            return max(0, self.query_budget - self.query_used)
        elif tool_name == "browse":
            return max(0, self.url_budget - self.url_used)
        return 0
    
    def get_budget_level(self, tool_name: str) -> BudgetLevel:
        """
        Classify budget level for a tool.
        
        Returns:
            HIGH: ≥70% remaining
            MEDIUM: 30-70% remaining
            LOW: 10-30% remaining
            CRITICAL: <10% remaining or depleted
        """
        remaining = self.get_remaining(tool_name)
        total = self.query_budget if tool_name == "search" else self.url_budget
        
        if total == 0:
            return "CRITICAL"
        
        percentage = remaining / total
        
        if percentage >= self.config.high_threshold:
            return "HIGH"
        elif percentage >= self.config.medium_threshold:
            return "MEDIUM"
        elif percentage >= self.config.low_threshold:
            return "LOW"
        else:
            return "CRITICAL"
    
    def get_overall_budget_level(self) -> BudgetLevel:
        """
        Get overall budget level (minimum of query and URL budgets).
        This determines the agent's overall strategy.
        """
        query_level = self.get_budget_level("search")
        url_level = self.get_budget_level("browse")
        
        # Return the more restrictive level
        levels = ["HIGH", "MEDIUM", "LOW", "CRITICAL"]
        query_idx = levels.index(query_level)
        url_idx = levels.index(url_level)
        
        return levels[max(query_idx, url_idx)]
    
    def get_strategy_guidance(self) -> dict:
        """
        Get budget-aware strategy guidance based on current budget level.
        
        Returns:
            Dictionary with recommendations for search and browse tools
        """
        level = self.get_overall_budget_level()
        query_level = self.get_budget_level("search")
        url_level = self.get_budget_level("browse")
        
        guidance = {
            "overall_level": level,
            "query_level": query_level,
            "url_level": url_level,
            "recommendations": {}
        }
        
        # Add recommendations based on level
        if level == "HIGH":
            guidance["recommendations"] = {
                "search": f"{self.config.high_queries[0]}-{self.config.high_queries[1]} diverse queries",
                "browse": f"up to {self.config.high_urls[0]}-{self.config.high_urls[1]} high-value URLs",
                "goal": "Broad exploration, build context fast"
            }
            guidance["max_queries"] = self.config.high_queries[1]
            guidance["max_urls"] = self.config.high_urls[1]
            
        elif level == "MEDIUM":
            guidance["recommendations"] = {
                "search": f"{self.config.medium_queries[0]}-{self.config.medium_queries[1]} precise queries",
                "browse": f"{self.config.medium_urls[0]}-{self.config.medium_urls[1]} URLs to close gaps",
                "goal": "Converge; eliminate uncertainty efficiently"
            }
            guidance["max_queries"] = self.config.medium_queries[1]
            guidance["max_urls"] = self.config.medium_urls[1]
            
        elif level == "LOW":
            guidance["recommendations"] = {
                "search": f"{self.config.low_queries[0]} tightly focused query",
                "browse": f"at most {self.config.low_urls[1]} promising URL",
                "goal": "Verify a single critical fact or finalize answer"
            }
            guidance["max_queries"] = self.config.low_queries[1]
            guidance["max_urls"] = self.config.low_urls[1]
            
        else:  # CRITICAL
            query_remaining = self.get_remaining("search")
            url_remaining = self.get_remaining("browse")
            
            if query_remaining == 0 and url_remaining == 0:
                guidance["recommendations"] = {
                    "search": "DEPLETED - no queries allowed",
                    "browse": "DEPLETED - no browsing allowed",
                    "goal": "Must provide answer or output 'None' if uncertain"
                }
            elif query_remaining == 0:
                guidance["recommendations"] = {
                    "search": "DEPLETED - avoid search",
                    "browse": "1 minimal-cost URL if absolutely essential",
                    "goal": "Finalize with remaining browse budget only"
                }
            elif url_remaining == 0:
                guidance["recommendations"] = {
                    "search": "1 minimal-cost query if absolutely essential",
                    "browse": "DEPLETED - avoid browse",
                    "goal": "Finalize with remaining query budget only"
                }
            else:
                guidance["recommendations"] = {
                    "search": "1 minimal-cost query if absolutely essential",
                    "browse": "1 minimal-cost URL if absolutely essential",
                    "goal": "Finalize answer or output 'None'"
                }
            
            guidance["max_queries"] = min(1, query_remaining)
            guidance["max_urls"] = min(1, url_remaining)
        
        return guidance
    
    def format_budget_message(self) -> str:
        """
        Format budget status message for inclusion in agent prompts.
        
        Returns:
            Formatted string showing current budget state
        """
        query_remaining = self.get_remaining("search")
        url_remaining = self.get_remaining("browse")
        
        message = f"""<budget>
Query Budget: {self.query_used}/{self.query_budget} used, {query_remaining} remaining
URL Budget: {self.url_used}/{self.url_budget} used, {url_remaining} remaining
Budget Level: {self.get_overall_budget_level()}
</budget>"""
        
        return message
    
    def get_state(self) -> BudgetState:
        """Get current budget state"""
        return BudgetState(
            query_used=self.query_used,
            url_used=self.url_used,
            query_remaining=self.get_remaining("search"),
            url_remaining=self.get_remaining("browse")
        )
    
    def can_use_tool(self, tool_name: str, count: int = 1) -> bool:
        """Check if tool can be used with given count"""
        return self.get_remaining(tool_name) >= count
    
    def reset(self) -> None:
        """Reset budget tracker"""
        self.query_used = 0
        self.url_used = 0
