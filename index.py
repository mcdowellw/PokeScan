"""
Vercel serverless function entry point for Pokemon TCG Scanner
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import your working scanner
from scanner_with_search import app

# Export for Vercel
def handler(request):
    """Vercel serverless handler"""
    return app

# Default export for Vercel
app = app