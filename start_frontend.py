#!/usr/bin/env python3
"""
Start the Document Assistant Frontend (Streamlit App)
"""

import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    try:
        frontend_path = Path(__file__).parent / "frontend" / "streamlit_app.py"
        
        print("🎨 Starting Document Assistant Frontend...")
        print("🌐 Frontend will be available at: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop the frontend")
        print("⚠️  Make sure the backend is running on http://localhost:8000")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_path),
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)