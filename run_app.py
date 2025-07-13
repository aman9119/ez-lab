#!/usr/bin/env python3
"""
Document-Aware AI Assistant Application Launcher
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    os.chdir(Path(__file__).parent / "backend")
    
    # Add parent directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    
    # Wait for backend to start
    time.sleep(3)
    
    frontend_path = Path(__file__).parent / "frontend" / "streamlit_app.py"
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_path),
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "streamlit", "PyPDF2", "openai", 
        "sentence-transformers", "tiktoken", "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_environment():
    """Check if environment is properly configured"""
    print("⚙️  Checking environment configuration...")
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("⚠️  No .env file found. Please create one based on .env.example")
        print("📝 Copy .env.example to .env and add your OpenAI API key")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured in .env file")
        print("🔑 Please add your OpenAI API key to the .env file")
        return False
    
    print("✅ Environment is properly configured!")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary directories...")
    
    base_path = Path(__file__).parent
    directories = ["uploads", "data", "data/vector_db"]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully!")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down application...")
    sys.exit(0)

def main():
    """Main application launcher"""
    print("=" * 60)
    print("📄 Document-Aware AI Assistant")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check dependencies and environment
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    print("\n🎉 Starting application...")
    print("📚 Backend will be available at: http://localhost:8000")
    print("🎨 Frontend will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the application")
    print("-" * 60)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Start frontend in main thread
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()