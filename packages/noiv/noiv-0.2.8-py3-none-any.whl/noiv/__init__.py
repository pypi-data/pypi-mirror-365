"""
NOIV - API Testing Tool with Built-in AI
"""

__version__ = "0.2.8"
__author__ = "Your Name"
__description__ = "API Testing Tool with Natural Language AI Generation"

def main_cli():
    """Entry point for the CLI"""
    from .cli import app
    app()
