
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
            Produce a refined and improved version of the article with detailed explanation of each point. 
            Dont just add bullet points. Expand each point into a paragraph with examples and code snippets if relevant.
    """


blog_plan_template="""
You are an expert AI researcher and technical writer.  
Your goal is to write a **technical blog post** of 10000 words about: "{topic}"  

We will use a **Plan → Execute → Reflect** process.

---

### Step 1: PLAN (ReWOO style)
- Define the audience knowledge level.  
- Decide the scope of the blog (overview, tutorial, deep-dive, key-facts, technical details, application area, recent developments, sources, controversies).  
- Create a detailed outline with sections & subsections.  

Output the plan as:
Plan_String: <one-line description of the plan>  
Steps: [Step 1: ..., Step 2: ..., Step N: ...]  
"""


blog_writer_prompt="""

You are an expert technical writer specializing in deep, insightful blog posts on Agentic AI—autonomous AI systems that plan, reason, execute tasks, and interact with environments or tools. Your goal is to create a comprehensive, engaging, and technically rigorous blog post based on the user's query or outline. Aim for 1500-3000 words, structured for readability, with code examples, diagrams (described in text), and real-world applications.

### Key Guidelines:
- **Depth Over Breadth**: Dive deep into concepts—explain fundamentals (e.g., agent architectures, planning algorithms), edge cases (e.g., failure modes in multi-agent systems), trade-offs (e.g., scalability vs. reliability), historical context (e.g., evolution from reactive to agentic AI), and future implications (e.g., ethical concerns in autonomous decision-making). Avoid superficial overviews; use analogies, math derivations (if relevant, like in reinforcement learning for agents), and peer-reviewed insights from papers like those on ReAct or LangChain.
- **Structure**:
  1. **Introduction**: Hook with a problem statement (e.g., "How can AI go beyond chatbots to autonomously solve complex tasks?"), real-world example (e.g., an agentic system in robotics), or provocative question. Outline the post's value and structure.
  2. **Core Concepts**: Break down key ideas step-by-step, such as agent components (perception, planning, action), frameworks (e.g., LangGraph, AutoGPT), and paradigms (e.g., hierarchical vs. flat agents). Use subsections, bullet points, and numbered lists for clarity.
  3. **Technical Deep Dive**: Include code snippets (in Markdown with syntax highlighting, e.g., Python with libraries like LangChain or CrewAI), algorithms (e.g., pseudocode for chain-of-thought reasoning), formulas (e.g., reward functions in RL-based agents), or architectures (e.g., diagrams of tool-calling loops). Explain why they work, optimizations (e.g., caching in agent memory), and common pitfalls (e.g., infinite loops in recursive agents).
  4. **Examples & Case Studies**: Provide 2-3 practical examples, with code, data, or simulations (e.g., building a web-scraping agent or a multi-agent debate system). Discuss results, benchmarks (e.g., using AgentBench), and lessons learned.
  5. **Comparisons & Trade-offs**: Contrast with alternatives (e.g., agentic AI vs. traditional ML pipelines via tables). Cover pros/cons, performance metrics (e.g., success rate, latency), and scalability (e.g., for enterprise vs. edge devices).
  6. **Advanced Topics**: Explore extensions (e.g., integrating with LLMs like GPT-4o), research frontiers (e.g., emergent behaviors in swarms), or integrations (e.g., with blockchain for secure agents).
  7. **Conclusion**: Summarize key takeaways, suggest next steps (e.g., resources like GitHub repos, experiments to try), and end with a call to action (e.g., "Build your first agent today!").
- **Tone & Style**: Professional yet accessible—conversational for engagement (e.g., "Imagine an AI that not only answers but acts..."), but precise and jargon-appropriate (e.g., "decomposition in task planning"). Use active voice, short paragraphs, and bold/italics for emphasis.
- **SEO & Readability**: Incorporate keywords naturally (e.g., "agentic AI frameworks," "autonomous AI agents"). Use headings (H1-H3), images (describe as ![alt text](url)), and links to sources (e.g., arXiv papers, docs).
- **Accuracy & Ethics**: Base on verified knowledge; cite sources (e.g., papers, docs) inline. Avoid hype; disclose assumptions (e.g., "Assuming access to API tools..."). Discuss ethical aspects like bias in agent decisions or safety in deployment.
- **Length & Polish**: Ensure logical flow; proofread for grammar, typos, and coherence.

User Query/Outline: [Insert the specific topic or outline here, e.g., "Building a multi-agent system for e-commerce automation with code examples."]

Generate the full blog post in Markdown format, ready for publishing.
"""

blog_execute_template = """    
   
   - Aim for 8000-10000 words blog.  
   - Keep technical rigor but also readability.  

For each step in the plan:  
    - Expand into a **detailed blog section** with explanations, examples, and references.  
    - Use engaging but precise writing style.  
    - Include bullet points, code snippets (if relevant), and comparisons.  

    
    here are the steps: {steps}
"""

blog_review_template = """

    You are an experienced technical blog writer with expertise in AI blogs. You will review following article: {initial_response} for the query: {query}.
    Provide detailed review focused on improving the technical content quality, readibility, and impactfulness.            
    Identify gaps, redundancies, or unclear explanations.  
    Suggest specific improvements.  
    Review the draft critically.  
    Rewrite or refine sections as needed until the blog flows well.  

"""

blog_refine_template ="""
            Given the initial response to '{query}':\n\n{initial_response}\n\n
            And the following 
                critique and recommendations:\n\n{reflection}\n\n
            Produce a refined and improved version of the blog.


             Review comments must include only the improvements required.
    if no more improvement are required then Respond with PAUSE and only PAUSE without any review comments.
    Respond with review comments only. Dont include the improved article in your response.
    """
