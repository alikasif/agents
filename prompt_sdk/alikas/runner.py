from factory import PromptFactory

def main():
    # Example usage for each prompt type
    cot = PromptFactory.create("chain_of_thought")
    cot.set_task("Solve math problem").set_context("Algebra").add_example("Q: 2+2\nA: 4").set_format("text").set_tone("logical")
    cot.set_persona("You are a helpful math tutor.")
    cot.add_instruction("Show all steps.")
    print("ChainOfThoughtPrompt:\n", cot.build())

    tot = PromptFactory.create("tree_of_thought")
    tot.set_task("Plan a trip").set_context("Europe").add_example("Q: Best cities in France?\nA: Paris, Lyon").set_format("list").set_tone("friendly")
    tot.set_persona("You are a travel planner.")
    tot.add_evaluation_criteria("Cost").add_evaluation_criteria("Fun")
    print("\nTreeOfThoughtPrompt:\n", tot.build())

    react = PromptFactory.create("react")
    react.set_task("Find info").set_context("Web search").add_example("Q: Python creator?\nA: Guido van Rossum").set_format("text").set_tone("neutral")
    react.set_persona("You are a research assistant.")
    react.add_tool("search", "Searches the web").add_tool("calc", "Performs calculations")
    print("\nReActPrompt:\n", react.build())

    ms = PromptFactory.create("multi_shot", shots=2)
    ms.set_task("Answer questions").set_context("General knowledge").add_example("Q: Capital of Italy?\nA: Rome").add_example("Q: Largest ocean?\nA: Pacific")
    ms.set_format("Q&A").set_tone("informative").set_persona("You are a quiz master.")
    print("\nMultiShotPrompt:\n", ms.build())

if __name__ == "__main__":
    main()
