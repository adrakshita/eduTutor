from llama_index.core import ServiceContext
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
import streamlit as st
from config import HF_TOKEN, LLM_MODEL_NAME

# Initialize LLM
llm = HuggingFaceInferenceAPI(
    model_name=LLM_MODEL_NAME,
    token=HF_TOKEN,
    max_new_tokens=500,
    generate_kwargs={"temperature": 0.3}
)

class SimpleTextSplitter:
    def __init__(self, separator=" ", chunk_size=8000, chunk_overlap=0):
        self.separator = separator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        words = text.split(self.separator)
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = self.separator.join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        return chunks

def generate_quiz(pdf_text, num_questions, max_tokens=8000):
    """Generates a quiz with properly formatted multiple-choice questions."""

    splitter = SimpleTextSplitter(separator=" ", chunk_size=max_tokens, chunk_overlap=0)
    chunks = splitter.split_text(pdf_text)
    
    formatted_questions = []

    for chunk in chunks:
        prompt = f"""
        Generate {num_questions} well-formatted multiple-choice questions from the following text. 
        Ensure each question is followed by four answer choices, each on a new line in the format:
        
        Question X: <question text>
        A. <option A>
        B. <option B>
        C. <option C>
        D. <option D>
        
        Text:
        {chunk}
        """
        response = llm.complete(prompt).text.strip()

        formatted_questions.append(response)

    # Formatting output
    quiz_output = "### 📋 Quiz Questions:\n\n" + "\n\n".join(formatted_questions)

    return quiz_output

