# Design Patterns in AI & Agentic Applications

This folder demonstrates various design patterns commonly used in AI and agentic application development. Each example is designed to illustrate best practices, reusable solutions, and architectural approaches for building robust, scalable, and maintainable AI systems and agents.

## What You'll Find Here

- **Pattern Overviews:** Brief explanations of each design pattern and its relevance to AI/agentic workflows.
- **Code Examples:** Practical implementations in Python, focused on real-world scenarios.
- **Usage Guidance:** Tips on when and how to apply each pattern in your own projects.

## Example Patterns

**Reflection:** The AI evaluates and refines its own output iteratively, improving accuracy. For example, in code generation, it might review and rewrite code for better correctness and style.

**ReAct:** Combines reasoning and acting, where the AI thinks through a problem and uses tools iteratively, such as reasoning about a query and then using a calculator.

**ReWoo:** Create plan and execute to solve complex problems

**Planning:** The AI breaks down complex tasks into steps and plans their execution, such as outlining a report before writing it.

**Tool Use:** The AI interacts with external tools like databases or web searches to perform tasks requiring real-world data. An example is using a web search tool for research.

**Multi-Agent Collaboration:** Multiple AI agents with specific roles work together, like one researching and another analyzing data for a final report.


#### Identification of Key Design Patterns
Through the analysis, five primary design patterns emerged as central to building AI and agentic applications. These patterns are detailed below, with descriptions, examples, and supporting evidence from the reviewed sources.

##### Reflection Pattern
- **Description**: The Reflection pattern involves the AI system evaluating its own output and iteratively refining it to improve quality and accuracy. This simulates human-like self-critique, allowing the AI to learn from its mistakes and produce higher-quality results.  
- **Implementation**: In practice, the AI might generate an initial output, such as code or text, then reflect on its correctness, style, or efficiency, and rewrite it based on self-feedback. This can be implemented using multi-agent frameworks, where a "critic" agent reviews the "doer" agent's work, or through iterative prompting of a single LLM. Tools like unit tests or web searches can be integrated for evaluation, as noted by Andrew Ng ([https://www.linkedin.com/posts/andrewyng_one-agent-for-many-worlds-cross-species-activity-7179159130325078016-_oXr](https://www.linkedin.com/posts/andrewyng_one-agent-for-many-worlds-cross-species-activity-7179159130325078016-_oXr)).  
- **Evidence**: Research suggests significant performance gains, with Analytics Vidhya reporting that GPT-3.5 achieved 95.1% correctness on the HumanEval benchmark using reflection, compared to 48.1% with zero-shot prompting ([https://www.analyticsvidhya.com/blog/2024/10/agentic-design-patterns/](https://www.analyticsvidhya.com/blog/2024/10/agentic-design-patterns/)). Papers like Self-Refine by Madaan et al. (2023) and Reflexion by Shinn et al. (2023) further validate this pattern's effectiveness.  
- **Applications**: Common in code writing, text generation, question answering, and Retrieval-Augmented Generation (RAG) systems, where factual accuracy is critical. For instance, the SELF-RAG approach enhances RAG systems by reflecting on generated content ([https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_self_rag/](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_self_rag/)).

##### Tool Use Pattern
- **Description**: The Tool Use pattern enables AI systems to interact with external tools, such as databases, web search engines, APIs, or programming functions, to perform tasks that require real-world interaction or access to up-to-date information. This extends the capabilities of LLMs beyond their internal knowledge, making them more versatile.  
- **Implementation**: Examples include an AI agent using a web search tool to gather information for research or executing a Python script to compute a result. This pattern is often seen in agentic workflows where the AI needs to access external data, as highlighted in the DeepLearning.AI course on AutoGen ([https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/)), which includes a conversational chess game implementing tool use.  
- **Evidence**: Analytics Vidhya notes that tool use is crucial for tasks requiring real-world interaction, with resources like [https://www.analyticsvidhya.com/blog/2024/07/how-to-fine-tune-large-language-models-with-monsterapi/](https://www.analyticsvidhya.com/blog/2024/07/how-to-fine-tune-large-language-models-with-monsterapi/) providing practical guidance. The pattern is also mentioned in Andrew Ng's post as one of the four key patterns driving progress.  
- **Applications**: Widely used in research agents, data analysis, and any task requiring external data or computation, such as financial analysis or enterprise automation.

##### Planning Pattern
- **Description**: The Planning pattern involves the AI breaking down complex tasks into smaller, manageable steps and planning how to execute them. This requires reasoning about the task and creating a sequence of actions to achieve the goal, often using adaptive planning techniques.  
- **Implementation**: For example, an AI tasked with writing a report might plan to first research the topic, then outline the structure, and finally write and refine the content. Techniques like ReAct and ReWOO are used, as noted by Analytics Vidhya ([https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/](https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/), [https://billxbf.github.io/works/ReWOO_preprint.pdf](https://billxbf.github.io/works/ReWOO_preprint.pdf)). DeepLearning.AI's course includes a stock report generation example with a planning agent, demonstrating practical application ([https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/)).  
- **Evidence**: The pattern is recognized as essential for handling multi-step tasks, with Daily Dose of Data Science emphasizing its role in effective task solving ([https://blog.dailydoseofds.com/p/5-agentic-ai-design-patterns](https://blog.dailydoseofds.com/p/5-agentic-ai-design-patterns)).  
- **Applications**: Task automation, workflow management, and complex problem-solving, such as project planning or multi-step research.

##### Multi-Agent Collaboration Pattern
- **Description**: This pattern involves multiple AI agents, each with specific roles or expertise, working together to achieve a common goal. Agents can delegate tasks, share information, and coordinate their efforts, often in collaborative, supervised, or hierarchical structures.  
- **Implementation**: An example is a system with one agent for research, another for data analysis, and a third for report generation, all collaborating to produce a final output. DeepLearning.AI's course includes examples like a two-agent chat for stand-up comedy and sequential chats for customer onboarding, using the AutoGen framework ([https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/)). Analytics Vidhya also highlights collaborative, supervised, and hierarchical approaches ([https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)).  
- **Evidence**: The pattern is widely recognized, with Andrew Ng noting its potential in driving progress and Analytics Vidhya reporting its use in enterprise automation and multi-department support.  
- **Applications**: Enterprise automation, multi-step workflows, and systems requiring diverse expertise, such as content creation teams or healthcare diagnostics.

##### ReAct (Reason and Act) Pattern
- **Description**: The ReAct pattern combines reasoning and acting, allowing the AI to both think through a problem (reason) and take actions (act) using tools. It iterates between reasoning and acting until the task is complete, enhancing autonomy and adaptability.  
- **Implementation**: For instance, an AI might reason about a query, decide to use a tool like a calculator, act by invoking it, and then reason again based on the result. Daily Dose of Data Science lists ReAct as a distinct pattern, combining reflection and tool use ([https://blog.dailydoseofds.com/p/5-agentic-ai-design-patterns](https://blog.dailydoseofds.com/p/5-agentic-ai-design-patterns)), and Analytics Vidhya mentions it in the context of planning ([https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/](https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/)).  
- **Evidence**: The pattern is noted for its effectiveness in complex decision-making, with Medium articles like [https://medium.com/@aydinKerem/ai-agents-design-patterns-explained-b3ac0433c915](https://medium.com/@aydinKerem/ai-agents-design-patterns-explained-b3ac0433c915) discussing its practical implementations.  
- **Applications**: Complex decision-making, problem-solving, and tasks requiring both cognitive and interactive capabilities, such as dynamic pricing systems or adaptive gaming AI.

#### Comparative Analysis
To further illustrate the relationships and differences among these patterns, the following table summarizes their key characteristics:

| **Pattern**               | **Focus**                          | **Key Feature**                          | **Example Use Case**                     | **Framework Support**                     |
|---------------------------|------------------------------------|------------------------------------------|------------------------------------------|------------------------------------------|
| Reflection                | Self-improvement                  | Iterative self-evaluation                | Code generation with self-critique       | AutoGen, LangGraph                       |
| Tool Use                  | External interaction              | Access to real-world tools               | Research using web search                | AutoGen, LangGraph                       |
| Planning                  | Task decomposition                | Step-by-step roadmap                     | Report writing with outlined steps       | AutoGen, ReAct, ReWOO                    |
| Multi-Agent Collaboration | Teamwork                         | Role-based collaboration                 | Multi-department support agents          | AutoGen, CrewAI, LangGraph               |
| ReAct                     | Reasoning and acting              | Iterative reasoning and tool use         | Dynamic pricing with calculator use      | LangGraph, ReAct framework               |

This table highlights the distinct roles each pattern plays, with some overlap, such as ReAct combining elements of Tool Use and Planning.


## How to Use

1. Browse the subfolders or files for each pattern.
2. Read the overview and comments in the code.
3. Run the examples to see the patterns in action.
4. Adapt the patterns to your own AI or agentic applications.

## Who Should Use This

- AI engineers and researchers
- Agentic application developers
- Anyone interested in software architecture for intelligent systems

## References

[AgenticAI Design Patterns](https://medium.com/data-science-collective/stop-prompting-start-designing-5-agentic-ai-patterns-that-actually-work-a59c4a409ebb)

[Reflection](https://huggingface.co/blog/Kseniase/reflection)

[ReACT & ReWoo](https://www.analyticsvidhya.com/blog/2024/11/agentic-ai-planning-pattern/)