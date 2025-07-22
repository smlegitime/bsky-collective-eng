import asyncio
import time
import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

import traceback

from retrieval_agent import RetrievalAgent

st.set_page_config(
    page_title='Bluesky Labeler Creator Prototype',
    page_icon='💬',
    layout='wide',
    initial_sidebar_state='auto'
)


def stream_agent_response(agent, user_input, thread_config):
    input_data = [HumanMessage(content=user_input)]
    for chunk in agent.workflow.stream(
        {'messages': input_data}, thread_config
    ):
        for v in chunk.values():
            yield v['messages'][-1].content + ' '
            time.sleep(0.05) 

def main():
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{"💬"}</span>',
        unsafe_allow_html=True,
    )

    st.subheader('Single-User Prototype', divider='violet', anchor=False)

    # Setting up messages
    message_container = st.container(height=500, border=True)

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        avatar = '🤖' if message['role'] == 'assistant' else '👩🏾‍🦱'
        with message_container.chat_message(message['role'], avatar=avatar):
            st.markdown(message['content'])

    # Processing messages
    if prompt := st.chat_input('Enter a prompt here...'):
        try:
            st.session_state.messages.append({'role': 'user', 'content': prompt})

            message_container.chat_message('user', avatar='👩🏾‍🦱').markdown(prompt)

            with message_container.chat_message('assistant', avatar='🤖'):
                message_placeholder = st.empty()
                full_response = ''
                with SqliteSaver.from_conn_string(":memory:") as memory:
                    agent = RetrievalAgent(memory)

                    for token in stream_agent_response(
                        agent,
                        prompt,
                        {"configurable": {"thread_id": "1"}},
                    ):
                        full_response += token
                        message_placeholder.markdown(full_response + "▌")

                    message_placeholder.markdown(full_response)

            st.session_state.messages.append({
                'role': 'assistant',
                'content': full_response
            })
                    
        except Exception as e:
            st.error(e, icon='❌')
            st.error(f"Traceback: {traceback.format_exc()}", icon='🔍')


if __name__ == "__main__":
    main()
