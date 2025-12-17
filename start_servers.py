#!/usr/bin/env python3
"""
Quick start script for Smart Farming Fertilizer System
Starts both backend API and frontend Flask servers
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("=" * 70)
    print("🌱 Smart Farming Fertilizer Recommendation System")
    print("=" * 70)
    print()
    
    # Get the smartfarming directory
    smartfarming_dir = Path(__file__).parent
    backend_dir = smartfarming_dir / "backend"
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print("❌ Error: backend directory not found!")
        print(f"   Expected location: {backend_dir}")
        sys.exit(1)
    
    # Check if required files exist
    required_files = [
        backend_dir / "main.py",
        backend_dir / "predictor.py",
        smartfarming_dir / "app.py"
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print("❌ Error: Required files missing:")
        for f in missing_files:
            print(f"   - {f}")
        sys.exit(1)
    
    print("✓ All required files found")
    print()
    
    # Start backend API
    print("🚀 Starting Backend API Server (FastAPI)...")
    print(f"   Location: http://localhost:8000")
    print(f"   Docs: http://localhost:8000/docs")
    print()
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(smartfarming_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("✓ Backend API started")
        print()
        
        # Wait a bit for backend to start
        print("⏳ Waiting for backend to initialize...")
        time.sleep(3)
        print()
        
        # Start Flask frontend
        print("🚀 Starting Flask Frontend Server...")
        print(f"   Location: http://localhost:5000")
        print()
        
        frontend_cmd = [sys.executable, "app.py"]
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=str(smartfarming_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("✓ Frontend server started")
        print()
        
        print("=" * 70)
        print("✅ System is running!")
        print("=" * 70)
        print()
        print("Access the application at: http://localhost:5000")
        print("API documentation at: http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop all servers...")
        print()
        
        # Keep the script running and show output
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("🛑 Stopping servers...")
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for processes to end
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
            print("✓ All servers stopped")
            print()
            
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Install it with:")
        print("   pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
