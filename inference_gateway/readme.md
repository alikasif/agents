# Inference Gateway (IGW)

A unified gateway for accessing multiple LLM providers through a single API. Built with **LiteLLM** as the core proxy, providing load balancing, cost tracking, and enterprise-grade features.

## 🎯 Why Use an Inference Gateway?

| Challenge | Solution |
|-----------|----------|
| Multiple LLM APIs with different formats | **Universal API** - One endpoint for all providers |
| Vendor lock-in | **Easy switching** between OpenAI, Anthropic, Gemini, Ollama |
| Unpredictable costs | **Cost tracking** and budget controls per user/key |
| Provider outages | **Fallback routing** and circuit breakers |
| Security concerns | **API key management** with virtual keys |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Your Application                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Inference Gateway (IGW)                      │
│  ┌───────────┬───────────┬───────────┬───────────┬───────────┐  │
│  │   Load    │  Circuit  │   Cost    │  Caching  │   Auth    │  │
│  │ Balancing │  Breaker  │ Tracking  │           │  (Keys)   │  │
│  └───────────┴───────────┴───────────┴───────────┴───────────┘  │
│                         LiteLLM Proxy                           │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────┬───────┴───────┬─────────────┐
        ▼             ▼               ▼             ▼
   ┌─────────┐  ┌──────────┐   ┌──────────┐  ┌──────────┐
   │ OpenAI  │  │Anthropic │   │  Gemini  │  │  Ollama  │
   │  (API)  │  │  (API)   │   │  (API)   │  │ (Local)  │
   └─────────┘  └──────────┘   └──────────┘  └──────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Universal API** | OpenAI-compatible endpoint for all LLM providers |
| **Load Balancing** | Distribute requests across multiple model deployments |
| **Circuit Breaker** | Automatic failover when providers are down |
| **Cost Tracking** | Per-user and per-key spend monitoring |
| **Virtual Keys** | Generate API keys with model access controls |
| **Caching** | Response caching to reduce costs and latency |
| **Guardrails** | Content filtering and safety controls |
| **Auth/AuthZ** | Master key + user key authentication |
| **Logging** | Request/response logging for debugging |

---

## 🚀 Quick Start

### 1. Install LiteLLM

```bash
pip install litellm[proxy] prisma
```

### 2. Configure Environment

Create `.env` file:
```bash
# LiteLLM Proxy
LITELLM_MASTER_KEY=sk-your-master-key
DB_URL=postgresql://user:pass@localhost:5432/litellm

# Providers
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini/gemini-1.5-flash

OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 3. Start the Proxy

```bash
cd inference_gateway/litellm
litellm --config config.yaml --port 4000
```

### 4. Make a Request

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt5",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 📁 Project Structure

```
inference_gateway/
├── readme.md              # This file
└── litellm/
    ├── config.yaml        # LiteLLM proxy configuration
    ├── chat_app.py        # Python client library
    └── llm_client.py      # FastAPI client service
```

---

## 🔧 Configuration

### Model Configuration (`config.yaml`)

```yaml
model_list:
  - model_name: gpt5           # Your alias
    litellm_params:
      model: "os.environ/OPENAI_MODEL"
      api_key: "os.environ/OPENAI_API_KEY"

  - model_name: anthropic
    litellm_params:
      model: "os.environ/ANTHROPIC_MODEL"
      api_key: "os.environ/ANTHROPIC_API_KEY"

general_settings:
  master_key: "os.environ/LITELLM_MASTER_KEY"
  database_url: "os.environ/DB_URL"

litellm_settings:
  max_budget: 100            # Max spend in USD
  budget_duration: 30d       # Budget reset period
```

---

## 🐍 Python Client

```python
from inference_gateway.litellm.chat_app import (
    create_user,
    generate_key,
    chat,
    get_user_info,
    get_key_info,
)

# 1. Create a user
user = create_user("john@example.com")

# 2. Generate API key for user
key_info = generate_key(
    user_id=user["user_id"],
    models=["gpt5", "gemini", "anthropic"],
    duration="7d"
)
api_key = key_info["key"]

# 3. Make chat request
response = chat(
    prompt="What is machine learning?",
    model="gpt5",
    api_key=api_key
)
print(response)

# 4. Track usage
user_info = get_user_info(user["user_id"])
key_info = get_key_info(api_key)
print(f"Total spend: ${key_info.get('spend', 0)}")
```

---

## 🔐 Key Management

| Endpoint | Description |
|----------|-------------|
| `POST /user/new` | Create a new user |
| `GET /user/info` | Get user details and spend |
| `POST /key/generate` | Generate virtual API key |
| `GET /key/info` | Get key details and spend |

---

## 🌐 Gateway Options Comparison

| Feature | LiteLLM | Portkey AI | OpenRouter | GKE Gateway |
|---------|---------|------------|------------|-------------|
| Self-hosted | ✅ | ❌ | ❌ | ✅ |
| Multi-provider | ✅ | ✅ | ✅ | ❌ |
| Cost tracking | ✅ | ✅ | ✅ | ❌ |
| Virtual keys | ✅ | ✅ | ❌ | ❌ |
| Open source | ✅ | ❌ | ❌ | ✅ |
| Local LLMs | ✅ | ❌ | ❌ | ✅ |

---

## 📚 Resources

- [LiteLLM Docs](https://docs.litellm.ai/)
- [Portkey AI](https://portkey.ai/)
- [OpenRouter](https://openrouter.ai/)
- [GKE Inference Gateway](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/about-gke-inference-gateway)
