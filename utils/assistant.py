import json
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .document_processor import DocumentProcessor, DocumentChunk
from .config import settings

class DocumentAssistant:
    """Main assistant class that handles all AI interactions"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.document_processor = DocumentProcessor()
        self.sessions = {}  # Store session data
        
    def initialize_session(self, session_id: str, chunks: List[DocumentChunk], filename: str):
        """Initialize a new session with document chunks"""
        self.sessions[session_id] = {
            "chunks": chunks,
            "filename": filename,
            "challenge_questions": None,
            "conversation_history": []
        }
    
    def generate_summary(self, session_id: str) -> str:
        """Generate a concise summary of the document (≤ 150 words)"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        chunks = self.sessions[session_id]["chunks"]
        
        # Get representative chunks (first few and some from middle/end)
        summary_chunks = []
        total_chunks = len(chunks)
        
        if total_chunks <= 5:
            summary_chunks = chunks
        else:
            # Take first 2, middle 2, and last 2
            summary_chunks.extend(chunks[:2])
            mid_start = total_chunks // 2 - 1
            summary_chunks.extend(chunks[mid_start:mid_start + 2])
            summary_chunks.extend(chunks[-2:])
        
        # Combine chunks for summary
        combined_text = "\n\n".join([chunk.content for chunk in summary_chunks])
        
        prompt = f"""
        Please provide a concise summary of this document in exactly {settings.SUMMARY_MAX_WORDS} words or fewer.
        Focus on the main topics, key findings, and important conclusions.
        
        Document content:
        {combined_text}
        
        Summary (≤ {settings.SUMMARY_MAX_WORDS} words):
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.SUMMARY_TEMPERATURE,
                max_tokens=200
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure word count
            words = summary.split()
            if len(words) > settings.SUMMARY_MAX_WORDS:
                summary = " ".join(words[:settings.SUMMARY_MAX_WORDS]) + "..."
            
            return summary
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def answer_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """Answer a free-form question about the document"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        chunks = self.sessions[session_id]["chunks"]
        
        # Find relevant chunks
        relevant_chunks = self.document_processor.find_relevant_chunks(chunks, question, top_k=3)
        
        # Prepare context
        context = "\n\n".join([f"Chunk {i+1}:\n{chunk.content}" for i, chunk in enumerate(relevant_chunks)])
        
        prompt = f"""
        Based on the following document excerpts, please answer the question accurately and concisely.
        
        Document excerpts:
        {context}
        
        Question: {question}
        
        Instructions:
        1. Answer based ONLY on the information provided in the document excerpts
        2. If the answer cannot be found in the excerpts, say "I cannot find this information in the provided document"
        3. Include a brief justification explaining which part of the document supports your answer
        4. Be specific and accurate
        
        Answer:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.QA_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Store in conversation history
            self.sessions[session_id]["conversation_history"].append({
                "question": question,
                "answer": answer,
                "relevant_chunks": [chunk.to_dict() for chunk in relevant_chunks]
            })
            
            return {
                "answer": answer,
                "source": f"Based on {len(relevant_chunks)} relevant sections from the document",
                "confidence": self._calculate_confidence(relevant_chunks, question)
            }
            
        except Exception as e:
            return {
                "answer": f"Error answering question: {str(e)}",
                "source": "Error",
                "confidence": 0.0
            }
    
    def generate_challenge_questions(self, session_id: str) -> List[Dict[str, Any]]:
        """Generate logic-based challenge questions"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        chunks = self.sessions[session_id]["chunks"]
        
        # Select diverse chunks for question generation
        selected_chunks = self._select_diverse_chunks(chunks, 5)
        combined_text = "\n\n".join([chunk.content for chunk in selected_chunks])
        
        prompt = f"""
        Based on the following document, create exactly {settings.CHALLENGE_QUESTIONS_COUNT} challenging questions that test comprehension and logical reasoning.
        
        Document content:
        {combined_text}
        
        Requirements for each question:
        1. Require deep understanding, not just surface-level reading
        2. Test logical reasoning, inference, or analysis
        3. Have clear, specific answers that can be found in the document
        4. Be challenging but fair
        5. Include questions that test cause-and-effect, comparison, or implication
        
        Format your response as a JSON array with this structure:
        [
          {{
            "id": 1,
            "question": "Your question here",
            "expected_answer": "The correct answer",
            "explanation": "Why this is the correct answer with document reference"
          }}
        ]
        
        Questions:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.CHALLENGE_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            questions = json.loads(content)
            
            # Store challenge questions in session
            self.sessions[session_id]["challenge_questions"] = questions
            
            return questions
            
        except json.JSONDecodeError:
            # Fallback: generate questions manually
            return self._generate_fallback_questions(combined_text)
        except Exception as e:
            return [{"id": 1, "question": f"Error generating questions: {str(e)}", "expected_answer": "Error", "explanation": "Error"}]
    
    def evaluate_answer(self, session_id: str, question_id: int, user_answer: str) -> Dict[str, Any]:
        """Evaluate user's answer to a challenge question"""
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        challenge_questions = self.sessions[session_id]["challenge_questions"]
        if not challenge_questions or question_id > len(challenge_questions):
            raise ValueError("Invalid question ID")
        
        question_data = challenge_questions[question_id - 1]
        chunks = self.sessions[session_id]["chunks"]
        
        # Find relevant chunks for this question
        relevant_chunks = self.document_processor.find_relevant_chunks(chunks, question_data["question"], top_k=3)
        context = "\n\n".join([chunk.content for chunk in relevant_chunks])
        
        prompt = f"""
        Evaluate the user's answer to the following question based on the document content.
        
        Document context:
        {context}
        
        Question: {question_data["question"]}
        Expected answer: {question_data["expected_answer"]}
        User's answer: {user_answer}
        
        Instructions:
        1. Score the answer from 0-100 based on accuracy and completeness
        2. Consider partial credit for partially correct answers
        3. Provide constructive feedback
        4. Reference specific parts of the document that support the correct answer
        
        Respond in JSON format:
        {{
          "score": 85,
          "feedback": "Your detailed feedback here",
          "correct_answer": "The complete correct answer",
          "document_reference": "Which part of the document supports this"
        }}
        
        Evaluation:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=settings.MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            evaluation = json.loads(content)
            
            return {
                "score": evaluation.get("score", 0),
                "feedback": evaluation.get("feedback", "No feedback available"),
                "correct_answer": evaluation.get("correct_answer", question_data["expected_answer"]),
                "source": evaluation.get("document_reference", "Document reference not available")
            }
            
        except json.JSONDecodeError:
            return {
                "score": 0,
                "feedback": "Error evaluating answer",
                "correct_answer": question_data["expected_answer"],
                "source": "Error processing evaluation"
            }
        except Exception as e:
            return {
                "score": 0,
                "feedback": f"Error evaluating answer: {str(e)}",
                "correct_answer": question_data["expected_answer"],
                "source": "Error"
            }
    
    def cleanup_session(self, session_id: str):
        """Clean up session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def _calculate_confidence(self, chunks: List[DocumentChunk], question: str) -> float:
        """Calculate confidence score based on chunk relevance"""
        if not chunks:
            return 0.0
        
        # Simple confidence calculation based on number of relevant chunks
        # and their content length
        base_confidence = min(0.8, len(chunks) * 0.2)
        
        # Adjust based on chunk content length
        avg_length = sum(len(chunk.content) for chunk in chunks) / len(chunks)
        length_factor = min(1.0, avg_length / 500)  # Normalize by expected chunk size
        
        return base_confidence * length_factor
    
    def _select_diverse_chunks(self, chunks: List[DocumentChunk], count: int) -> List[DocumentChunk]:
        """Select diverse chunks from the document"""
        if len(chunks) <= count:
            return chunks
        
        # Select chunks from different parts of the document
        selected = []
        step = len(chunks) // count
        
        for i in range(count):
            index = i * step
            if index < len(chunks):
                selected.append(chunks[index])
        
        return selected
    
    def _generate_fallback_questions(self, text: str) -> List[Dict[str, Any]]:
        """Generate fallback questions if JSON parsing fails"""
        return [
            {
                "id": 1,
                "question": "What is the main topic discussed in this document?",
                "expected_answer": "Please refer to the document content",
                "explanation": "This question tests basic comprehension of the document's main theme"
            },
            {
                "id": 2,
                "question": "What are the key findings or conclusions mentioned?",
                "expected_answer": "Please refer to the document content",
                "explanation": "This question tests understanding of important results or conclusions"
            },
            {
                "id": 3,
                "question": "How do the different sections of the document relate to each other?",
                "expected_answer": "Please refer to the document content",
                "explanation": "This question tests logical reasoning and document structure understanding"
            }
        ]