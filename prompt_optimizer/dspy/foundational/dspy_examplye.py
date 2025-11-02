import dspy
from dspy.datasets import HotPotQA
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper

load_dotenv(override=True)

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

def optimize():
    def search_wikipedia(query: str) -> list[str]:
        results = dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")(query, k=3)
        return [x["text"] for x in results]

    trainset = [x.with_inputs('question') for x in HotPotQA(train_seed=2024, train_size=50).train]

    print(f"train set size; {len(trainset)} \n {trainset[0]} \n\n")

    react = dspy.ReAct("question -> answer", tools=[search_wikipedia])

    tp = dspy.MIPROv2(metric=dspy.evaluate.answer_exact_match, auto="light", num_threads=24)

    optimized_react = tp.compile(react, trainset=trainset)

    print(f" \n\n optimizez react prompt:: {optimized_react}")


def react_prompting():

    def evaluate_math(expression: str):
        return dspy.PythonInterpreter({}).execute(expression)

    def search_wikipedia(query: str):
        results = dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")(query, k=3)
        return [x["text"] for x in results]
    
    def google_search(query: str):
        print(f"\nsearcing google with query {query}")
        search = GoogleSerperAPIWrapper()
        return search.run(query)

    react = dspy.ReAct("question -> answer: str", tools=[evaluate_math, search_wikipedia, google_search])

    print(f"react:: {react}\n")

    pred = react(question="Who won the 2016 Russian national silver medal with another Russian ice dancer born 29 April 1995?")
    print(pred.answer)


if __name__ == "__main__":
    react_prompting()