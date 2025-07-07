#!/usr/bin/env python3
"""
Startup script for School Management System development server
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Set environment variables for development
    os.environ.setdefault("ENV", "development")
    os.environ.setdefault("DEBUG", "true")
    
    # Run the development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
