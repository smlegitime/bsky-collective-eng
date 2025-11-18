"""
Researcher Agent

This agent retrieves context from a knowledge base to help answer user queries.
"""

from langchain.tools import tool
from langchain.agents import create_agent

from utils.indexing import build_index
from src import model # Claude model defined in package __init__

# ---- SYSTEM PROMPT AND STATE ----

RESEARCHER_AGENT_PROMPT = """
You are a smart and helpful research agent.
You have access to a tool that retrieves context from a blog post.
Use the tool to help answer user queries.
"""

# ---- TOOLS ----

@tool(response_format="content_and_artifact")
def retrieve_context(query:str):
    """Retrieve information to help answer a query."""
    vector_store = build_index()
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# ---- AGENT DEFINITION ----

researcher_agent = create_agent(
    model=model,
    tools=[retrieve_context],
    system_prompt=RESEARCHER_AGENT_PROMPT
)