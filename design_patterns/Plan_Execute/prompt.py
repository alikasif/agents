from langchain_core.prompts import PromptTemplate

blog_prompt = """
        Create a detailed, original blog post for Agentic AI Design patterns ranging from 1,500 to 2,000 words that introduces the Agentic AI design pattern to readers with an intermediate understanding of AI concepts. 
        Explain why it is important to understand these patterns to build the domain specific expert agents.        
        Specifically about patterns like Reflection, Tool(ReACT & ReWoo) and Planning which are used to build deep reasearch agents, and solve complex problems using step by step plan like Humans.
        
        The target audience should be AI practitioners familiar with machine learning, neural networks, and AI system architectures but new to Agentic AI specifically. At the beginning of the post, 
        clearly highlight the practical impact and significance of the Agentic AI design pattern to engage readers.

        The blog should maintain a professional yet engaging and accessible tone, balancing technical depth with clarity to keep readers interested. 
        Include a glossary or a definitions section for specialized terms related to the pattern to aid comprehension.

        Each pattern must have following sections

        1. what it is? Explain with some real life anecdote
        2. How it is implemented?
        3. Flow diagram
        4. What kind of problems can be solved through this pattern?
        5. Research paper linked to the design pattern

        Ensure all claims and insights are supported by citations in APA format from current and diverse, reputable sources.

        Include pseudocode or code snippets where applicable to enhance practical understanding. 
        Specify any programming language or style for these snippets (e.g., Python-style pseudocode) to maintain consistency.

        Throughout the blog, clarify technical concepts without sacrificing depth, maintaining reader engagement by weaving in examples, clear explanations, and practical relevance.
        """
    
linkedin_prompt= """
        Write a 2500 characters linkedin post about AI Design patterns. Write 1 line about patterns like Reflection, Tool use, Planning, ReACT & ReWOO (Reasoning With Open Ontology) and Multi Agent
        Highlight in few words why it is important to understand what happens under the hood of Agent SDK from various providers like OpenAI, Crew, Google ADK, Autogen
        to build domain specific expert agent.
        Use simple easy to understand words which creates interest for users to read the post and know more about these patterns.
"""
