from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import json
from datetime import datetime

from utils.document_processor import DocumentProcessor
from utils.assistant import DocumentAssistant
from utils.config import settings

app = FastAPI(title="Document-Aware AI Assistant", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
document_processor = DocumentProcessor()
assistant = DocumentAssistant()

# In-memory storage for sessions (in production, use Redis or database)
active_sessions = {}

class QuestionRequest(BaseModel):
    session_id: str
    question: str

class ChallengeAnswerRequest(BaseModel):
    session_id: str
    question_id: int
    answer: str

class SessionResponse(BaseModel):
    session_id: str
    summary: str
    status: str

@app.post("/upload", response_model=SessionResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF or TXT)"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session directory
        session_dir = os.path.join(settings.UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(session_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        chunks = document_processor.process_document(file_path)
        
        # Initialize assistant with document
        assistant.initialize_session(session_id, chunks, file.filename)
        
        # Generate summary
        summary = assistant.generate_summary(session_id)
        
        # Store session info
        active_sessions[session_id] = {
            "filename": file.filename,
            "upload_time": datetime.now().isoformat(),
            "chunks": len(chunks),
            "summary": summary
        }
        
        return SessionResponse(
            session_id=session_id,
            summary=summary,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Handle free-form questions about the document"""
    try:
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        response = assistant.answer_question(request.session_id, request.question)
        
        return {
            "answer": response["answer"],
            "source": response["source"],
            "confidence": response["confidence"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@app.post("/challenge")
async def generate_challenge(session_id: str):
    """Generate challenge questions for the user"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        questions = assistant.generate_challenge_questions(session_id)
        
        return {
            "questions": questions,
            "instructions": "Answer these questions based on the document content"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating challenge: {str(e)}")

@app.post("/evaluate")
async def evaluate_answer(request: ChallengeAnswerRequest):
    """Evaluate user's answer to a challenge question"""
    try:
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        evaluation = assistant.evaluate_answer(
            request.session_id, 
            request.question_id, 
            request.answer
        )
        
        return {
            "score": evaluation["score"],
            "feedback": evaluation["feedback"],
            "correct_answer": evaluation["correct_answer"],
            "source": evaluation["source"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {"sessions": list(active_sessions.keys())}

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and clean up resources"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up session data
    assistant.cleanup_session(session_id)
    del active_sessions[session_id]
    
    return {"message": "Session deleted successfully"}

@app.get("/")
async def root():
    return {"message": "Document-Aware AI Assistant API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)