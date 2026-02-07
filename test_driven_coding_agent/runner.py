"""
TDD Agent Runner

Entry point for running the TDD agent.
"""

from agent import TDDAgent


def run_tdd(problem: str, model_prefix: str = "GEMINI") -> str:
    """Run TDD agent on a problem."""
    agent = TDDAgent(model_prefix=model_prefix)
    return agent.run(problem)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        problem = sys.argv[1]
    else:
        # problem = """
        # Implement a project to mimic banking with operations like deposit, withdraw, and check balance with multiple users.
        # """

        # problem = """
        #     implement a function to find 2 sum from an array of integers
        # """
    
        problem = """
            Implement a online shopping cart. it must have add_items, get_total_value, get_total_items methods. 
            It should also  have an ability to apply discount at cart level as as per item level discount.
            Discounts can be flat & % based.
        """
    
    print("=" * 60)
    print("TDD Agent - Test Driven Development")
    print("=" * 60)
    print(f"Problem: {problem.strip()[:100]}...")
    print("=" * 60)
    
    result = run_tdd(problem)
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(result)
