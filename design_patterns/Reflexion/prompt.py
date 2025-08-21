from langchain_core.prompts import PromptTemplate

intial_prompt = PromptTemplate(
    input_variables=["query"],
    template="Write best possible python code for {query}. Dont include any test run example. " \
        "Your response must contain only the code to solve the user query."
    )

reflection_prompt = PromptTemplate(
    input_variables=["initial_response", "query"],
    template=
            "You are a senior lead python code reviewer. You will review following code: {initial_response} for the query: {query}."
            "Provide detailed code review focused on improving the code quality, performance, modularity, testability, and readability."
            "Do not add review comments for adding unit test but do add review comments for testability of code."
            "Review comments must include only the improvements required."
            "if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments."
            "Respond with code review comments only. Dont include the improved code in your response."
    )


refinement_prompt = PromptTemplate(
    input_variables=["initial_response", "reflection", "query"],
    template="Given the initial response to '{query}':\n\n{initial_response}\n\n"
            "And the following critique and recommendations:\n\n{reflection}\n\n"
            "Produce a refined and improved version of the python code. Respond with only the code."
    )
