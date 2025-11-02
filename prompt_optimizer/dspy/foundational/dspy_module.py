import dspy
from dotenv import load_dotenv
from dspy.datasets import MATH
from typing import Literal
from langchain_community.utilities import GoogleSerperAPIWrapper


load_dotenv(override=True)

gpt4o_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
dspy.configure(lm=gpt4o_mini)  # we'll use gpt-4o-mini as the default LM, unless otherwise specified
dspy.settings.configure(track_usage=True)


def google_search(query: str):
    print(f"\nsearcing google with query {query}")
    search = GoogleSerperAPIWrapper()
    return search.run(query)


def predict_module():
    signature = dspy.Signature("input -> joke")
    sentence = "Life is a journey to learn and have fun"

    # 1) Use built in module with a signature.
    classify = dspy.Predict(signature=signature)

    # 2) Call with input argument(s). 
    response = classify(input=sentence)

    # 3) Access the output.
    print(response.joke)


def cot_module():
    question = "Who won the 2016 Russian national silver medal with another Russian ice dancer born 29 April 1995?"

    # 1) Declare with a signature, and pass some config.
    cot = dspy.ChainOfThought(signature='question -> answer', n=5)

    # 2) Call with input argument.
    response = cot(context = google_search(question), question=question)

    # 3) Access the outputs.
    print(f"\n COT {response.answer}")
    print(f"\nCOT Reasoning: {response.reasoning}")


def react_module():
    question = "Who won the 2016 Russian national silver medal with another Russian ice dancer born 29 April 1995?"

    # 1) Declare with a signature, and pass some config.
    cot = dspy.ReAct(signature='question -> answer', tools=[google_search])

    # 2) Call with input argument.
    response = cot(question=question)

    # 3) Access the outputs.
    print(f"\n React {response.answer}")
    print(f"\nReact Reasoning: {response.reasoning}")

def program_of_thoughts():
    question = "check if a number is part of finbanocci series"

    # 1) Declare with a signature, and pass some config.
    pot = dspy.ProgramOfThought(signature='question -> code')

    # 2) Call with input argument.
    response = pot(question=question)

    # 3) Access the outputs.
    print(f"\n POT {response.code}")
    usage = pot.get_lm_usage()


def rag():

    def search(query: str) -> list[str]:
        """Retrieves abstracts from Wikipedia."""
        results = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')(query, k=3)
        results =  [x['text'] for x in results]
        print(f"wiki results {results}")

    rag = dspy.ChainOfThought('context, question -> response')

    question = "What's the name of the castle that David Gregory inherited?"
    response = rag(context=google_search(question), question=question)
    print(f"\n rag:: {response.response}")



class Hop(dspy.Module):

    def __init__(self, num_docs=10, num_hops=4):
        self.num_docs, self.num_hops = num_docs, num_hops
        self.generate_query = dspy.ChainOfThought('claim, notes -> query')
        self.append_notes = dspy.ChainOfThought('claim, notes, context -> new_notes: list[str], titles: list[str]')

    def forward(self, claim: str) -> list[str]:
        notes = []
        titles = []

        for _ in range(self.num_hops):
            query = self.generate_query(claim=claim, notes=notes).query
            context = google_search(query)
            prediction = self.append_notes(claim=claim, notes=notes, context=context)
            notes.extend(prediction.new_notes)
            titles.extend(prediction.titles)

        return dspy.Prediction(notes=notes, titles=list(set(titles)))



if __name__ == "__main__":
    #cot_module()
    #react_module()
    #program_of_thoughts()
    #rag()
    
    hop = Hop()
    print(hop(claim="Stephen Curry is the best 3 pointer shooter ever in the human history"))