from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage, ToolMessage

# Agent state for persistence - new messages are appended to the state
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:

    def __init__(self, model, tools, checkpointer, system=''):
        self.system = system

        # Define workflow graph
        workflow = StateGraph(AgentState)
        workflow.add_node('llm_call', self.call_ollama)
        workflow.add_node('action', self.take_action)
        workflow.add_conditional_edges(
            'llm_call',
            self.exists_action,
            {True: 'action', False: END}
        )
        workflow.add_edge('action', 'llm_call')
        workflow.set_entry_point('llm_call')
        self.workflow = workflow.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state:AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0
    
    def call_ollama(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}
    
    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f'Calling: {t}')
            if not t['name'] in self.tools:
                print('\n ....bad tool name....')
                result = 'bad tool name, retry'
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(
                tool_call_id=t['id'],
                name=t['name'],
                content=str(result)
            ))
        print('Back to the model!')
        return {'messages': results}