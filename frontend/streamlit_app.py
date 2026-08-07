import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000/chat"

st.set_page_config(
    page_title="Government AI Chatbot",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Government Services AI Chatbot")

st.write("Ask about government schemes, eligibility, documents, and CSC centres.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask your question...")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    try:

        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=30
        )

        data = response.json()

        answer = data["answer"]

    except Exception as e:

        answer = f"Error: {e}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)