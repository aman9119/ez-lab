import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Document Processing
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # File Storage
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Vector Database
    VECTOR_DB_PATH: Path = DATA_DIR / "vector_db"
    
    # Assistant Configuration
    SUMMARY_MAX_WORDS: int = int(os.getenv("SUMMARY_MAX_WORDS", "150"))
    CHALLENGE_QUESTIONS_COUNT: int = int(os.getenv("CHALLENGE_QUESTIONS_COUNT", "3"))
    
    # Temperature settings for different tasks
    SUMMARY_TEMPERATURE: float = float(os.getenv("SUMMARY_TEMPERATURE", "0.3"))
    QA_TEMPERATURE: float = float(os.getenv("QA_TEMPERATURE", "0.1"))
    CHALLENGE_TEMPERATURE: float = float(os.getenv("CHALLENGE_TEMPERATURE", "0.7"))
    
    def __init__(self):
        # Create directories if they don't exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        
        # Validate OpenAI API key
        if not self.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Please set it in your environment variables.")

settings = Settings()