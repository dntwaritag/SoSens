#!/usr/bin/env python3
'''
Run script for FastAPI application
'''

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )