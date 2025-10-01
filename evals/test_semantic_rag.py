import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from dotenv import load_dotenv


def test_case():
    load_dotenv(override=True)
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5
    )
    test_case = LLMTestCase(
        input="what is llm based routing?",
        # Replace this with the actual output from your LLM application
        actual_output="LLM-based routing refers to a technique where a Large Language Model (LLM) is used directly to analyze an input (for example, a user query) \
            and determine what should happen next—such as which workflow, tool, or sub-agent to use. The LLM is given a prompt that asks it to interpret the input and \
                output a specific identifier or instruction that represents the next step. This process occurs at inference time, meaning the LLM itself is actively \
                    involved in making routing decisions as the system runs, rather than relying on predefined rules or a separately trained classification model.",
        expected_output="LLM based routing uses LLM model to analyze the input and output a specific identifier or instruction that indicates the next step or destination. \
            The agentic system then reads this output and directs the workflow accordingly",
        retrieval_context=["LLM based routing uses LLM model to decide the next step."]
    )

    assert_test(test_case, [correctness_metric])