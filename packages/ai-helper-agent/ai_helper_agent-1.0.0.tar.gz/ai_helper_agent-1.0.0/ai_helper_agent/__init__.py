"""
AI Helper Agent - Interactive AI Assistant for Code Analysis
"""

from .core import InteractiveAgent, create_agent
from .utils import validate_python_code, run_python_code, format_code_output
from .config import config

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "InteractiveAgent",
    "create_agent",
    "validate_python_code", 
    "run_python_code",
    "format_code_output",
    "config"
]

# Package metadata
__title__ = "ai-helper-agent"
__description__ = "Interactive AI Helper Agent for code assistance, analysis, and bug fixing"
__url__ = "https://github.com/yourusername/ai-helper-agent"
__license__ = "MIT"