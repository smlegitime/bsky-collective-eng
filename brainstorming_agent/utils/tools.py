"""
Filename: brainstorming_agent/utils/tools.py
Date: 2025-07-30
Version: 1.0
Description: This script defines the tools available to the brainstorming agent.
"""
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools.retriever import create_retriever_tool

from brainstorming_agent.utils.rag_utils import preprocess_docs, initialize_retriever

# Is processing docs from urls defined in ../data/retrieval_sources.json 
doc_splits = preprocess_docs()

# Retriever tool for RAG
retriever_tool = create_retriever_tool(
    retriever=initialize_retriever(doc_splits),
    name="retrieve_bsky_docs",
    description="Search and return information about the Bluesky social app and Bluesky labelers.",
)

# Agent has access to web search and RAG tools
tools = [
    TavilySearchResults(max_results=2), 
    retriever_tool
]