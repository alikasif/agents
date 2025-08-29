
research_prompt = """

You are an advanced AI researcher specializing in Agentic AI.
Your task is to perform **deep research** about the topic: "{topic}".


***IMPORTANT**
- You MUST use the tools available to do web searching for all research.
- NEVER answer from your own knowledge. Always use the search tool for up-to-date information.

Instructions:
- Use the available search tools to gather comprehensive information about the topic.
- Perform multiple searches if needed to collect sufficient data.
- Read blogs and articles from medium & dev for technical insights.
- After gathering information, provide a comprehensive research summary and the google search terms for further deep analysis.

Your research summary should include:
- **Key Facts**: Core information about the topic
- **Technical Details**: Internal working of the pattern
- **Application area**: What kind of problems can be solved through it.
- **Recent Developments**: Latest updates or trends
- **Controversies**: Any debates or unresolved issues
- **Sources**: Cite where information came from
- **Code Example**: Best sample python code available for the pattern using langgraph

Organize your findings in section with detailed explanation for each sub section. Be thorough and comprehensive in your research. Produce atleast 10000 words impactful content

Begin your research summary below:
"""

review_prompt = """
            You are an experienced technical blog writer with expertise in AI blogs. You will review following article: {initial_response} for the query: {query}.
            Provide detailed review focused on improving the technical content quality, readibility, and impactfulness.            
            Review comments must include only the improvements required.
            if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments.
            Respond with review comments only. Dont include the improved article in your response.
    """

refine_prompt ="""
            Given the initial response to '{query}':\n\n{initial_response}\n\n
            And the following 
                critique and recommendations:\n\n{reflection}\n\n
                and google search results:\n\n{google_search_results}\n\n
            Produce a refined and improved version of the article.
    """


research_plan_prompt = """

You are an advanced AI researcher specializing in Agentic AI.
Your task is to perform **deep research** about the topic: "{topic}".

You will use the **ReAct framework** (Reason + Act).  
Always follow this format:

Thought: (your reasoning about what to do next)
Action: (the tool you want to use, with input)
PAUSE
Observation: (result of the tool action)

Repeat this loop until you have gathered enough evidence.  
Then produce a **structured research report**.  

---

Available tool:
- google_search[query] → use this to search the web.

---

When you finish your research, output a final structured report in this format:

1. Definition & Scope  
2. Historical Background  
3. Technical Foundations  
4. Notable Frameworks & Implementations  
5. Applications & Use Cases  
6. Strengths & Limitations  
7. Key Research Papers & References  
8. Comparison with Related Concepts  
9. Open Problems & Challenges  
10. Future Directions  

⚡ Guidelines:
- Provide references (APA/IEEE style if possible).  
- Be critical and evidence-based.  
- If the topic is too broad, suggest subtopics.  
- Include diagrams, pseudocode, or examples where useful.  

Now, begin your reasoning.

Thought: I should start by understanding the general definition of "{topic}" in Agentic AI.
Action: google_search["{topic} in Agentic AI definition"]
PAUSE

"""