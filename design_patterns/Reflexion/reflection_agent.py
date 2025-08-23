from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from prompt import *

    
class Code(BaseModel):
    code: str 

class CodeReview(BaseModel):
    review_comments: str


class RefinedResponse(BaseModel):
    improved_code: str


class ReflectionAgent:

    def __init__(self):

        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"),)

        self.writer_llm = self.llm.with_structured_output(Code)
        self.generator = code_intial_prompt|self.writer_llm

        self.critic_llm = self.llm.with_structured_output(CodeReview)
        self.reflector = code_reflection_prompt | self.critic_llm

        self.refiner_llm = self.llm.with_structured_output(RefinedResponse)
        self.refiner = code_refinement_prompt | self.refiner_llm

    
    def generate(self, user_input):
               
        initial_response = self.generator.invoke(user_input)
        # print(f"Initial Response:\n{initial_response.code}\n")
        return initial_response.code        


    def critic(self, generated_response, user_input):

        reflection = self.reflector.invoke({"initial_response":generated_response, "query":user_input})
        return reflection.review_comments        


    def refine(self, user_input, current_response, critic):

            refined_response = self.refiner.invoke(
                {
                "query":user_input,
                "initial_response":current_response,
                "reflection":critic,
                }
            )
            return refined_response.improved_code


    def reflexion_loop(self, user_input: str):
        
        i=0

        current_response = self.generate(user_input)
        critic=""
        
        while i < 3:
            print(f"\n\n--- Reflection Iteration {i+1} ---")            
            critic = self.critic(current_response, user_input)
            # print(f"Reflection:\n{reflection.review_comments}\n")

            if 'PAUSE' == critic:
                break
           
            # print(f"Refined Response:\n{refined_response.improved_code}\n")
            current_response = self.refine(user_input, current_response, critic)
            i+=1
        
        print("\n\n\n============================================================================================")
        # print("Final Code Review Comments:")
        # print("\n\n\n")
        # print(critic)
        # print("\n\n\n")
        print("Final Code Written:")
        print("\n\n\n")
        print(current_response)
        print("===================================================================================================")
        return current_response
    

if __name__ == '__main__':
    load_dotenv(override=True)
    agent = ReflectionAgent()
    user_input = input("Enter your code writing request: ")
    agent.reflexion_loop(user_input)
