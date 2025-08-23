from langchain_core.prompts import PromptTemplate

code_intial_prompt = PromptTemplate(
    input_variables=["query"],
    template="Write best possible python code for {query}. Dont include any test run example. " \
        "Your response must contain only the code to solve the user query."
    )

code_reflection_prompt = PromptTemplate(
    input_variables=["initial_response", "query"],
    template=
            "You are a senior lead python code reviewer. You will review following code: {initial_response} for the query: {query}."
            "Provide detailed code review focused on improving the code quality, performance, modularity, testability, and readability."
            "Do not add review comments for adding unit test but do add review comments for testability of code."
            "Review comments must include only the improvements required."
            "if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments."
            "Respond with code review comments only. Dont include the improved code in your response."
    )


code_refinement_prompt = PromptTemplate(
    input_variables=["initial_response", "reflection", "query"],
    template="Given the initial response to '{query}':\n\n{initial_response}\n\n"
            "And the following critique and recommendations:\n\n{reflection}\n\n"
            "Produce a refined and improved version of the python code. Respond with only the code."
    )


intial_prompt_na = PromptTemplate(
    input_variables=["query"],
    template="""
            You are an expert prompt writer. You write prompt which is used to complete the task in a precise and effective way. Write best possible prompt to complete the task for : {query}.
            Your output must start with  'You are an expert practitioner who can complete the task '{query}' with these instruction.
            """
    )


reflection_prompt_na = PromptTemplate(
    input_variables=["initial_response", "query"],
    template="""
            You are an expert prompt reviewer. Your job is to review and critic the prompt to make it precise, impactful and effective. 
            Provide detailed prompt review focused on improving the quality, performance, impactfulness. You must understand the user request and provide feedback on the providec prompt.
            You will review following prompt: {initial_response} for the query: {query}.            
            Review comments must include only the improvements required.
            if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments.
            Respond with review comments only. Dont include the improved prompt in your response.
            """
    )


refinement_prompt_na = PromptTemplate(
    input_variables=["initial_response", "reflection", "query"],
    template="""
            Given the initial response:\n\n {initial_response}  to '{query}'\n\n
            And the following critique and recommendations:\n\n{reflection}\n\n
            Produce a refined and improved version of the prompt based on the review and critics. Respond with only the prompt without any thing related to refinement.
            """
    )

blog_prompt_na =  PromptTemplate(
    input_variables=["query"],
    template = 
        """
        Create a detailed, original blog post for {query} ranging from 1,500 to 2,000 words that introduces the Agentic AI design pattern to readers with an intermediate understanding of AI concepts. The target audience should be AI practitioners familiar with machine learning, neural networks, and AI system architectures but new to Agentic AI specifically. At the beginning of the post, clearly highlight the practical impact and significance of the Agentic AI design pattern to engage readers.

        The blog should maintain a professional yet engaging and accessible tone, balancing technical depth with clarity to keep readers interested. Include a glossary or a definitions section for specialized terms related to the pattern to aid comprehension.

        Structure the post into these well-linked sections to ensure seamless flow:

        1. **Introduction**:
        - Define Agentic AI precisely.
        - Outline its core principles.
        - Highlight the practical impact and significance of applying this pattern.

        2. **Architecture and Operation**:
        - Describe the operational mechanisms.
        - Detail key components and overall architecture.
        - Provide descriptive explanations of visual aids or workflow diagrams, ensuring these descriptions are accessible to readers with disabilities.

        3. **Practical Applications**:
        - Present real-world examples showcasing successful Agentic AI implementations, tailored to specific AI subfields or industries such as healthcare, finance, or autonomous systems.

        4. **Benefits and Challenges**:
        - Discuss advantages of deploying Agentic AI.
        - Explore technical difficulties.
        - Address ethical and societal considerations.
        - Highlight common misconceptions or pitfalls related to Agentic AI.

        5. **Current Trends and Future Outlook**:
        - Summarize recent (within the last 2-3 years), peer-reviewed research findings and emerging trends.
        - Discuss possible future developments.

        6. **Conclusion and Call to Action**:
        - Recap key points.
        - Encourage further engagement by suggesting specific, reputable resources, recent research papers, and industry reports.

        Ensure all claims and insights are supported by citations in APA format from current and diverse, reputable sources.

        Include pseudocode or code snippets where applicable to enhance practical understanding. Specify any programming language or style for these snippets (e.g., Python-style pseudocode) to maintain consistency.

        Throughout the blog, clarify technical concepts without sacrificing depth, maintaining reader engagement by weaving in examples, clear explanations, and practical relevance.
        """
    )