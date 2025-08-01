"""
Filename: brainstorming_agent/utils/state.py
Date: 2025-07-30
Version: 1.0
Description: This script defines the agent's state (context + messages).
"""
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]