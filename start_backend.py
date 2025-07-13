#!/usr/bin/env python3
"""
Start the Document Assistant Backend API Server
"""

import sys
import os
from pathlib import Path

# Add the document_assistant directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Change to backend directory
os.chdir(Path(__file__).parent / "backend")

if __name__ == "__main__":
    try:
        import uvicorn
        print("🚀 Starting Document Assistant Backend API...")
        print("📚 API will be available at: http://localhost:8000")
        print("📖 API documentation: http://localhost:8000/docs")
        print("🔄 Press Ctrl+C to stop the server")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)