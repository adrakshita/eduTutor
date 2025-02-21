import streamlit as st
from pdf_handler import handle_pdf_upload
from query_handler import handle_query
from chat_manager import create_chat, select_chat, delete_chat
from quiz_generator import generate_quiz
from config import PERSIST_DIR, HF_TOKEN, LLM_MODEL_NAME, EMBED_MODEL_NAME
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os

def initialize_settings():
    # Setting up the LLM and embeddings using Hugging Face Inference API
    Settings.llm = HuggingFaceInferenceAPI(
        model_name=LLM_MODEL_NAME,
        tokenizer_name=LLM_MODEL_NAME,
        context_window=3000,
        token=HF_TOKEN,
        max_new_tokens=512,
        generate_kwargs={"temperature": 0.1},
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL_NAME
    )

initialize_settings()

# Initialize session state for chats
if 'chats' not in st.session_state:
    st.session_state.chats = {}
    st.session_state.current_chat = None

def download_chat():
    if st.session_state.current_chat and st.session_state.current_chat in st.session_state.chats:
        chat_history = st.session_state.chats[st.session_state.current_chat]
        chat_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        st.download_button(
            label="Download Chat",
            data=chat_text,
            file_name=f"{st.session_state.current_chat}_chat.txt",
            mime="text/plain"
        )

def handle_sidebar_action():
    with st.sidebar:
        st.title("Chat Management")
        chat_action = st.selectbox("Choose an action", ["Create Chat", "Select Chat", "Delete Chat", "Download Chat"])
        
        if chat_action == "Create Chat":
            chat_name = st.text_input("Enter chat name")
            if chat_name:
                create_chat(chat_name)
    
        elif chat_action == "Select Chat":
            chat_name = st.selectbox("Select chat", list(st.session_state.chats.keys()))
            if chat_name:
                select_chat(chat_name)
    
        elif chat_action == "Delete Chat":
            chat_name = st.selectbox("Select chat to delete", list(st.session_state.chats.keys()))
            if chat_name:
                delete_chat(chat_name)
        
        elif chat_action == "Download Chat":
            download_chat()

def main_app_interface():
    st.title("Edu Tutor - AI Tutor & Quiz Generator")
    st.markdown("**Retrieval-Augmented Generation & Quiz Creation** 📚🎓")
    
    # Handle PDF Upload
    handle_pdf_upload()

    # Check if a chat is selected
    if st.session_state.current_chat:
        st.subheader("💬 Chat with AI")
        
        user_prompt = st.chat_input("Ask me anything about the PDF content:")
        if user_prompt:
            st.session_state.chats[st.session_state.current_chat].append({'role': 'user', "content": user_prompt})
            response = handle_query(user_prompt)
            st.session_state.chats[st.session_state.current_chat].append({'role': 'assistant', "content": response})

        # Display Chat History
        for message in st.session_state.chats.get(st.session_state.current_chat, []):
            with st.chat_message(message['role']):
                st.write(message['content'])

        # Add quiz generation feature if PDF text is available
        if "pdf_text" in st.session_state:
            st.divider()
            st.subheader("📝 Generate a Quiz")

            num_questions = st.slider("Number of Questions", 3, 10, 5)
            
            if st.button("Generate Quiz"):
                quiz = generate_quiz(st.session_state["pdf_text"], num_questions)
                st.session_state["quiz"] = quiz
                st.success("Quiz generated successfully!")

            if "quiz" in st.session_state:
                st.markdown("### 📋 Your Quiz:")
                st.write(st.session_state["quiz"])

                # Download quiz button
                st.download_button(
                    label="Download Quiz",
                    data=st.session_state["quiz"],
                    file_name="generated_quiz.txt",
                    mime="text/plain"
                )
    else:
        st.warning("Please create or select a chat to start.")

def run_app():
    handle_sidebar_action()
    main_app_interface()

if __name__ == "__main__":
    run_app()
