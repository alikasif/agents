import asyncio
from dotenv import load_dotenv

def invoke_agent(user_input: str):
    """
    Example function to invoke the API endpoint assistant agent with a user query.
    """
    from agent import execute_user_query

    try:
        response = asyncio.run(execute_user_query(user_input=user_input))
        print(f"\ninput: {user_input} \nResponse from agent:", response)
    except Exception as e:
        print(f"Error invoking agent: {str(e)}")

if __name__ == "__main__":
    load_dotenv(override=True)
    input_query = input("Enter your query: ")
    invoke_agent(input_query)