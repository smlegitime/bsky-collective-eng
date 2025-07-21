import ollama
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

import traceback

from agent import Agent
from data.prompts import basic_search_prompt, config_generation_prompt

st.set_page_config(
    page_title='Bluesky Labeler Creator Prototype',
    page_icon='💬',
    layout='wide',
    initial_sidebar_state='auto'
)


def extract_model_names(models_info: list) -> tuple:
    return tuple(model['model'] for model in models_info['models'])

def main():
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{"💬"}</span>',
        unsafe_allow_html=True,
    )

    st.subheader('Single-User Prototype', divider='violet', anchor=False)

    # Select downloaded models from ollama
    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    # Instatiate agent checkpointer
    memory = MemorySaver()

    if available_models:
        selected_model = st.selectbox('Pick a model available locally on your system ↓', available_models)
    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")

    # Setting up messages
    message_container = st.container(height=500, border=True)

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        avatar = '🤖' if message['role'] == 'assistant' else '👩🏾‍🦱'
        with message_container.chat_message(message['role'], avatar=avatar):
            st.markdown(message['content'])

    # Initialize search tool
    search_tool = DuckDuckGoSearchRun(name='Search')

    # Processing messages
    if prompt := st.chat_input('Enter a prompt here...'):
        try:
            st.session_state.messages.append({'role': 'user', 'content': prompt})

            message_container.chat_message('user', avatar='👩🏾‍🦱').markdown(prompt)

            with message_container.chat_message('assistant', avatar='🤖'):
                model = ChatOllama(model=selected_model)
                
                # Calling agent with base config generation prompt
                bot = Agent(model=model, tools=[search_tool], system=config_generation_prompt, checkpointer=memory)
                messages = [HumanMessage(content=prompt)]
                thread = {"configurable": {"thread_id": "1"}}

                def generate_stream():
                    full_response = ''
                    for event in bot.workflow.stream({"messages": messages}, thread):
                        for v in event.values():
                            full_response += v['messages'][-1].content
                            yield v['messages'][-1].content
                    st.session_state.messages.append({'role': 'assistant', 'content': full_response})
                
                st.write_stream(generate_stream)
                print(bot.workflow.get_state(config=thread))
                    
        except Exception as e:
            st.error(e, icon='❌')
            st.error(f"Traceback: {traceback.format_exc()}", icon='🔍')


if __name__ == "__main__":
    main()
