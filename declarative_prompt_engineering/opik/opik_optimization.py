"""
    Optimize a simple system prompt on the tiny_test dataset.
    Requires: pip install gepa, and a valid OPENAI_API_KEY for LiteLLM-backed models.
"""

from typing import Any, Dict
from opik.evaluation.metrics import LevenshteinRatio
from opik.evaluation.metrics.score_result import ScoreResult
from opik_optimizer import ChatPrompt, datasets
from opik_optimizer.gepa_optimizer import GepaOptimizer
from dotenv import load_dotenv
from opik_optimizer import EvolutionaryOptimizer
from opik_optimizer import MetaPromptOptimizer
from opik_optimizer import ParameterOptimizer
from opik_optimizer.parameter_optimizer import ParameterSearchSpace


load_dotenv(override=True)

def levenshtein_ratio(dataset_item: Dict[str, Any], llm_output: str) -> ScoreResult:
    return LevenshteinRatio().score(reference=dataset_item["label"], output=llm_output)

dataset = datasets.tiny_test()
#print((dataset.get_items()))

prompt = ChatPrompt(
    system="You are a helpful assistant. Answer concisely with the exact answer.",
    user="{text}",
)

def gepa():
    optimizer = GepaOptimizer(
        model="openai/gpt-4o-mini",
        model_parameters={
            #"reflection_model": "openai/gpt-4o",  # stronger reflector is often helpful
            "temperature": 0.2,
            "max_tokens":200
        },
        n_threads=2,
        
    )
    return optimizer

def evolutionary():
    optimizer = EvolutionaryOptimizer(
        model="openai/gpt-4o-mini",
        model_parameters={"temperature": 0.4},
        population_size=20,
        num_generations=10,
    )
    return optimizer

def meta_prompt():
    optimizer = MetaPromptOptimizer(
        model="openai/gpt-4",
        model_parameters={
            "temperature": 0.1,
            "max_tokens": 5000
        },
        n_threads=8,
        seed=42
    )
    return optimizer
    
def parameter_optimization():
    optimizer = ParameterOptimizer(
        model="openai/gpt-4",
        default_n_trials=20,    # Number of optimization trials
        n_threads=4,            # Parallel evaluation threads
        seed=42
    )

    parameter_space = ParameterSearchSpace(
        parameters=[
            {
                "name": "temperature",
                "distribution": "float",
                "low": 0.0,
                "high": 2.0
            },
            {
                "name": "top_p",
                "distribution": "float",
                "low": 0.1,
                "high": 1.0
            }
        ]
    )

    results = optimizer.optimize_parameter(
        prompt=prompt,
        dataset=dataset,
        metric=levenshtein_ratio,
        parameter_space=parameter_space,
        n_samples=100
    )   
    # Access results
    results.display()
    print(f"Best temperature: {results.details['optimized_parameters']['temperature']}")
    print(f"Best top_p: {results.details['optimized_parameters']['top_p']}")
    print(f"Parameter importance: {results.details['parameter_importance']}")


result = meta_prompt().optimize_prompt(
    prompt=prompt,
    dataset=dataset,
    metric=levenshtein_ratio,
    max_trials=12,
    reflection_minibatch_size=2,
    n_samples=5,
)

result.display()

parameter_optimization()
