import streamlit as st

from app.chatbot.rag import GovernmentRAG

st.set_page_config(
    page_title="Government AI Chatbot",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Government Services AI Chatbot")
st.write("Ask about government schemes, eligibility, documents, and CSC centres.")

if "chatbot" not in st.session_state:
    st.session_state.chatbot = GovernmentRAG()

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
        result = st.session_state.chatbot.ask(
            question,
            session_id="default"
        )

        answer = result["answer"]

    except Exception as e:
        answer = f"Error: {str(e)}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)