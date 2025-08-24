from langchain_core.prompts import PromptTemplate

blog_prompt = """
        Create a detailed, original blog post for Agentic AI Design patterns ranging from 1,500 to 2,000 words that introduces the Agentic AI design pattern to readers with an intermediate understanding of AI concepts. 
        Explain why it is important to understand these patterns to build the domain specific expert agents.        
        Specifically about patterns like Reflection, Tool(ReACT & ReWoo) and Planning which are used to build deep reasearch agents, and solve complex problems using step by step plan like Humans.
        
        The target audience should be AI practitioners familiar with machine learning, neural networks, and AI system architectures but new to Agentic AI specifically. At the beginning of the post, 
        clearly highlight the practical impact and significance of the Agentic AI design pattern to engage readers.

        The blog should maintain a professional yet engaging and accessible tone, balancing technical depth with clarity to keep readers interested. 
        Include a glossary or a definitions section for specialized terms related to the pattern to aid comprehension.

        1. Keep It Concise and Readable: Aim for 500+ words but under 10 minutes reading time. Use short paragraphs (3-4 sentences max), 
        simple language, and bullet points/lists for skimmability. Break up text with visuals, GIFs, or memes.
        2. Use Storytelling and Personal Touches: Write like you're talking to a friend—share personal experiences, stories, or relatable examples. 
        Start with a strong hook (e.g., a question or bold statement) to grab attention immediately.
        3. Provide Actionable Value: Make content helpful, unique, and research-backed. Address reader pain points, offer solutions, 
        and end with key takeaways or a call-to-action (e.g., "What’s your biggest challenge? Comment below!"). This boosts engagement metrics like read ratio, 
        which Medium uses for distribution.
        4. Proofread Thoroughly: Eliminate errors for professionalism. High-quality, error-free content improves user experience, reduces bounce rates, 
        and signals value to Google

        Each pattern must have following sections

        1. what it is? Explain with some real life anecdote
        2. How it is implemented?
        3. Flow diagram
        4. What kind of problems can be solved through this pattern?

        Throughout the blog, clarify technical concepts without sacrificing depth, maintaining reader engagement by weaving in examples, 
        clear explanations, and practical relevance.
        """
    
linkedin_prompt= """
        Write a 2500 characters linkedin post about AI Design patterns. Write 1 line about patterns like Reflection, Tool use, Planning, ReACT & ReWOO (Reasoning With Open Ontology) and Multi Agent
        Highlight in few words why it is important to understand what happens under the hood of Agent SDK from various providers like OpenAI, Crew, Google ADK, Autogen
        to build domain specific expert agent.
        Use simple easy to understand words which creates interest for users to read the post and know more about these patterns.
        """

reflection_pattern = """
        write 300 words technical content about Multi Agent pattern in AI agents.
        1. Keep It Concise and Readable: Aim for 300 words but under 5 minutes reading time. Use short paragraphs (3-4 sentences max), 
        simple language, and bullet points/lists for skimmability. Break up text with visuals, GIFs, or memes.
        2. Use Storytelling and Personal Touches: Write like you're talking to a friend—share personal experiences, stories, or relatable examples. 
        Start with a strong hook (e.g., a question or bold statement) to grab attention immediately.
        3. Provide Actionable Value: Make content helpful, unique, and research-backed. Address reader pain points, offer solutions, 
        and end with key takeaways or a call-to-action (e.g., "What’s your biggest challenge? Comment below!"). This boosts engagement metrics like read ratio, 
        which Medium uses for distribution.
        4. Proofread Thoroughly: Eliminate errors for professionalism. High-quality, error-free content improves user experience, reduces bounce rates, 
        and signals value to Google
"""