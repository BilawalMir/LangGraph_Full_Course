import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid
from langgraph_database_backend import retrieve_all_threads


# ******************************* Utility Functions *************************************


def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id


def reset_chat():
    thread_id = generate_thread_id()
    del st.session_state.message_history[:]
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    st.rerun()


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# ************************** Session State *************************************

# st.session_state --> dict
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# ******************************* SideBar UI *************************************
st.sidebar.title("LangGraph ChatBot")

if st.sidebar.button("New Chat"):
    reset_chat()


st.sidebar.header("MY Conversation")

for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for sms in messages:
            if isinstance(sms, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role": role, "content": sms.content})
        st.session_state["message_history"] = temp_messages


# ******************************* Main UI *************************************

# loading conversation history
for sms in st.session_state["message_history"]:
    with st.chat_message(sms["role"]):
        st.text(sms["content"])
user_input = st.chat_input("type here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    # CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}
    # this is for separate thread interface in LangSMITH and Also name the Traces name chat_turn
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }
    # first add message to message history
    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadate in chatbot.stream(
                {"message": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": CONFIG}},
                stream_mode="messages",
            )
        )
    st.session_state["message_history"].append({"role": "user", "content": ai_message})
# The End
# Function not working because thread didnt stored i db right now
# def load_conversation(thread_id):
# return chatbot.get_state(config={"configurable": {"thread_id": thread_id}}).values[
#    "messages"
# ]
