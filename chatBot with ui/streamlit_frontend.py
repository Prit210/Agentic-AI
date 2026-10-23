import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import chatBot

CONFIG={'configurable':{'thread_id':1}}

if 'message_history' not in st.session_state:
    st.session_state['config']=CONFIG
    st.session_state['message_history']=[]


# loading the convorsation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type here")

if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    responce = chatBot.invoke({'messages':[HumanMessage(content=user_input)]},config=st.session_state['config'])
    ai_responce = responce['messages'][-1].content

    st.session_state['message_history'].append({'role':'ai','content':ai_responce})
    with st.chat_message('ai'):
        st.text(ai_responce)  
