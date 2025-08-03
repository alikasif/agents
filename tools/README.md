# OpenAI Tools Integration Demo

This project demonstrates different approaches to integrating tools with OpenAI's Chat API and Agent SDK. It showcases the use of hosted tools (native tools), functions as tools, MCP (Message Control Protocol), and UTCP (Universal Tool Control Protocol).

## Overview

This project explores various methods for integrating external tools and APIs with OpenAI's language models. It provides examples of how to leverage different tool integration techniques to enhance the capabilities of OpenAI's Chat API and Agent SDK.

The project demonstrates the following tool integration approaches:

- **Hosted Tools (Native Tools)**: Utilizing OpenAI's built-in tools, such as web browsing, without requiring additional setup.
- **Functions as Tools**: Converting custom Python functions into OpenAI-compatible tools, allowing the language model to execute specific code snippets.
- **MCP (Message Control Protocol)**: Implementing the MCP protocol for tool management, enabling standardized communication between the language model and external tools.
- **UTCP (Universal Tool Control Protocol)**: Employing UTCP for standardized tool interactions, providing a unified interface for accessing and utilizing various tools.
[UTCP](https://github.com/universal-tool-calling-protocol)
[UTCP Examples](https://github.com/universal-tool-calling-protocol/utcp-examples)

## Features

- Demonstrates hosted tools, functions as tools, MCP, and UTCP integration with OpenAI
- Provides examples of converting custom functions into OpenAI-compatible tools
- Implements MCP for tool management and standardized communication
- Utilizes UTCP for standardized tool interactions and a unified tool interface
- Includes a REST API server for web searches using the Google Serper API
- Supports asynchronous and synchronous API calls

## Prerequisites

- Python 3.8+
- OpenAI API key
- Serper API key
- UTCP client configuration

## Installation

1. Clone the repository and navigate to the tools directory:

```bash
cd agents/tools
```

2. Install the required packages:

```bash
uv sync
```

3. Set up the environment variables in a `.env` file:

```
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
```

## Usage

### Running the Web Search Server

1. Start the FastAPI server:

```bash
python web_search_server.py
```

2. Access the API at: `http://127.0.0.1:8882/search/?query=your+search+query`

### Using OpenAI Tools

Run the OpenAI tools demo for Chat Client:

```bash
uv run tools/open_ai_chat_client_tools_demo.py 
```

Run the OpenAI tools demo for Agent:

```bash
uv run tools/open_ai_agent_tools_demo.py
```


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request.

