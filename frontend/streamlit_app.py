import streamlit as st
import requests
import json
import os
from typing import Dict, Any, List
import time

# Configure page
st.set_page_config(
    page_title="Document-Aware AI Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .summary-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    
    .question-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    
    .answer-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .challenge-question {
        background: #e2e3f0;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .score-display {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .score-excellent { background: #d4edda; color: #155724; }
    .score-good { background: #fff3cd; color: #856404; }
    .score-fair { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'document_summary' not in st.session_state:
        st.session_state.document_summary = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    if 'challenge_questions' not in st.session_state:
        st.session_state.challenge_questions = None
    if 'current_question_id' not in st.session_state:
        st.session_state.current_question_id = 0
    if 'question_scores' not in st.session_state:
        st.session_state.question_scores = {}
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def upload_document(file):
    """Upload document to backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        return None

def ask_question(session_id: str, question: str):
    """Ask a question to the assistant"""
    try:
        payload = {"session_id": session_id, "question": question}
        response = requests.post(f"{API_BASE_URL}/ask", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Question failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error asking question: {str(e)}")
        return None

def generate_challenge(session_id: str):
    """Generate challenge questions"""
    try:
        response = requests.post(f"{API_BASE_URL}/challenge", params={"session_id": session_id})
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Challenge generation failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error generating challenge: {str(e)}")
        return None

def evaluate_answer(session_id: str, question_id: int, answer: str):
    """Evaluate user's answer"""
    try:
        payload = {"session_id": session_id, "question_id": question_id, "answer": answer}
        response = requests.post(f"{API_BASE_URL}/evaluate", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Evaluation failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error evaluating answer: {str(e)}")
        return None

def display_score(score: int):
    """Display score with color coding"""
    if score >= 80:
        css_class = "score-excellent"
        emoji = "🎉"
    elif score >= 60:
        css_class = "score-good"
        emoji = "👍"
    else:
        css_class = "score-fair"
        emoji = "📚"
    
    st.markdown(f"""
    <div class="score-display {css_class}">
        {emoji} Score: {score}/100
    </div>
    """, unsafe_allow_html=True)

def render_home_page():
    """Render the home page"""
    st.markdown('<h1 class="main-header">📄 Document-Aware AI Assistant</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 What can this assistant do?</h3>
        <ul>
            <li><strong>Document Upload:</strong> Support for PDF and TXT files</li>
            <li><strong>Instant Summary:</strong> Get a concise summary (≤150 words) immediately</li>
            <li><strong>Ask Anything:</strong> Free-form questions with contextual answers</li>
            <li><strong>Challenge Mode:</strong> Test your understanding with AI-generated questions</li>
            <li><strong>Grounded Responses:</strong> All answers backed by document references</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📁 Upload Your Document")
    st.markdown("Choose a PDF or TXT file to get started:")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt'],
        help="Upload a structured document like a research paper, report, or manual"
    )
    
    if uploaded_file is not None:
        st.success(f"File selected: {uploaded_file.name}")
        
        if st.button("🚀 Process Document", type="primary"):
            with st.spinner("Processing document... This may take a moment."):
                result = upload_document(uploaded_file)
                
                if result:
                    st.session_state.session_id = result["session_id"]
                    st.session_state.document_summary = result["summary"]
                    st.session_state.filename = uploaded_file.name
                    st.success("Document processed successfully!")
                    st.rerun()

def render_document_interface():
    """Render the main document interface"""
    st.markdown(f'<h1 class="main-header">📄 {st.session_state.filename}</h1>', unsafe_allow_html=True)
    
    # Display document summary
    st.markdown("### 📋 Document Summary")
    st.markdown(f"""
    <div class="summary-box">
        <p>{st.session_state.document_summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["🤔 Ask Anything", "🎯 Challenge Me"])
    
    with tab1:
        render_ask_anything()
    
    with tab2:
        render_challenge_mode()
    
    # Sidebar with session info
    with st.sidebar:
        st.markdown("### 📊 Session Info")
        st.markdown(f"**File:** {st.session_state.filename}")
        st.markdown(f"**Session ID:** {st.session_state.session_id[:8]}...")
        
        if st.button("🔄 Upload New Document"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def render_ask_anything():
    """Render the Ask Anything interface"""
    st.markdown("### 💬 Ask Questions About Your Document")
    st.markdown("Ask any question about the document content. The assistant will provide grounded answers with references.")
    
    # Question input
    question = st.text_input(
        "Your question:",
        placeholder="e.g., What are the main findings? How does X relate to Y?",
        key="question_input"
    )
    
    if st.button("🔍 Ask", type="primary", disabled=not question):
        if question:
            with st.spinner("Searching document and generating answer..."):
                response = ask_question(st.session_state.session_id, question)
                
                if response:
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        "question": question,
                        "answer": response["answer"],
                        "source": response["source"],
                        "confidence": response["confidence"]
                    })
                    
                    # Clear input
                    st.session_state.question_input = ""
                    st.rerun()
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("### 📜 Conversation History")
        
        for i, conv in enumerate(reversed(st.session_state.conversation_history)):
            st.markdown(f"""
            <div class="question-box">
                <strong>Q:</strong> {conv['question']}
            </div>
            <div class="answer-box">
                <strong>A:</strong> {conv['answer']}<br>
                <small><strong>Source:</strong> {conv['source']} | <strong>Confidence:</strong> {conv['confidence']:.2f}</small>
            </div>
            """, unsafe_allow_html=True)

def render_challenge_mode():
    """Render the Challenge Mode interface"""
    st.markdown("### 🎯 Challenge Your Understanding")
    st.markdown("Test your comprehension with AI-generated questions based on the document.")
    
    # Generate challenge questions
    if st.session_state.challenge_questions is None:
        if st.button("🎲 Generate Challenge Questions", type="primary"):
            with st.spinner("Generating challenging questions..."):
                result = generate_challenge(st.session_state.session_id)
                
                if result:
                    st.session_state.challenge_questions = result["questions"]
                    st.session_state.current_question_id = 0
                    st.rerun()
    
    # Display challenge questions
    if st.session_state.challenge_questions:
        questions = st.session_state.challenge_questions
        
        st.markdown("### 📝 Challenge Questions")
        
        for i, question in enumerate(questions, 1):
            with st.expander(f"Question {i}: {question['question'][:50]}..."):
                st.markdown(f"""
                <div class="challenge-question">
                    <strong>Question {i}:</strong> {question['question']}
                </div>
                """, unsafe_allow_html=True)
                
                # Answer input
                answer_key = f"answer_{i}"
                user_answer = st.text_area(
                    f"Your answer for Question {i}:",
                    key=answer_key,
                    placeholder="Type your answer here..."
                )
                
                if st.button(f"Submit Answer {i}", key=f"submit_{i}"):
                    if user_answer:
                        with st.spinner("Evaluating your answer..."):
                            evaluation = evaluate_answer(
                                st.session_state.session_id,
                                i,
                                user_answer
                            )
                            
                            if evaluation:
                                st.session_state.question_scores[i] = evaluation
                                st.rerun()
                    else:
                        st.warning("Please provide an answer before submitting.")
                
                # Display evaluation if available
                if i in st.session_state.question_scores:
                    eval_data = st.session_state.question_scores[i]
                    
                    display_score(eval_data["score"])
                    
                    st.markdown("**Feedback:**")
                    st.info(eval_data["feedback"])
                    
                    st.markdown("**Correct Answer:**")
                    st.success(eval_data["correct_answer"])
                    
                    st.markdown("**Document Reference:**")
                    st.caption(eval_data["source"])
        
        # Overall score
        if st.session_state.question_scores:
            total_score = sum(score["score"] for score in st.session_state.question_scores.values())
            avg_score = total_score / len(st.session_state.question_scores)
            
            st.markdown("### 🏆 Your Performance")
            display_score(int(avg_score))
            st.markdown(f"**Questions Completed:** {len(st.session_state.question_scores)}/{len(questions)}")
            
            if st.button("🎲 Generate New Challenge", type="secondary"):
                st.session_state.challenge_questions = None
                st.session_state.question_scores = {}
                st.rerun()

def main():
    """Main application"""
    initialize_session_state()
    
    # Check if document is uploaded
    if st.session_state.session_id is None:
        render_home_page()
    else:
        render_document_interface()

if __name__ == "__main__":
    main()