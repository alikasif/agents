"""
Prompts for Multi-Conversation Summarization Agent Components

This module contains LLM prompts for:
1. Conversation Segmentation Agent - Identifies topic boundaries and groups messages
2. Summary Generation Agent - Creates summaries and extracts Q&A pairs
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

exmaple:
User: "What are the best practices for API design?"
Assistant: "There are several key practices: clear naming conventions, versioning, proper HTTP methods, comprehensive documentation..."
User: "Can you give me an example with REST?"
Assistant: "Sure, here's a REST API example with proper resource structure..."
User: "This is really helpful. By the way, how do I deploy this to the cloud?"
Assistant: "For deployment, you have several options: AWS, Azure, Google Cloud..."

Your task is to analyze a conversation and prepare the logical block based on the conversation. You must identify where the topics changes which should call for newer block. You must:
1. Identify clear topic boundaries where the conversation shifts to a new subject
2. Group related consecutive messages into logical conversation blocks
3. Handle smooth topic transitions gracefully
4. Ensure each block represents a focused discussion on a specific topic or subtopic

Guidelines:
- A new topic block should start when there's a clear shift in subject matter
- Related follow-up questions on the same topic should stay in the same block
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

Please identify:
0. Related follow-up questions on the same topic should stay in the same block
1. All topic blocks with clear boundaries
2. The primary topic of each block
3. Confidence level for each segmentation point
4. Reasoning for each topic transition

Ensure each block is meaningful and represents a distinct topic or sub-topic discussion."""

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

SUMMARY_GENERATION_SYSTEM_PROMPT = """You are an expert summarization specialist skilled in creating concise, accurate summaries of conversation blocks while extracting key question-answer pairs.

Your responsibilities:
1. Create abstractive summaries that capture the essence of the conversation block
2. Preserve critical context, nuance, and important details
3. Extract primary questions asked and corresponding answers/responses
4. Identify key takeaways and insights
5. Ensure summaries are self-contained and understandable without the original conversation

Guidelines:
- Summaries should be concise but comprehensive (capture all essential information)
- Preserve technical accuracy and specific details mentioned
- Identify the main question that drives the block
- Extract secondary questions if relevant
- Capture both explicit answers and implicit conclusions
- Highlight any decisions, recommendations, or next steps
- Maintain professional, clear language
- Avoid unnecessary filler or repetition

Output Format:
Return a JSON structure with:
{
    "block_id": number,
    "topic": "Topic Title",
    "summary": "Concise summary of the block",
    "main_question": "Primary question addressed",
    "secondary_questions": ["question 1", "question 2"],
    "key_answers": [
        {
            "question": "What is...",
            "answer": "..."
        }
    ],
    "key_insights": ["insight 1", "insight 2"],
    "recommendations": ["recommendation 1"],
    "summary_length": word_count,
    "quality_score": 0.95
}
"""

SUMMARY_GENERATION_USER_PROMPT = """Create a comprehensive summary and extract Q&A pairs from the following conversation block.

Configuration:
- MAX_SUMMARY_LENGTH: {max_summary_length} words
- INCLUDE_QA_PAIRS: {include_qa_pairs}

Topic: {topic}

Conversation Block:
{conversation_block}

Please provide:
1. A concise summary (max {max_summary_length} words) that captures the key discussion
2. The main question that drives this conversation block
3. Any secondary or follow-up questions asked
4. Key answers and explanations provided
5. Important insights or conclusions reached
6. Any recommendations or next steps mentioned
7. Quality assessment of the summary

Ensure the summary is self-contained and provides value for future reference."""

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
