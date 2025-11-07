import dspy
from dotenv import load_dotenv
from dspy.datasets import MATH


load_dotenv(override=True)
gpt4o_mini = dspy.LM('openai/gpt-4o-mini', max_tokens=2000)
gpt4o = dspy.LM('openai/gpt-4o', max_tokens=2000)
dspy.configure(lm=gpt4o_mini)  # we'll use gpt-4o-mini as the default LM, unless otherwise specified

dataset = MATH(subset='algebra')
dataset.train = dataset.train[:20]
dataset.dev = dataset.dev[:10]

print(len(dataset.train), len(dataset.dev))

example = dataset.train[0]
print("Question:", example.question)
print("Answer:", example.answer)

module = dspy.ChainOfThought("question -> answer")
module(question=example.question)

THREADS = 4
kwargs = dict(num_threads=THREADS, display_progress=True, display_table=5)
evaluate = dspy.Evaluate(devset=dataset.dev, metric=dataset.metric, **kwargs)

evaluate(module)

kwargs = dict(num_threads=THREADS, teacher_settings=dict(lm=gpt4o), prompt_model=gpt4o_mini)
optimizer = dspy.MIPROv2(metric=dataset.metric, auto="light", **kwargs)

kwargs = dict(max_bootstrapped_demos=4, max_labeled_demos=4)
optimized_module = optimizer.compile(module, trainset=dataset.train, **kwargs)

evaluate(optimized_module)

dspy.inspect_history()
