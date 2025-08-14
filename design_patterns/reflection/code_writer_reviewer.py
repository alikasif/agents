from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate


def write_code(llm):
   
    prompt = PromptTemplate(
    
        input_variables=["query"],
        #  this needs to be a tuple so do not forget the , at the end and do not include any , in-between
        template="Write best possible code for {query}",
    )

    generator = LLMChain(llm=llm, prompt=prompt)
   
    return generator


def review_code(llm):

    reflection_prompt = PromptTemplate(
    input_variables=["initial_response", "query"],
    template=
            "You are a senior lead python code reviewer. You will review following code {initial_response} for the query {query}."
            "Provide detailed code reviw focused on improving the code quality, performance, modularity, testability, and readability"
            "to an asistant code writer to help improve this code."
            "if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments."
            "Respond with code review comments only. Dont include the improved code in your response."
    )

    reflector = LLMChain(llm=llm, prompt=reflection_prompt)

    return reflector

def refinement(llm):
    refinement_prompt = PromptTemplate(
    input_variables=["initial_response", "reflection", "query"],
    template="Given the initial response to '{query}':\n\n{initial_response}\n\n"
             "And the following critique and recommendations:\n\n{reflection}\n\n"
             "Produce a refined and improved version of the response."
    )

    refinement_chain = LLMChain(llm=llm, prompt=refinement_prompt)

    return refinement_chain



def write_and_review(user_input: str):
    
    i=0
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    initial_response = write_code(llm).invoke(user_input)
    current_response = initial_response
    reflection=""
    while i < 3:
        print(f"\n\n--- Reflection Iteration {i+1} ---")
        reflection = review_code(llm).invoke({"initial_response":current_response, "query":user_input})
        print(f"Reflection:\n{reflection}\n")

        if 'PAUSE' == reflection:
            break

        refined_response = refinement(llm).invoke(
            {"initial_response":current_response,
            "reflection":reflection,
            "query":user_input}
        )
        print(f"Refined Response:\n{refined_response}\n")
        current_response = refined_response
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
