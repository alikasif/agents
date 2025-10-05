
RETREIVAL_GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)

ROUTER_PROMPT = """
    You are a router assistant. You will tell which datasource to use for the given question {question}
    You will be given a mapping of datasource name to its description.

    Datasources mapping:

    {datasources}

    If none of the available datasource is appropriate to answer the question the just respond with "None"
"""

RAG_PROMPT= (
            "You are a helpful assistant. Use the provided context to answer the user's question. "
            "If the answer is not contained within the context, say you don't know and do not hallucinate."
        )

QUERY_PLANNING_PROMPT = (
    "You are a query planning assistant. You will help to break down the user's complex question into simpler sub-questions that can be answered using available datasources. \n"
    "Break the question into maximum 5 simpler sub-questions that are specific and clear. \n"
    "Each question should be self-contained and not depend on other sub-questions. \n"
    "If the question is already simple, just return the original question as the only sub-question. \n"
    "Here is the user question: {question} \n"
)


HALLUCINATION_GRADE_PROMPT = """
    You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. 'Yes' means that the answer is grounded in / supported by the set of facts.\n 
    Give a binary score 'yes' or 'no'.
    """

