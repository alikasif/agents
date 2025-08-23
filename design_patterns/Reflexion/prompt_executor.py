from design_patterns.Reflexion.reflection_agent import *
from langchain_core.prompts import PromptTemplate
from prompt import *


class PromptExecutor:

    def __init__(self):
        self.executor_llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=os.getenv("OPENAI_MODEL"),)        
       

    def get_prompt(self, query):
        agent = ReflectionAgent()
        prompt = agent.reflexion_loop(query)
        return prompt


    def execute(self, query):

        prompt_agent = ReflectionAgent()
        prompt = prompt_agent.reflexion_loop(query)

        blog_prompt = PromptTemplate(
                input_variables=[],
                template=prompt)
        
        executor = blog_prompt | self.executor_llm

        initial_response = executor.invoke({})

        print(f"\n\n\n Response : {initial_response.content}\n")
            

if __name__ == '__main__':
    load_dotenv(override=True)
    user_input = input("Enter your request: ")
    executor = PromptExecutor()
    executor.execute(user_input)
