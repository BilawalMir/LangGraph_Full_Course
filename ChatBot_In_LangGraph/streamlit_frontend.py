import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable": {"thread_id": "thread-1"}}
# st.session_state --> dict
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


for sms in st.session_state["message_history"]:
    with st.chat_message(sms["role"]):
        st.text(sms["content"])
user_input = st.chat_input("type here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]}, config=CONFIG
    )
    ai_message = response["message"][-1].content
    st.session_state["message_history"].append({"role": "user", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)