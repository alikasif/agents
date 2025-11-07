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

question = {"question": "What is the capital of France?"}
demos = [{"question": "What is 1+1?", "answer": "2"}]

adapter = dspy.ChatAdapter()
signature = dspy.Signature("question -> answer")
predict = dspy.Predict(signature)
print(adapter.format(signature=signature, inputs=question, demos=demos ))
result = predict(question=question)
