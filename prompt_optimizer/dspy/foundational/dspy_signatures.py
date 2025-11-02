import dspy
from dotenv import load_dotenv
from dspy.datasets import MATH
from typing import Literal


load_dotenv(override=True)

gpt4o_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
gpt4o = dspy.LM('openai/gpt-4o', max_tokens=2000)
dspy.configure(lm=gpt4o_mini)  # we'll use gpt-4o-mini as the default LM, unless otherwise specified

def predict():

    signature = dspy.Signature(
            "question -> fun_answer",
            instructions="give funny witty answer",
        )


    print(signature)

    fun_witty_answer = dspy.Predict(signature=signature)
    comment = "why sky is blue?"
    response = fun_witty_answer(question=comment).fun_answer

    print(response)


def tagging():
    document = """The 21-year-old made seven appearances for the Hammers and netted his only goal for them in a Europa League qualification round match 
        against Andorran side FC Lustrains last season. Lee had two loan spells in League One last term, with Blackpool and then Colchester United. 
        He scored twice for the U's but was unable to save them from relegation. The length of Lee's contract with the promoted Tykes has not been revealed. 
        Find all the latest football transfers on our dedicated page."""

    tag = dspy.ChainOfThought('document -> tag')
    print(tag)
    response = tag(document=document)

    print(response.tag)


class Emotion(dspy.Signature):
    """Classify emotion."""

    sentence: str = dspy.InputField()
    sentiment: Literal['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] = dspy.OutputField()
    llm_response: str = dspy.OutputField(desc="raw response from LLM")
    tokens: int = dspy.OutputField(desc="total tokens used")

sentence = "i started feeling a little vulnerable when the giant spotlight started blinding me"

classify = dspy.Predict(Emotion)
response = classify(sentence=sentence)

print(f"\n\n {response}")

