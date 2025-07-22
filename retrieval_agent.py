from langgraph.graph import MessagesState
from langchain_ollama import ChatOllama
from langchain_text_splitters import Language
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import init_chat_model

from utils import load_docs, split_code, create_retriever
from data.prompts import GENERATE_PROMPT, GRADE_PROMPT, REWRITE_PROMPT

# Consts
SOURCE_CODE_PATH = './data/labeler-starter-kit-bsky-main/src'
FILE_EXTS = [".ts"]
LANG = Language.TS

def instantiate_retriever_tool():
    docs = load_docs(SOURCE_CODE_PATH, FILE_EXTS)
    split_docs = split_code(docs, LANG)
    retriever = create_retriever(split_docs)

    retriever_tool = create_retriever_tool(
        retriever,
        'retrieve_source_code',
        'Search and return information about the provided source code.'
    )
    return retriever_tool

class GradeDocuments(BaseModel):
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

class RetrievalAgent:
    def __init__(self, memory):
        self.retriever_tool = instantiate_retriever_tool()
        self.response_model = ChatOllama(model='mistral:7b')
        self.grader_model = init_chat_model(
            model='llama3.2',
            model_provider='ollama',
        )

        workflow = StateGraph(MessagesState)

        workflow.add_node(self.generate_query_or_respond)
        workflow.add_node('retrieve', ToolNode([self.retriever_tool]))
        workflow.add_node(self.rewrite_question)
        workflow.add_node(self.generate_answer)

        workflow.add_edge(START, 'generate_query_or_respond')

        # Decide whether to retrieve
        workflow.add_conditional_edges(
            'generate_query_or_respond',
            tools_condition, # assess llm decision (call retreiver_tool or respond to user)
            {
                'tools': 'retrieve',
                END: END
            }
        )

        # After the retrieval node is called
        workflow.add_conditional_edges(
            'retrieve',
            self.grade_documents # assess agent decision
        )

        self.workflow = workflow.compile(checkpointer=memory)

    def generate_query_or_respond(self, state: MessagesState):
        """Determine whether the llm should call the retriever tool or answer on its own"""
        response = (
            self.response_model.bind_tools([self.retriever_tool]).invoke(state['messages'])
        )
        return {'messages': [response]}
    
    def grade_documents(self, state: MessagesState) -> Literal['generate_answer', 'rewrite_question']:
        """Determine whether the retrieved documents are relevant to the question"""
        question = state['messages'][0].content #human message
        context = state['messages'][-1].content #ai message

        prompt = GRADE_PROMPT.format(question=question, context=context)
        response = (
            self.grader_model.with_structured_output(GradeDocuments).invoke(
                [{'role': 'user', 'content': prompt}]
            )
        )
        score = response.binary_score

        if score == 'yes':
            return 'generate_answer'
        else:
            return 'rewrite_question'

    def rewrite_question(self, state: MessagesState):
        """Rewrite the original user question."""
        messages = state['messages']
        question = messages[0].content
        prompt = REWRITE_PROMPT.format(question=question)
        response = self.response_model.invoke([{'role': 'user', 'content': prompt}])
        return {'messages': [{'role': 'user', 'content': response.content}]}
    
    def generate_answer(self, state: MessagesState):
        """Generate an answer"""
        question = state['messages'][0].content
        context = state['messages'][-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self.response_model.invoke([{'role': 'user', 'content': prompt}])
        return {'messages': [response]}
