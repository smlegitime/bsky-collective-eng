# Bluesky Labeler Collective Development Tool - Prototype

Prototype agent for the [Collaborative Engineering](https://docs.google.com/document/d/1Wn-cG2htkIA1lBjoc7RARM74pEaU-kdpjEFT93J5174/edit?usp=sharing) project.

## Overview

The project contains logic for the [Bluesky Labeler](https://docs.bsky.app/docs/advanced-guides/moderation) developer agent workflow prototype that should:
- Answer general questions about Bluesky, the AT protocol, and Labelers using web search or RAG
- Evaluate the semantic relevance of retrieved documents based on user queries
- Reformulate user queries for better document retrieval performance
- Generate a proposal for a label based on user input and context
- Enable user approval or editing of the proposal
- Generate a sample labeler TypeScript project based on the approved proposals

[!TIP]
Detailed [Requirements and Specifications](https://docs.google.com/document/d/1Wn-cG2htkIA1lBjoc7RARM74pEaU-kdpjEFT93J5174/edit?tab=t.bx70y9burmic#heading=h.hj1zhksgbbkb) are on a live Google doc.

### Directory Structure
The project is a [Langgraph Server](https://docs.langchain.com/langgraph-platform/langgraph-server) application and follows the required [application structure configuration](https://docs.langchain.com/langgraph-platform/setup-app-requirements-txt) for deployment.
```
└── 📁bsky-collective-eng
    └── 📁brainstorming_agent
        └── 📁constants
            ├── output_samples.py
            ├── prompt_templates.py
            ├── retrieval_sources.json
        └── 📁utils
            ├── __init__.py
            ├── nodes.py
            ├── rag_utils.py
            ├── state.py
            ├── test_func.ipynb
            ├── tools.py
        ├── __init__.py
        ├── agent.py
        ├── requirements.txt
    └── 📁data
        └── 📁bsky-docs
    ├── .gitignore
    ├── langgraph.json
    └── README.md
```
[!IMPORTANT]
The project needs a `.env` file with the `OPENAI_API_KEY` to use the GPT-4.1 model and `TAVILY_API_KEY` for the web search tool. Be sure to add that file after cloning this repo.

## Installation & Usage
#### Using Langgraph Studio
[!NOTE]
You'll need to add the `LANGSMITH_API_KEY` to your `.env` file. You can [create a LangSmith account](https://smith.langchain.com/o/null/host/deployments) if needed. 

To install [Langgraph Studio](https://docs.langchain.com/langgraph-platform/langgraph-studio)

### Installation
Clone this repository

Add the `.env` file in the root of the project

Initialize a virtual environment
```sh
conda create -n my_virtual_env python=3.12
```

Install dependencies
```sh
pip install -U "langgraph-cli[inmem]"
```
and run
```sh
langgraph dev
```
## More Resources
- [Multi-agent systems](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Langchain tools](https://python.langchain.com/docs/integrations/tools/). The protoype uses the Tavily Web Search tool
- [LangSmith - Get Started](https://docs.smith.langchain.com/)
- [Document loaders](https://python.langchain.com/docs/integrations/document_loaders/). The prototype uses the [`WebBaseLoader`](https://python.langchain.com/docs/integrations/document_loaders/web_base/) document loader for the retrieval tool.
- [ChatOllama](https://python.langchain.com/v0.2/api_reference/ollama/chat_models/langchain_ollama.chat_models.ChatOllama.html#)
