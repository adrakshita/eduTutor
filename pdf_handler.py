import os
import PyPDF2
import streamlit as st
from config import DATA_DIR

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def handle_pdf_upload():
    """Handles PDF upload and extraction."""
    os.makedirs(DATA_DIR, exist_ok=True)

    uploaded_file = st.file_uploader("Upload your PDF and Click Submit to Process", type=["pdf"])
    if st.button("Submit & Process"):
        if uploaded_file:
            pdf_path = os.path.join(DATA_DIR, "uploaded_pdf.pdf")
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            text = extract_text_from_pdf(pdf_path)
            st.session_state["pdf_text"] = text  # Store extracted text in session
            st.success("PDF processed successfully!")
        else:
            st.warning("Please upload a PDF file.")
