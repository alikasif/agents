from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

    
class Code(BaseModel):
    code: str 

def write_code(llm):
    
    prompt = PromptTemplate(
    
        template="Write best possible python code for {query}. Dont include any test run example. " \
        "Your response must contain only the code to solve the user query." ,   
        input_variables=["query"],

    )

    structured_llm = llm.with_structured_output(Code)

    generator = prompt|structured_llm
   
    return generator


class CodeReview(BaseModel):
    review_comments: str

def review_code(llm):

    reflection_prompt = PromptTemplate(
    input_variables=["initial_response", "query"],
    template=
            "You are a senior lead python code reviewer. You will review following code: {initial_response} for the query: {query}."
            "Provide detailed code reviw focused on improving the code quality, performance, modularity, testability, and readability."
            "Do not add review comments for adding unit test but do add review comments for testability of code."
            "Review comments must include only the improvements required."
            "if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments."
            "Respond with code review comments only. Dont include the improved code in your response."
    )
    structured_llm = llm.with_structured_output(CodeReview)

    reflector = reflection_prompt | structured_llm

    return reflector


class RefinedResponse(BaseModel):
    improved_code: str

def refinement(llm):
    refinement_prompt = PromptTemplate(
    input_variables=["initial_response", "reflection", "query"],
    template="Given the initial response to '{query}':\n\n{initial_response}\n\n"
             "And the following critique and recommendations:\n\n{reflection}\n\n"
             "Produce a refined and improved version of the python code. Respond with only the code."
    )

    structured_llm = llm.with_structured_output(RefinedResponse)

    refinement_chain = refinement_prompt | structured_llm

    return refinement_chain



def write_and_review(user_input: str):
    
    i=0
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"),)

    initial_response = write_code(llm).invoke(user_input)
   # print(f"Initial Response:\n{initial_response.code}\n")
    current_response = initial_response.code
    reflection=""
    while i < 5:
        print(f"\n\n--- Reflection Iteration {i+1} ---")
        reflection = review_code(llm).invoke({"initial_response":current_response, "query":user_input})
        reflection = reflection.review_comments
 #       print(f"Reflection:\n{reflection.review_comments}\n")

        if 'PAUSE' == reflection:
            break

        refined_response = refinement(llm).invoke(
            {"initial_response":current_response,
            "reflection":reflection,
            "query":user_input}
        )
#        print(f"Refined Response:\n{refined_response.improved_code}\n")
        current_response = refined_response.improved_code
        i+=1
    
    print("\n\n\n")
    print("Final Code Review Comments:")
    print("\n\n\n")
    print(reflection)
    print("\n\n\n")
    print("Final Code Written:")
    print("\n\n\n")
    print(current_response)
    

if __name__ == '__main__':
    print("\n\nThis module is designed for code writing and reviewing tasks.\n\n")
    load_dotenv(override=True)
    user_input = input("Enter your code writing request: ")
    write_and_review(user_input)
