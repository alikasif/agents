
# AgenticRAG-DocQA

## Approach
This project builds a robust, modular, and cloud-native agentic Retrieval-Augmented Generation (RAG) system dedicated to autonomous document Q&A. The system uses Python and leverages Azure OpenAI GPT-4-Turbo (or 3.5 for alternative flows) with a vector database (primarily Azure AI Search; supports Chroma/Pinecone for future flexibility). A central Master Orchestrator Agent coordinates a team of specialized sub-agents through CrewAI and LangGraph: a Query Analysis Agent (query refinement/decomposition), a Retrieval Agent (optimized context retrieval), and a Generation/Reflection Agent (LLM-based answer synthesis and review). The design supports multi-step, reflexive reasoning, agent collaboration, prompt augmentation (chain-of-thought, reflection), and streaming responses. It is production-oriented: secure, extensible, and ready for scalable enterprise deployment.

## Architecture Diagram
sequenceDiagram
    participant User
    participant API as API Gateway (FastAPI/Azure Functions)
    participant Auth as Auth Layer (JWT/OAuth/OpenID)
    participant Master as Master Agent (Orchestrator)
    participant Query as Query Analysis Agent
    participant Retriever as Retrieval Agent
    participant Vector as Vector DB (Azure AI Search)
    participant Generator as Generation/Reflection Agent (LLM)
    participant Storage as Document Store (Blob, Versioned)

    User->>API: Submit question (with auth token)
    API->>Auth: Validate token, enforce rate limits
    Auth-->>API: Auth ok (user info, access)
    API->>Master: Forward question + user context
    Master->>Query: Refine/Decompose query
    Query->>Master: Structured query/intent
    Master->>Retriever: Retrieve relevant passages (with access control)
    Retriever->>Vector: Vector search (semantic query, user-scoped)
    Vector-->>Retriever: Top-k relevant chunks
    Retriever-->>Master: Retrieved docs + metadata, version ids
    Master->>Generator: Compose prompt/context
    Generator->>AzureOpenAI: Call GPT-4 Turbo with context
    AzureOpenAI-->>Generator: Generated answer (possibly streamed via SSE/WebSocket)
    Generator-->>Master: Refined, final answer (+review, confidence)
    Master-->>API: Return/stream answer (logs/metrics)
    API-->>User: Show answer
    Note over Storage, Vector: Index refresh/update by background pipeline for new or changed docs


## Design Patterns
- Agent-Oriented Modular Design: Central Master Agent orchestrates specialized, collaborative sub-agents (Query Decomposition, Contextual Retrieval, Generation/Reflection).
- Separation of Concerns: Each pipeline stage (ingestion, query analysis, retrieval, synthesis, serving) is decoupled for maintainability and extensibility.
- Chain-of-Thought and Reflective Prompting: Multi-step reasoning and answer validation integrated via agent handoff chains.
- Stateful Orchestration: LangGraph manages workflow, transitions, rollback, error handling, supporting multi-hop queries and reflexive loops.
- Streaming Response Pattern: Supports low-latency UI via Server-Sent Events (SSE) from LLM to frontend.
- Security by Design: API auth (JWT/OAuth), document access control, secret management, audit logging.
- Document Versioning/Index Refresh: Background jobs and metadata version tags in vector DB ensure up-to-date answers.
- Resilient/Recoverable Architecture: Errors, timeouts, and partial failures handled by agent timeouts, fallback prompts, and rollbacks in LangGraph state.
- Scalability & Concurrency: Asynchronous agent execution, API scaling (FastAPI workers/Azure Functions), parallel retrieval and generation (where possible).

## LLM, SDKs, Tools, Frameworks
- LLM: Azure OpenAI GPT-4-Turbo (primary), GPT-3.5-Turbo (alt/cheaper flows), future extensibility to OSS LLMs (OpenAI API-compatible, Azure ML endpoints).
- Frameworks/Orchestration: LangGraph (stateful, agentic workflow), CrewAI (modular agent roles/cooperation), possible hybrid with LangChain for fallback flows.
- Vector Store: Azure AI Search (main), ChromaDB, Pinecone, Weaviate for extensibility.
- Embeddings: AzureOpenAIEmbedding API (text-embedding-ada-002).
- API Serving: FastAPI (REST, handles SSE with StreamingResponse), or Azure Functions for serverless execution (uses client-persisted state or Dapr/Redis for step recovery).
- Document Store: Azure Blob/Share, with versioned files and indexer triggers.
- Tools: Docker (container packaging), Azure Monitor/App Insights (logging/audit/alerting), Key Vault (secrets/config), pytest/Postman for tests.
- Optional: LlamaIndex or LangChain for document importing/preprocessing; Docugami for advanced doc parsing.
- Access control: JWT/OAuth2 via Azure AD or Auth0; user-context passed throughout agent chain.


## Detailed Design
1. Document Ingestion & Indexing:
   - Documents ingested via batch or event-based triggers (e.g., blob upload), chunked into coherent segments (e.g., paragraph, heading-based).
   - Preprocessed/cleaned; embedded using Azure OpenAI text-embedding-ada-002.
   - Stored in Azure AI Search (or open vector DB) with metadata: doc id, chunk id, version, access tags, timestamp, etc.
   - Index refresh pipeline periodically checks for updates (file version changes or deletions) and re-embeds affected chunks (ensures freshness, low staleness latency).
2. Security & Privacy:
   - All API endpoints require JWT/OAuth-based authentication; supports user roles (admin/user/viewer) mapped in agent logic.
   - Document access control: Each doc/chunk indexed with access control metadata; retrieval agents filter search and results by user permissions.
   - Encrypted secrets in Azure Key Vault; all inter-service comms secured via HTTPS (TLS).
   - Optional: GDPR support—allows per-user data/file deletion and audit logging of access.
   - Audit trail: Query + result association, agent action logs, access logs pushed to Azure Monitor/Audit sinks.
3. Agentic Orchestration (Core QnA Flow):
   - FastAPI or Azure Function endpoints receive user query (secured/session-aware), pass to orchestrator w/ user context.
   - LangGraph defines flow (nodes: Query Agent → Retrieval Agent → Generation Agent; reflexive cycles for complex or uncertain queries).
   - Partial failures (e.g., retrieval timeout): Orchestrator retries agent or uses fallback (e.g., less strict filters, smaller context), or gracefully returns “insufficient information.” State is logged.
   - CrewAI agents encapsulate each role; shared state passed as graph memory (question form, intermediate results, user info).
   - Parallel agent execution possible for independent retrieval tasks (multi-hop QnA, federated document stores).
   - Errors/timeouts trigger rollback or re-prompt, with fallback flows defined in LangGraph.
4. Retrieval & Vector Schema:
   - Vector DB indexed on: doc id, chunk id, version, content embedding, access tag(s), title, source URL/path, ingest time.
   - Retrieval agent queries vs. all/chosen scopes, applies access/user filters, merges top-k chunks with metadata and version info.
   - Optionally supports semantic and keyword hybrid retrieval, BM25, or rerankers.
5. Prompt Design & LLM Operations:
   - Master/system prompt: Defines roles/goals/processes for all agents; passed at orchestration/boot.
   - Query agent prompt: Breaks down/de-composes/clarifies user complex queries (supports chain-of-thought).
   - Generation agent prompt: Synthesizes answer, encouraged to cite sources and apply reflection ("review your answer"/"provide confidence score").
   - Reflection/review agent step may be optional/async for latency-sensitive apps (configurable toggles in orchestration).
   - Dynamic context window management to maintain token limit and context relevance.
6. Streaming & Serving:
   - Streaming responses from LLM to UI over SSE (Server-Sent Events) via FastAPI’s StreamingResponse, or websockets for real-time UIs.
   - Streaming supported end-to-end: LLM → Generator agent → API → User client.
   - Retry and heartbeat logic on stream failures; fallback to batch mode on broken connections.
7. Scaling & Concurrency:
   - Horizontal scaling at serving (FastAPI workers)/Azure Functions (stateless in serverless), LLM API request level, and parallel retrieval/generation where independent.
   - Orchestration/state: LangGraph state stores (in-memory for short flows, Redis/Dapr for scalable/long-running, especially in FaaS/decentralized deployments).
   - Monitoring: All queries/flows logged with timing, agent steps, errors/metrics (Azure Monitor, custom logs).
8. Update/Versioning & Audit:
   - Document additions/updates invalidate/re-embed previous chunks; version number and timestamp present in each indexed entry.
   - Background jobs sweep for deletions, handle index cleanup (soft/hard delete, as per policy).
   - All user queries and major agent actions audited for accountability; supports enterprise audit requirements.
9. Testing/QA:
   - Automated unit/integration tests (pytest, mock LLM/vector DB, FastAPI test client).
   - End-to-end flows validated on sample documents.
   - Benchmarking QnA latency/accuracy, error rate, passage coverage.
10. Extensibility:
   - Add new sub-agents (e.g., citation/rationale agent, specialized doc types) as plug-ins via CrewAI/LangGraph.
   - Swap LLM/vector provider via simple config change (shared API contract).

## Prompting Technique
- System-Level Prompting: Orchestrator prompt encodes agent roles, process sequencing, and safeguards against hallucination.
- Chain-of-Thought: Query/Generation agents use prompts that encourage a stepwise reasoning (e.g., “Break down the question before searching”, “Think through your answer in steps”).
- Reflection/Verification Loop: Generation agent (optionally asynchronous) reviews its draft, provides confidence and recommended references; loop can be skipped/batched for low-latency needs.
- Hybrid Context Prompt: Relevant passages + metadata embedded in the prompt; prompts dynamically adjust (e.g., concise vs. exhaustive answer style, citation modes).
- Few-shot/Zero-shot Examples: For high-variance queries, system prompt can inject illustrative QA pairs.
- Secure Prompting: User context/scope is passed in prompt chain (access control applied both at retrieval and prompt construction).
- Streaming Prompt: LLM output delivered as it becomes available; prompt and agent chain annotated so downstream consumers can render partial output.


## GitHub Links
- CrewAI: https://github.com/joaomdmoura/crewai
- LangGraph RAG example: https://github.com/langchain-ai/langgraph/blob/main/examples/retrieval_agents.ipynb
- Azure OpenAI RAG demo: https://github.com/Azure-Samples/azure-search-openai-demo
- LangChain QA reference: https://github.com/hwchase17/langchain/blob/master/docs/use_cases/question_answering.md
- VectorDB (Chroma): https://github.com/chroma-core/chroma
- LlamaIndex: https://github.com/jerryjliu/llama_index
- FastAPI Streaming: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- Azure Monitor/Audit: https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/logs

