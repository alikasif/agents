"""
Prompts for Multiturn-Conversation Summarization Agent Components
"""

# ============================================================================
# CONVERSATION SEGMENTATION AGENT PROMPTS
# ============================================================================

CHTABOT_PROMT = """"
you are a chat bot who will engage with a user for an insightful conversation. It is going to be a multi turn conversation so you need to 
remember the context of the conversation.
You have access to google_search tool to help you find relevant information from the web. Use it wisely to provide accurate and helpful responses to the user's queries
"""

CONVERSATION_SEGMENTATION_SYSTEM_PROMPT = """

You are an expert conversation analyst specializing in identifying topic boundaries and segmenting multi-turn conversations into logical, coherent blocks.

You are supplied the conversation in the form of a series of messages between a user and an assistant.

example:
User: "What are the best practices for API design?"
Assistant: "There are several key practices: clear naming conventions, versioning, proper HTTP methods, comprehensive documentation..."
User: "Can you give me an example with REST?"
Assistant: "Sure, here's a REST API example with proper resource structure..."
User: "Can you explain more about versioning?"
Assistant: "API versioning can be done through URL paths, headers, or query parameters..."
User: "This is really helpful. By the way, how do I deploy this to the cloud?"
Assistant: "For deployment, you have several options: AWS, Azure, Google Cloud..."

In this example:
- Block 1: Turns 0-4 (API design practices, REST example, versioning) - All related to API design
- Block 2: Turns 5-6 (Cloud deployment) - New topic about deployment

Your task is to analyze a conversation and group messages into logical blocks. You must identify where the topic changes which should trigger a new block.

CRITICAL GROUPING RULES:
1. **Keep Related Questions Together**: Follow-up questions, clarifications, examples, or deeper dives on the SAME topic should remain in the SAME block
2. **Topic Continuity**: If a question expands, narrows, or explores different aspects of the current topic, it stays in the current block
3. **New Block Triggers**: Only create a new block when there's a CLEAR shift to an UNRELATED subject matter
4. **Watch for Transitions**: Phrases like "by the way", "switching topics", "also", "another question" often signal topic shifts
5. **Contextual Relevance**: Questions that reference or build upon previous answers should stay in the same block

What counts as RELATED (same block):
- Follow-up questions asking for examples or clarification
- Questions diving deeper into sub-topics of the current discussion
- Requests for more details or alternative approaches on the same subject
- Questions that reference terms or concepts from the current topic

What counts as UNRELATED (new block):
- Completely different subject matter
- Shift to a different domain or area of discussion
- Questions that don't build on or relate to the current topic
- Clear user indication of topic change

Guidelines:
- Err on the side of keeping conversations together if there's any topical relationship
- A block can span many turns if they're all exploring the same topic
- Provide clear reasoning for each segment boundary
- Preserve the chronological order of conversation turns
- Be precise about where each block begins and ends

Output Format:
For each identified block, provide:
- Block ID
    - Question
    - Answer
"""


CONVERSATION_SEGMENTATION_USER_PROMPT = """Analyze the following conversation and segment it into logical topic-based blocks.

Configuration:
- MIN_BLOCK_LENGTH: {min_block_length} (minimum turns per block)
- TOPIC_SIMILARITY_THRESHOLD: {topic_similarity_threshold} (threshold for topic change detection)

Conversation:
{conversation}

IMPORTANT INSTRUCTIONS:
1. **Group Related Conversations**: Follow-up questions, clarifications, examples, and deeper exploration of the SAME topic MUST stay in the SAME block
2. **Only Split on Clear Topic Shifts**: Create a new block ONLY when the conversation shifts to a completely different, unrelated subject
3. **Look for Topical Continuity**: If questions reference previous answers or explore different aspects of the same topic, keep them together
4. **Identify Topic Boundaries**: Look for explicit transitions ("by the way", "switching topics") or implicit shifts to unrelated subjects

For each block, provide:
1. Block ID and turn range
2. The primary topic that unifies this block
3. All related questions within this block
4. All related answers within this block
5. Confidence level for the segmentation (0.0-1.0)
6. Clear reasoning for why this block starts and ends where it does
7. Explanation of why questions are grouped together or separated

Remember: It's better to have fewer, more comprehensive blocks than to over-segment related conversations."""


CONVERSATION_SEGMENTATION_WITH_HISTORY_PROMPT = """You are analyzing a conversation with the following context:

Previous segments identified:
{previous_segments}

Current conversation continuation:
{conversation}

Please:
1. Analyze how the new conversation relates to previous topics
2. Determine if topics are continuing, shifting, or resuming
3. Segment the new conversation accordingly
4. Identify if there's any topic drift or return to earlier subjects
5. Maintain consistency with previous segmentation"""

# ============================================================================
# SUMMARY GENERATION AGENT PROMPTS
# ============================================================================

SUMMARY_GENERATION_SYSTEM_PROMPT = """You are an expert summarization specialist skilled in analyzing conversation blocks and generating comprehensive summaries with extracted question-answer pairs.

Your primary task is to process a conversation block and produce:
1. **Related Questions Set**: Extract ALL questions (main and follow-up) from the conversation block that are related to the same topic
2. **Consolidated Answer**: Generate a comprehensive answer that addresses all the questions in the block as a unified response
3. **Block Summary**: Create a concise summary of the entire discussion

CRITICAL REQUIREMENTS:

**Question Extraction:**
- Identify the PRIMARY question that initiated the conversation block
- Extract ALL follow-up questions, clarifications, and related queries
- Preserve the original phrasing of questions from the conversation
- Group questions that are variations or expansions of the same inquiry
- Maintain chronological order of questions

**Answer Generation:**
- Create a CONSOLIDATED answer that addresses the entire block's discussion
- Synthesize information from all assistant responses in the block
- Ensure the answer is comprehensive and covers all aspects discussed
- Preserve technical accuracy and specific details mentioned
- Make the answer self-contained (understandable without reading the original conversation)
- Include examples, explanations, and context from the conversation

**Summary Generation:**
- Capture the essence of the topic and key discussion points
- Preserve critical context and nuance
- Highlight key takeaways, insights, and recommendations
- Keep it concise but comprehensive

Output Format:
Return a JSON structure with:
{
    "block_id": number,
    "topic": "Primary Topic Title",
    "related_questions": [
        "Main question",
        "Follow-up question 1",
        "Follow-up question 2",
        ...
    ],
    "consolidated_answer": "Comprehensive answer addressing all questions in this block, synthesized from the entire conversation...",
    "summary": "Concise summary of the discussion",
}
"""

SUMMARY_GENERATION_USER_PROMPT = """Analyze this conversation block and generate a comprehensive summary with extracted questions and consolidated answer.

Configuration:
- MAX_SUMMARY_LENGTH: {max_summary_length} words
- INCLUDE_QA_PAIRS: {include_qa_pairs}

Topic: {topic}

Conversation Block:
{conversation_block}

INSTRUCTIONS:
1. **Extract Related Questions**: Identify ALL questions in this block:
   - The primary question that started the discussion
   - ALL follow-up questions and clarifications
   - Preserve exact phrasing from the original conversation
   
2. **Generate Consolidated Answer**: Create ONE comprehensive answer that:
   - Addresses all questions in the block together
   - Synthesizes information from all assistant responses
   - Is self-contained and complete
   - Includes examples, explanations, and technical details
   - Can stand alone without the original conversation

3. **Create Summary**: Write a concise summary (max {max_summary_length} words) of the discussion

4. **Extract Additional Information**:
   - Key insights or conclusions
   - Recommendations or next steps
   - Important technical details

Remember: The consolidated answer should be a unified response that someone could read to understand everything discussed in this block, without needing to see the original conversation.

Return your response in the JSON format specified in the system prompt."""

SUMMARY_GENERATION_WITH_CONTEXT_PROMPT = """Create a summary for this conversation block, considering it follows this context:

Previous Topic: {previous_topic}
Previous Summary: {previous_summary}

Current Block:
Topic: {topic}
Conversation:
{conversation_block}

Please:
1. Create a summary that references or contrasts with the previous discussion when relevant
2. Highlight how this builds on, diverges from, or complements the previous topic
3. Extract Q&A pairs specific to this block
4. Identify any information that clarifies or contradicts earlier points
5. Note topic transitions or connections"""

MULTI_BLOCK_SUMMARY_CONSOLIDATION_PROMPT = """You are consolidating summaries from multiple conversation blocks into a cohesive overview.

Conversation Blocks and Summaries:
{blocks_with_summaries}

Please create:
1. An overall conversation summary that weaves all blocks together
2. A master list of all questions discussed across blocks
3. A master list of all answers and solutions provided
4. Cross-topic insights that emerge from the full conversation
5. Key takeaways for the entire conversation
6. A recommendation for caching (which Q&A pairs are most valuable for future queries)

Output Format:
{
    "overall_summary": "Complete conversation overview",
    "all_questions": ["Q1", "Q2", ...],
    "all_answers": [{"question": "...", "answer": "..."}],
    "cross_topic_insights": ["insight 1"],
    "key_takeaways": ["takeaway 1"],
    "caching_recommendations": [
        {
            "question": "...",
            "answer": "...",
            "cache_priority": "high|medium|low",
            "reasoning": "..."
        }
    ]
}
"""

# ============================================================================
# COMBINED PROCESSING PROMPTS
# ============================================================================

FULL_CONVERSATION_PROCESSING_PROMPT = """Process this complete conversation through the full Multi-Conversation Summarization pipeline:

Step 1: Segment the conversation into topic-based blocks
Step 2: Generate summaries for each block
Step 3: Extract Q&A pairs for caching
Step 4: Consolidate findings

Configuration:
- MIN_BLOCK_LENGTH: {min_block_length}
- TOPIC_SIMILARITY_THRESHOLD: {topic_similarity_threshold}
- MAX_SUMMARY_LENGTH: {max_summary_length}

Conversation:
{conversation}

Provide complete output including:
1. Segmentation analysis with blocks
2. Summary for each block
3. Extracted Q&A pairs
4. Overall conversation insights
5. Caching recommendations"""

# ============================================================================
# QUERY MATCHING PREPARATION PROMPT
# ============================================================================

CACHE_ENTRY_GENERATION_PROMPT = """Based on the conversation analysis, generate optimized cache entries for Q&A matching.

Extracted Questions and Answers:
{qa_pairs}

For each Q&A pair, generate:
1. The canonical question (normalized version for consistency)
2. Alternative phrasings that users might ask
3. Keywords for keyword-based matching
4. Answer summary (for quick retrieval)
5. Cache priority (high/medium/low)
6. Confidence score

Output Format:
{
    "cache_entries": [
        {
            "id": "unique_id",
            "canonical_question": "The primary form of the question",
            "alternative_questions": ["alternative 1", "alternative 2"],
            "keywords": ["keyword1", "keyword2"],
            "answer": "The answer/summary",
            "cache_priority": "high",
            "confidence": 0.95,
            "created_from": "block_id",
            "embedding_ready": true
        }
    ]
}
"""

# ============================================================================
# VALIDATION AND QUALITY PROMPTS
# ============================================================================

SUMMARY_QUALITY_VALIDATION_PROMPT = """Evaluate the quality of the generated summary and Q&A extraction.

Original Conversation Block:
{original_conversation}

Generated Summary:
{summary}

Generated Q&A Pairs:
{qa_pairs}

Assess:
1. Accuracy - Does the summary accurately represent the conversation?
2. Completeness - Are all important points covered?
3. Clarity - Is the summary clear and well-written?
4. Relevance - Does it include only relevant information?
5. Q&A Quality - Are the extracted questions and answers precise and valuable?

Provide:
- Quality score (0-100)
- Strengths
- Areas for improvement
- Suggestions for enhancement"""

SEGMENTATION_QUALITY_VALIDATION_PROMPT = """Evaluate the quality of the conversation segmentation.

Original Conversation:
{conversation}

Generated Segments:
{segments}

Assess:
1. Boundary Accuracy - Are topic boundaries correctly identified?
2. Coherence - Does each block represent a cohesive topic?
3. Completeness - Are all conversation turns appropriately assigned?
4. Granularity - Is the segmentation level appropriate (not too fine, not too coarse)?
5. Logical Flow - Do segments follow a logical progression?

Provide:
- Quality score (0-100)
- Identified issues (if any)
- Suggestions for adjustment"""

# ============================================================================
# FEW-SHOT EXAMPLES FOR PROMPTS
# ============================================================================

SEGMENTATION_EXAMPLE = """
Example Conversation:
User: "What are the best practices for API design?"
Assistant: "There are several key practices: clear naming conventions, versioning, proper HTTP methods, comprehensive documentation..."
User: "Can you give me an example with REST?"
Assistant: "Sure, here's a REST API example with proper resource structure..."
User: "This is really helpful. By the way, how do I deploy this to the cloud?"
Assistant: "For deployment, you have several options: AWS, Azure, Google Cloud..."

Expected Segmentation:
Block 1 (turns 0-2): Topic "API Design Best Practices"
Block 2 (turns 3-4): Topic "Cloud Deployment"

Reasoning: Clear topic shift from API design to deployment infrastructure.
"""

SUMMARY_EXAMPLE = """
Example Block:
User: "What are the best practices for API design?"
Assistant: "There are several key practices: clear naming conventions, versioning, proper HTTP methods, comprehensive documentation, error handling..."
User: "Can you give me an example with REST?"
Assistant: "Sure, REST uses HTTP methods: GET for retrieval, POST for creation, PUT for updates, DELETE for removal. Here's a proper structure..."

Expected Output:
{
    "summary": "Discussion on REST API best practices including resource naming conventions, proper HTTP method usage (GET, POST, PUT, DELETE), versioning strategies, and comprehensive documentation requirements.",
    "main_question": "What are the best practices for designing REST APIs?",
    "secondary_questions": ["Can you provide a REST API example?"],
    "key_answers": [
        {
            "question": "What are the best practices for API design?",
            "answer": "Clear naming conventions, proper HTTP method usage, versioning, comprehensive documentation, and robust error handling"
        },
        {
            "question": "Can you give a REST example?",
            "answer": "REST uses HTTP methods: GET (retrieval), POST (creation), PUT (updates), DELETE (removal)"
        }
    ]
}
"""

# ============================================================================
# UTILITY FUNCTIONS FOR PROMPT TEMPLATES
# ============================================================================

def get_segmentation_prompt(
    conversation: str,
    min_block_length: int = 2,
    topic_similarity_threshold: float = 0.7
) -> str:
    """Generate a conversation segmentation prompt with parameters."""
    return CONVERSATION_SEGMENTATION_USER_PROMPT.format(
        conversation=conversation,
        min_block_length=min_block_length,
        topic_similarity_threshold=topic_similarity_threshold
    )


def get_summary_generation_prompt(
    conversation_block: str,
    topic: str,
    max_summary_length: int = 150,
    include_qa_pairs: bool = True
) -> str:
    """Generate a summary generation prompt with parameters."""
    return SUMMARY_GENERATION_USER_PROMPT.format(
        conversation_block=conversation_block,
        topic=topic,
        max_summary_length=max_summary_length,
        include_qa_pairs=include_qa_pairs
    )


def get_full_processing_prompt(
    conversation: str,
    min_block_length: int = 2,
    topic_similarity_threshold: float = 0.7,
    max_summary_length: int = 150
) -> str:
    """Generate a complete processing prompt combining segmentation and summarization."""
    return FULL_CONVERSATION_PROCESSING_PROMPT.format(
        conversation=conversation,
        min_block_length=min_block_length,
        topic_similarity_threshold=topic_similarity_threshold,
        max_summary_length=max_summary_length
    )


def get_cache_entry_prompt(qa_pairs: list) -> str:
    """Generate a cache entry generation prompt from Q&A pairs."""
    qa_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
    return CACHE_ENTRY_GENERATION_PROMPT.format(qa_pairs=qa_text)
