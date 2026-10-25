import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import chatBot
import uuid

# *********************** Utility functions ***********************

# for id generation
def generate_thread_id():
    return uuid.uuid4()

# reset the chat with the new empty one
def reset_chat():
    st.session_state['thread_id']=generate_thread_id()
    add_thread(st.session_state['thread_id'])
    st.session_state['chat_name']=st.session_state['thread_id']

    st.session_state['message_history']=[]

    st.session_state['name_to_thread'][st.session_state['thread_id']]=st.session_state['thread_id']
    st.session_state['thread_id_to_name'][st.session_state['thread_id']]=st.session_state['thread_id']


# addd thread_id to the chat_threads list
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


# add chat name to the chat_names list 
def add_chat_name(name):
    if name not in st.session_state['chat_names']:
        st.session_state['chat_names'].append(name)

# for renaming the chats

#
def start_rename(thread_id):
    st.session_state["rename_thread_id"] = thread_id

def rename_chat(thread_id,name: str):
    name = name.strip()

    if not name:
        st.warning("Please enter a valid non empty name.")
        return False

    old_name = st.session_state["thread_id_to_name"][thread_id]

    if name == old_name:
        return True

    # Prevent duplicate conversation names
    for existing_id, existing_name in st.session_state["thread_id_to_name"].items():
        if existing_id != thread_id and str(existing_name) == name:
            st.warning("A chat with this name already exists.")
            return False
    
    # update thread_id_to_name
    st.session_state['thread_id_to_name'][thread_id]=name

    #update name to thread_id
    st.session_state['name_to_thread'].pop(old_name,None)
    st.session_state['name_to_thread'][name]=thread_id

    # update the list of chat_names
    if old_name in st.session_state["chat_names"]:
        index = st.session_state["chat_names"].index(old_name)
        st.session_state["chat_names"][index] = name
    else:
        st.session_state["chat_names"].append(name)

    # update the current chat name 
    if st.session_state["thread_id"] == thread_id:
        st.session_state["chat_name"] = name

        return True

def load_conversations(thread_id):
    return chatBot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']


# *********************** session setup ***********************

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_name" not in st.session_state:
    st.session_state["chat_name"] = st.session_state["thread_id"]

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

if "chat_names" not in st.session_state:
    st.session_state["chat_names"] = []

if "thread_id_to_name" not in st.session_state:
    st.session_state["thread_id_to_name"] = {}

if "name_to_thread" not in st.session_state:
    st.session_state["name_to_thread"] = {}

# Register the current conversation
current_id = st.session_state["thread_id"]
current_name = st.session_state["chat_name"]

add_thread(current_id)

if current_id not in st.session_state["thread_id_to_name"]:
    st.session_state["thread_id_to_name"][current_id] = current_name

st.session_state["name_to_thread"][current_name] = current_id
add_chat_name(current_name)



# *********************** sidebar UI ***********************

st.sidebar.title('Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads'][::-1]:

    chat_name = st.session_state["thread_id_to_name"].get(
        thread_id, str(thread_id)
    )

    col1, col2 =  st.sidebar.columns([5, 1], vertical_alignment="center")

    with col1:
     
        if st.button(chat_name,key=f"chat_{str(thread_id)}",use_container_width=True): 

            st.session_state['thead_id']=thread_id
            messages=load_conversations(thread_id)

            temp_messages=[]

            for message in messages:

                if isinstance(message,HumanMessage):
                    role='user'
                else:
                    role='ai'

                temp_messages.append({'role':role,'content':message.content})

            st.session_state['message_history']=temp_messages

    with col2:
        with st.popover("⋮"):
            if st.button("Rename",key=f"rename_{str(thread_id)}",use_container_width=True):
                start_rename(thread_id)
                st.rerun()

# Show the rename form when a conversation is selected for renaming
rename_thread_id = st.session_state.get("rename_thread_id")

if rename_thread_id is not None:
    old_name = st.session_state["thread_id_to_name"][rename_thread_id]

    with st.sidebar.form(f"rename_form_{rename_thread_id}"):
        new_name = st.text_input(
            "New conversation name",
            value="Enter a new name"
        )

        save = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")

        if save:
            success = rename_chat(rename_thread_id, new_name)

            if success:
                st.session_state.pop("rename_thread_id", None)
                st.rerun()

        if cancel:
            st.session_state.pop("rename_thread_id", None)
            st.rerun()


# *********************** main UI ***********************

# loading the convorsation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type here")

CONFIG={'configurable':{'thread_id':st.session_state['thread_id']}} 


if user_input:

    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('ai'):
        ai_responce = st.write_stream(
            message_chunk.content for message_chunk , metadata in chatBot.stream(
                   {'messages':[HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode='messages')
            )

    st.session_state['message_history'].append({'role':'ai','content':ai_responce})