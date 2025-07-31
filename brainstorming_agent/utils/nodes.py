"""
Filename: brainstorming_agent/utils/nodes.py
Date: 2025-07-30
Version: 1.0
Description: This script instantiates the available LLMs for the agent and defines wrapper node functions.
"""
from functools import lru_cache # Last-Recently Used cache to reduce execution time
from pydantic import BaseModel, Field
from typing import Literal

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from brainstorming_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode

from brainstorming_agent.constants.prompt_templates import (
    EVAL_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT
)

# Evaluate documents using a binary score for relevance check
class EvaluateDocument(BaseModel):
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == 'openai':
        model = ChatOpenAI(temperature=0, model_name='gpt-4.1-mini')
    elif model_name == 'ollama':
        model = ChatOllama(temperature=0, model_name='mistral:7b', reasoning=False)
    else:
        raise ValueError(f'Unsupported model type: {model_name}')
    
    model = model.bind_tools(tools)
    return model

# Assigns a binary score to question-document pairs based on semantic relevance
def evaluate_documents(state) -> Literal['generate_answer', 'rewrite_question']:
    eval_model = _get_model('openai')

    question = state['messages'][0].content
    context = state['messages'][-1].content

    prompt = EVAL_PROMPT.format(context=context, question=question)

    response = eval_model.with_structured_output(EvaluateDocument).invoke(
        [{'role': 'user', 'content': prompt}]
    )
    score = response.binary_score

    if score == 'yes':
        return 'generate_answer'
    else:
        return 'rewrite_question'

# Rewrite the original user question
def rewrite_question(state):
    model = _get_model('openai')
    messages = state['messages']
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = model.invoke(
        [{'role': 'user', 'content': prompt}]
    )
    return {'messages': [{'role': 'user', 'content': response.content}]}

# Generates an answer following retrieval or search
def generate_answer(state):
    model = _get_model('openai')
    question = state['messages'][0].content
    context = state['messages'][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = model.invoke([{'role': 'user', 'content': prompt}])
    return {'messages': [response]}


# Defines the function that has a termination condition dependent on tool call
def should_continue(state):
    messages = state['messages']
    last_message = messages[-1]
    # Finish if there are no tool calls
    if not last_message.tool_calls:
        return 'end'
    # Otherwise, continue
    else:
        return 'continue'
    
# TODO: Improve prompt and import from separate file
system_prompt = """Be a helpful assistant"""

# Calls the main agent model
def call_model(state, config):
    messages = state['messages']
    messages = [{'role': 'system', 'content': system_prompt}] + messages
    model_name = config.get('configurable', {}).get('model_name', 'openai')
    model = _get_model(model_name)
    response = model.invoke(messages)
    # Returning a list, which will get appended to existing list
    return {'messages': [response]}

# Defines the function to execute tools
tool_node = ToolNode(tools)