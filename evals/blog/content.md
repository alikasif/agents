"Imagine a company hires a new employee. Their resume is excellent and they complete all of their tasks quickly and efficiently. Their work is technically getting done—but is it getting done well? Is it high quality, accurate and reliable?"
LLM model evaluation vs. LLM system evaluation

LLM evaluation (which can also be called LLM model evaluation) assesses how well a model performs. It looks at the core language model itself, focusing on its ability to understand and generate text across various tasks and domains. Model evaluation typically involves testing the model's raw capabilities. 


LLM system evaluation is more comprehensive and provides insights into the end-to-end performance of the LLM-powered application. System evaluation looks at the entire ecosystem that is built around an LLM
Online & Offline Evaluation
Offline

    Evaluating the application in a controlled setting
    Typically using curated test Datasets instead of live user queries
    Heavily used during development (can be part of CI/CD pipelines) to measure improvements / regressions
    Repeatable and you can get clear accuracy metrics since you have ground truth.


Online

    Evaluating the application in a live, real-world environment, i.e. during actual usage in production.
    Use Evaluation Methods that track success rates, user satisfaction scores, or other metrics on live traffic
    Advantage of online evaluation is that it captures things you might not anticipate in a lab setting
    Can include collecting implicit and explicit user feedback, and possibly running shadow tests or A/B tests


What is evals?

Evaluation, often shortened as ‘Evals’, is the systematic assessment and measurement of the performance of LLMs and their applications. Think of evaluations as a series of tests and metrics meticulously crafted to judge the “production-readiness” of your application.


Here are the most important and common metrics that you will likely need before launching your LLM system into production:

    Answer Relevancy: Determines whether an LLM output is able to address the given input in an informative and concise manner.
    Task Completion: Determines whether an LLM agent is able to complete the task it was set out to do.
    Correctness: Determines whether an LLM output is factually correct based on some ground truth.
    Hallucination: Determines whether an LLM output contains fake or made-up information.
    Tool Correctness: Determines whether an LLM agent is able to call the correct tools for a given task.
    Contextual Relevancy: Determines whether the retriever in a RAG-based LLM system is able to extract the most relevant information for your LLM as context.
    Responsible Metrics: Includes metrics such as bias and toxicity, which determines whether an LLM output contains (generally) harmful and offensive content.
    Task-Specific Metrics: Includes metrics such as summarization, which usually contains a custom criteria depending on the use-case.


If you decide to change your LLM system completely tomorrow for the same LLM use case, your custom metrics shouldn't change at all, and vice versa.


Characteristics of LLM metrics:

Quantitative. Metrics should always compute a score when evaluating the task at hand. 

Reliable. As unpredictable as LLM outputs can be, the last thing you want is for an LLM evaluation metric to be equally flaky

Accurate. Reliable scores are meaningless if they don’t truly represent the performance of your LLM application.


Types of metrics scorer:
LLM Model Evaluation Benchmarks


Statistical Scorers: Does not take any semantics into account and have extremely limited reasoning capabilities, they are not accurate enough for evaluating LLM outputs that are often long and complex. 

BLUE, ROUGE, METEOR, Lavenshtein distance


Model-Based Scorers: NL1, BLEURT


Best way is LLM As Judge:LLM-as-a-Judge Simply Explained: The Complete Guide to Run LLM Evals at Scale - Confident AI

Coherence, Consistency, Fluency, Relevance, AVG


Model based scorer Implementation:

    G-Eval: uses LLMs to evaluate LLM outputs (aka. LLM-Evals), and is one the best ways to create task-specific metrics. G-Eval is great in the case of evaluation where subjectivity is involved.
    DAG(Deep Acyclic Graph): is a decision tree powered by LLM-as-a-judge, where each node is an LLM judgement and each edge is a decision. Used where it is extremely clear what you want the score to be for a certain combination of constraints, the DAG scorer is perfect
    Prometheus: Prometheus is a fully open-source LLM that is comparable to GPT-4’s evaluation capabilities when the appropriate reference materials (reference answer, score rubric) are provided. It is also use case agnostic, similar to G-Eval.


Model + Statistical Scorer

    QAG scorer It uses confined answers (usually either a ‘yes’ or ‘no’) to close-ended questions (which can be generated or preset) to compute a final metric score. It is reliable because it does NOT use LLMs to directly generate scores.
    GPTScore: GPTScore uses the conditional probability of generating the target text as an evaluation metric.
    SelfCheckGPT It is a simple sampling-based approach that is used to fact-check LLM outputs. It assumes that hallucinated outputs are not reproducible, whereas if an LLM has knowledge of a given concept, sampled responses are likely to be similar and contain consistent facts. It is only suitable for hallucination detection, and not for evaluating other use cases such as summarization, coherence, etc.


Why it is required?

Evals are crucial instruments that offer deep insights into how your app interacts with user inputs and real-world data. Robust evaluation of your application means ensuring that it not only adheres to technical specifications but also resonates with user expectations and proves its worth in practical scenarios.


What makes a good Evals?

    Covers the most important outcomes of your LLM-application
    A small number of metrics, which are interpretable, preferably
    Fast and automatic to compute
    Tested on a diverse & representative dataset
    Highly correlated with human judgment


Eval Metrics:

Precision and recall to BLEU and ROUGE scores, 

    Accuracy
    Recall
    F1 score
    Coherence
    Perplexity
    BLEU
    ROUGE
    Latency
    Toxicity



How to do evals?

 Manual Vibe checks: by asking: “Do these responses feel right?”While not systematic, vibe checks

help you see if things are working, spot issues, and come up with new prompt ideas. However, this

approach isn’t reliable or repeatable. As you move forward, you’ll need more structure — with

consistent grading and detailed records of results.

A more rigorous way to leverage human expertise is a labeling or annotation process: you can create

a formal workflow where reviewers evaluate responses using set instructions.

These manual LLM evaluations are the most reliable way to determine if your LLM app does its job well. As the product builder, you are best equipped to define what “success” means for your use case. In highly nuanced and specialized fields like healthcare, you may need to bring in subject matter experts to help judge this.


Evaluation methods

    LLM-as-a-judge is a technique to evaluate the quality of LLM applications by using an LLM as a judge. The LLM is given a trace or a dataset entry and asked to score and reason about the output. The resulting scores include chain-of-thought reasoning as a comment.
    Human Annotation is a manual evaluation method. It is used to collaboratively annotate traces, sessions and observations with scores.
    Custom Scores are the most flexible way to implement evaluation workflows using Langfuse. As any other evaluation method the purpose of custom scores is to assign evaluations metrics to Traces, Observations, Sessions, or DatasetRuns via the Score object (see Scores Data Model).

Automated LLM Evals

    With ground truth: compare the LLM’s outputs to target reference answers. 
    Without ground truth: directly assign quantitative scores or labels to the responses


How to match the LLM responses with expected response?
With ground truth

The tricky part is comparing responses to the ground truth. How do you decide if the new response is correct?


    Exact Match: Check if the response exactly matches the expected output (True/False). Confirm a certain text is correctly classified as “spam”.
    Word or Item Match: Check if the response includes specific words or items, regardless of full phrasing (True/False). Verify that “Paris” appears in answers about France’s capital.
    JSON match: Match key-value pairs in structured JSON outputs, ignoring order (True/False). Verify that all ingredients extracted from a recipe match a known list.
    Semantic Similarity: Measure similarity using embeddings to compare meanings. (E.g., cosine similarity). Match “reject” and “decline” as similar responses.
    N-gram: overlap Measure overlap between generated and reference text (E.g. BLEU, ROUGE, METEOR scores). Compare word sequence overlap between two sets of translations or summaries.
    LLM-as-a-judge: Prompt an LLM to evaluate correctness (Returns label or score). Check that the response maintains a certain style and level of detail. LLM-as-a-Judge Simply Explained: The Complete Guide to Run LLM Evals at Scale - Confident AI


Without ground truth

Reference-free evaluations: directly score the responses by chosen criteria.

For complex, open-ended tasks or multi-turn chats, it’s hard to define a single “right” response. And in production, there are no perfect references: you’re evaluating outputs as they come in. 

Instead of comparing outputs to a fixed answer, you can run Reference-free LLM evaluations. They assess specific qualities of the output, like structure, tone, or meaning


    LLM-as-a-Judge: Use an LLM with an evaluation prompt to assess custom properties. Check if the response fully answers the question fully and does not contradict retrieved context.
    ML models: Use specialized ML models to score input/output texts. Verify that text is non-toxic and has a neutral or positive sentiment.
    Semantic similarity: Measure text similarity using embeddings. Track how similar the response is to the question as a proxy for relevance.
    Regular expressions: Check for specific words, phrases, or patterns.Monitor for mentions of competitor names or banned terms.
    Format match: Validate structured formats like JSON, SQL, and XML.Confirm the output is valid JSON and includes all required keys.
    Text statistics: Measure properties like word count or symbols. Ensure all generated summaries are single sentences.


Tools for Evals

    GPTScore: A novel evaluation framework that leverages the zero-shot capabilities of generative pre-trained models for scoring text. Highlights the framework’s flexibility in evaluating various text generation tasks without the need for extensive training or manual annotation.
    LLM-Eval: A method that evaluates multiple dimensions of conversation quality using a single LLM prompt. Offers a versatile and robust solution, showing a high correlation with human judgments across diverse datasets.
    LLM-as-a-judge: Explores using LLMs as a surrogate for human evaluation, tapping into the model’s alignment with human preferences. Demonstrates that LLM judges like GPT-4 can achieve an agreement rate exceeding 80% with human evaluations, suggesting a scalable and effective method for approximating human judgments.
    DeepEval: confident-ai/deepeval: The LLM Evaluation Framework


LLM benchmarks

consist of sample datasets, tasks and prompt templates to test LLMs on specific skills, such as question-answering, machine translation, summarization and sentiment analysis. They also include metrics for evaluating performance and a scoring mechanism. Their assessment criteria can be based in ground truth or human preferences

    MMLU (Massive Multitask Language Understanding) dataset, which consists of a collection of multiple-choice questions spanning various domains.
    HumanEval, which assesses an LLM’s performance in terms of code generation, especially functional correctness.
    TruthfulQA, which addresses hallucination problems by measuring an LLM’s ability to generate truthful answers to questions.
    General Language Understanding Evaluation (GLUE), and SuperGLUE, which tests performance of natural language processing (NLP) models, especially those designed for language-understanding tasks.
    The Hugging Face datasets library, which provides open source access to numerous evaluation datasets.

The selected benchmarks are introduced to the LLM through zero-shot, few-shot and fine-tuning tests to see how well the model operates. With few-shot tests, the LLM is evaluated on its ability to perform with limited data after it receives a small number of labeled examples that demonstrate how to fulfill the task. Zero-shot tests ask the LLM to complete a task without any examples, testing how it adapts to new circumstances


LLM as a judge vs. humans in the loop (HITL)

When evaluating model outputs, developers and researchers use two approaches: LLM-as-a-judge and human-in-the-loop evaluation.


Limitations of LLM assisted Evals

    Application-Specific: One major constraint is that LLM-driven evaluators produce application-specific metrics. A numeric score given by an LLM in one context does not necessarily equate to the same value in another, hindering the standardization of metrics across diverse projects.
    Position Bias: According to a study, LLM evaluators often show a position bias, favoring the first result when comparing two outcomes. This can skew evaluations in favor of responses that appear earlier, regardless of their actual quality.
    Verbose Bias: LLMs also tend to prefer longer responses. This verbosity bias means that more extended, potentially less clear answers may be favored over concise and direct ones.
    Self-Affinity Bias: LLMs may exhibit a preference for answers generated by other LLMs over human-authored text, potentially leading to a skewed evaluation favoring machine-generated content.
    Stochastic Nature: The inherent fuzziness within LLMs means they might assign different scores to the same output when invoked separately, adding an element of unpredictability to the evaluation.


To mitigate these biases and improve the reliability of LLM evaluations, several strategies can be employed:

    Position Swapping: To counteract position bias, swapping the reference and the result in evaluations ensures the outcome being assessed is in the first position.
    Few-shot Prompting: Introducing a few examples or prompts into the evaluation task can calibrate the evaluator and reduce biases like verbosity bias.
    Hybrid Evaluation: To achieve a more grounded evaluation, integrating LLM-based assessments with human judgment or advanced non-traditional metrics can be highly effective. This combined approach offers a comprehensive assessment framework that balances the innovative capabilities of LLMs with the proven accuracy of non-traditional metrics.


Approach of Evals

Simple LLM wrapper application:

RAG:

Agents:


What sites are present for evals?


What should be the result of evals?

The choice of which LLM evaluation metric to use depends on the use case and architecture of your LLM application. Our experience tells us that you don't want more than 5 LLM evaluation metrics in your evaluation pipeline. As you'll see later, most metrics look extremely attractive - I mean, who doesn't want to prevent biases for their internal RAG QA app? But the truth is, when you're evaluating everything, you're evaluating nothing at all.

Too much data != good. You'll want:

    1-2 custom metrics (G-Eval or DAG) that are use case specific
    2-3 generic metrics (RAG, agentic, or conversational) that are system specific

For example, if you’re building a RAG-based customer support chatbot on top of OpenAI’s models with tool calling capabilities, you’ll want 3 RAG metrics (eg., faithfulness, answer relevancy, contextual relevancy) and 1 agentic metric (e.g. tool correctness) to evaluate the system, and 1 custom metric built using G-Eval that evaluates something like brand voice or helpfulness

Another useful tip of deciding whether to use G-Eval or DAG is, if the criteria is purely subjective, use G-Eval. Otherwise use DAG. I say "purely", because you can also use G-Eval as one of the nodes in DAG.


RAG Metrics

Faithfulness: Evaluates whether the LLM/generator in your RAG pipeline is generating LLM outputs that factually aligns with the information presented in the retrieval context. QAG scorer is best for RAG


Answer Relevancy: assesses whether your RAG generator outputs concise answers, and can be calculated by determining the proportion of sentences in an LLM output that a relevant to the input


Contextual Precision is a RAG metric that assesses the quality of your RAG pipeline’s retriever. When we’re talking about contextual metrics, we’re mainly concerned about the relevancy of the retrieval context.


Contextual Precision is an additional metric for evaluating a Retriever-Augmented Generator (RAG). It is calculated by determining the proportion of sentences in the expected output or ground truth that can be attributed to nodes in the retrieval context. A higher score represents a greater alignment between the retrieved information and the expected output, indicating that the retriever is effectively sourcing relevant and accurate content to aid the generator in producing contextually appropriate responses.


Contextual relevancy is simply the proportion of sentences in the retrieval context that are relevant to a given input.


Agentic Metrics - *** FIND OUT MORE****

Tool correctness is an agentic metric that assesses the quality of your agentic systems, and is the most unusual metric here because it is based on exact matching and not any LLM-as-a-judge. It is computed by comparing the tools called for a given input to the expected tools that should be called


Task completion is an agentic metric that uses LLM-as-a-judge to evaluate whether your LLM agent is able to accomplish its given task. given task is inferred from the input it was provided with to kickstart the agentic workflow, while the entire execution process is used to determine the degree of completion of such task



Fine-Tuning Metrics

Hallucination Some of you might recognize this being the same as the faithfulness metric. Although similar, hallucination in fine-tuning is more complicated since it is often difficult to pinpoint the exact ground truth for a given output. 


Toxicity metric evaluates the extent to which a text contains offensive, harmful, or inappropriate language. Off-the-shelf pre-trained models like Detoxify, which utilize the BERT scorer, can be employed to score toxicity


Bias metric evaluates aspects such as political, gender, and social biases in textual content. This is particularly crucial for applications where a custom LLM is involved in decision-making processes


Use Case Specific Metrics

custom helpfulness metric assesses whether your LLM app is able to be of use to users interacting with it.

prompt alignment metric assesses whether your LLM is able to generate text according to the instructions laid out in your prompt template

Summarization Is factually aligned with the original text. Includes important information from the original text. Using QAG, we can calculate both factual alignment and inclusion scores to compute a final summarization score


How to Evaluate Large Language Models

evaluation in the training phase and production.


Top 10 LLM Models Evaluation Frameworks
LLM Applications Evals

    Giskard is an open-source Python library that automatically detects performance, bias & security issues in AI applications. The library covers LLM-based applications such as RAG agents, all the way to traditional ML models for tabular data.

Models Evals

    DeepEval
    MLFlow LLM Evaluate
    RAGAs - Evaluation framework for your Retrieval Augmented Generation (RAG) pipelines
    Deepchecks
    Arize AI Phoenix
    LLMBench
    ChainForge
    GuardRails AI
    OpenPipe
    PromptFlow


Important links

https://lnkd.in/p/g7yu7aeA

Evaluating Large Language Model (LLM) systems: Metrics, challenges, and best practices | by Jane Huang | Data Science at Microsoft | Medium




