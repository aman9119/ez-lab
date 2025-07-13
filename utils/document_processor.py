import os
import re
from typing import List, Dict
from pathlib import Path
import PyPDF2
import tiktoken
from sentence_transformers import SentenceTransformer
import numpy as np
from .config import settings

class DocumentChunk:
    """Represents a chunk of text from a document"""
    def __init__(self, content: str, page_number: int = None, start_pos: int = None, end_pos: int = None):
        self.content = content
        self.page_number = page_number
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.embedding = None
        
    def to_dict(self):
        return {
            "content": self.content,
            "page_number": self.page_number,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos
        }

class DocumentProcessor:
    """Handles document processing, chunking, and vectorization"""
    
    def __init__(self):
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def process_document(self, file_path: str) -> List[DocumentChunk]:
        """Process a document and return chunks"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            text = self._extract_text_from_pdf(file_path)
        elif file_extension == '.txt':
            text = self._extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Clean and preprocess text
        text = self._clean_text(text)
        
        # Create chunks
        chunks = self._create_chunks(text)
        
        # Generate embeddings
        self._generate_embeddings(chunks)
        
        return chunks
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', '', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _create_chunks(self, text: str) -> List[DocumentChunk]:
        """Split text into chunks with overlap"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        current_tokens = 0
        start_pos = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = len(self.tokenizer.encode(paragraph))
            
            # If adding this paragraph would exceed chunk size, finalize current chunk
            if current_tokens + paragraph_tokens > settings.CHUNK_SIZE and current_chunk:
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    start_pos=start_pos,
                    end_pos=start_pos + len(current_chunk)
                ))
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, settings.CHUNK_OVERLAP)
                current_chunk = overlap_text + " " + paragraph
                current_tokens = len(self.tokenizer.encode(current_chunk))
                start_pos = start_pos + len(current_chunk) - len(overlap_text)
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_tokens += paragraph_tokens
        
        # Add the last chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                start_pos=start_pos,
                end_pos=start_pos + len(current_chunk)
            ))
        
        return chunks
    
    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """Get overlap text from the end of a chunk"""
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= overlap_tokens:
            return text
        
        overlap_tokens_list = tokens[-overlap_tokens:]
        return self.tokenizer.decode(overlap_tokens_list)
    
    def _generate_embeddings(self, chunks: List[DocumentChunk]):
        """Generate embeddings for all chunks"""
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
    
    def find_relevant_chunks(self, chunks: List[DocumentChunk], query: str, top_k: int = 5) -> List[DocumentChunk]:
        """Find most relevant chunks for a query"""
        query_embedding = self.embedding_model.encode([query])
        
        similarities = []
        for chunk in chunks:
            similarity = np.dot(query_embedding[0], chunk.embedding) / (
                np.linalg.norm(query_embedding[0]) * np.linalg.norm(chunk.embedding)
            )
            similarities.append((chunk, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in similarities[:top_k]]
    
    def get_chunk_context(self, chunks: List[DocumentChunk], target_chunk: DocumentChunk, context_size: int = 2) -> str:
        """Get surrounding context for a chunk"""
        target_index = chunks.index(target_chunk)
        
        start_index = max(0, target_index - context_size)
        end_index = min(len(chunks), target_index + context_size + 1)
        
        context_chunks = chunks[start_index:end_index]
        return "\n\n".join([chunk.content for chunk in context_chunks])