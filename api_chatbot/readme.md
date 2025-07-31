# API Chatbot Project

## Overview
This project demonstrates an AI-powered API assistant that helps users interact with REST APIs using natural language. It uses the AutoGen Agent SDK to create an intelligent agent that can understand API specifications and convert natural language queries into appropriate API endpoint calls.

## Features

* Natural Language to REST API endpoint conversion
* OpenAPI/Swagger specification parsing via YAML
* AutoGen Agent SDK integration with Gemini LLM
* Integrated REST client for API calls
* Tool-enabled agent for dynamic YAML spec reading

## Components

### 1. API Specification (dog_store.yaml)
- OpenAPI/Swagger specification defining the DogStore API endpoints
- Contains endpoint definitions for managing dog records (GET, POST, PUT, DELETE)

### 2. Agent System (agent.py)
- Uses AutoGen's AssistantAgent for intelligent API interaction
- Implements YAML reading tool for dynamic spec parsing
- Converts natural language to endpoint selections
- Configurable with different LLM backends

### 3. REST Client (dog_store_client.py)
- Implements HTTP client for API interactions
- Supports all CRUD operations defined in the spec
- Handles request/response formatting

## Usage

1. Set up environment:
```bash
pip install pyautogen pyyaml requests
```

2. Run the agent:
```python
python main.py
```

3. Example queries:
- "Show me all dogs"
- "Get details for dog with ID 1"
- "Add a new dog named Max"
- "Update dog with ID 2"
- "Remove dog with ID 3"

## Architecture
```
User Query -> AutoGen Agent -> YAML Spec -> Endpoint Selection -> REST Client -> API Server
```

## Dependencies
- AutoGen Agent SDK
- PyYAML
- Requests
- Google Gemini LLM

## Configuration
The agent can be configured with different:
- LLM backends (currently using Gpt)
- API specifications (YAML format)
- System prompts for Agent

