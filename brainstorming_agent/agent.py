"""
Filename: brainstorming_agent/agent.py
Date: 2025-07-30
Version: 1.0
Description: This script defines the graph for the brainstorming agent.
"""
from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition
from brainstorming_agent.utils.nodes import (
    call_model,
    evaluate_documents, 
    rewrite_question,
    generate_answer,
    tool_node
)
from brainstorming_agent.utils.state import AgentState

# Config definition
class GraphConfig(TypedDict):
    model_name: Literal['openai', 'ollama']


# Defining the graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)

workflow.add_node('agent', call_model)
workflow.add_node('retrieve', tool_node)
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.set_entry_point('agent')

# Decide to respond directly or use search/retrieval tools
workflow.add_conditional_edges(
    'agent',
    tools_condition,
    {
        'tools': 'retrieve',
        END: END
    }
)
# Edges taken after a tool is a called
workflow.add_conditional_edges(
    'retrieve',
    evaluate_documents # conditional node mapping happens within the function
)

workflow.add_edge('generate_answer', END)
workflow.add_edge('rewrite_question', 'agent')


graph = workflow.compile()