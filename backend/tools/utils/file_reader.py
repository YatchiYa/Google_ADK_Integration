"""
Custom Tools for Google ADK Integration
Provides fallback implementations and custom tools
"""

import re
import ast
import operator
import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pytz
from loguru import logger 
import json


def file_reader(file_path: str, max_lines: int = 100) -> str:
    """
    Read and return file contents
    
    Args:
        file_path: Path to the file
        max_lines: Maximum number of lines to read
        
    Returns:
        str: File contents or error message
    """
    try:
        import os
        
        # Security check - only allow certain file types
        allowed_extensions = ['.txt', '.md', '.json', '.csv', '.log', '.py', '.js', '.html', '.css']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in allowed_extensions:
            return f"Error: File type '{file_ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found"
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Limit lines
        if len(lines) > max_lines:
            content = ''.join(lines[:max_lines])
            content += f"\n\n... (truncated, showing first {max_lines} lines of {len(lines)} total)"
        else:
            content = ''.join(lines)
        
        logger.info(f"Read {len(lines)} lines from {file_path}")
        return f"Contents of {file_path}:\n\n{content}"
        
    except UnicodeDecodeError:
        return "Error: File contains non-text content or unsupported encoding"
    except PermissionError:
        return "Error: Permission denied - cannot read file"
    except Exception as e:
        logger.error(f"File reader error: {e}")
        return f"Error reading file: {str(e)}"


