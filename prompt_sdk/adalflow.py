from dotenv import load_dotenv
import adalflow as adal
import re
from typing import Dict, Union
from adalflow.optim.parameter import ParameterType
from adalflow.components.model_client.openai_client import OpenAIClient

load_dotenv(override=True)


few_shot_template = r"""<START_OF_SYSTEM_PROMPT>
{{system_prompt}}
{# Few shot demos #}
{% if few_shot_demos is not none %}
Here are some examples:
{{few_shot_demos}}
{% endif %}
<END_OF_SYSTEM_PROMPT>
<START_OF_USER>
{{input_str}}
<END_OF_USER>
"""


@adal.func_to_data_component
def parse_integer_answer(answer: str):
    """A function that parses the last integer from a string using regular expressions."""
    try:
        # Use regular expression to find all sequences of digits
        numbers = re.findall(r"\d+", answer)
        if numbers:
            # Get the last number found
            answer = int(numbers[-1])
        else:
            answer = -1
    except ValueError:
        answer = -1

    return answer


class ObjectCountTaskPipeline(adal.Component):

    def __init__(self, model_client: adal.ModelClient, model_kwargs: Dict):
        super().__init__()

        system_prompt = adal.Parameter(
            data="You will answer a reasoning question. Think step by step. " \
            "The last line of your response should be of the following format: 'Answer: $VALUE' where VALUE is a numerical value.",
            role_desc="To give task instruction to the language model in the system prompt",
            requires_opt=True,
            param_type=ParameterType.PROMPT,
        )
        
        few_shot_demos = adal.Parameter(
            data=None,
            role_desc="To provide few shot demos to the language model",
            requires_opt=True,
            param_type=ParameterType.DEMOS,
        )

        self.llm_counter = adal.Generator(
            model_client=model_client,
            model_kwargs=model_kwargs,
            template=few_shot_template,
            prompt_kwargs={
                "system_prompt": system_prompt,
                "few_shot_demos": few_shot_demos,
            },
            output_processors=parse_integer_answer,
            use_cache=True,
        )

    def bicall(self, question: str, id: str = None) -> Union[adal.GeneratorOutput, adal.Parameter]:
        output = self.llm_counter(prompt_kwargs={"input_str": question}, id=id)
        return output
    

adal.setup_env()

gpt_3_model = {
    "model_client": OpenAIClient(),
    "model_kwargs": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 2000,
        "temperature": 0.0,
        "top_p": 0.99,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    },
}

question = "I have a flute, a piano, a trombone, four stoves, a violin, an accordion, a clarinet, a drum, two lamps, and a trumpet. How many musical instruments do I have?"
task_pipeline = ObjectCountTaskPipeline(**gpt_3_model)
print(task_pipeline)

answer = task_pipeline.bicall(question)
print(answer)

# # set it to train mode
# task_pipeline.train()
# answer = task_pipeline.bicall(question, id="1")
# print(answer)
# print(f"full_response: {answer.full_response}")