
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

def json_formatter(json_string: str) -> str:
    """
    Format and validate JSON
    
    Args:
        json_string: JSON string to format
        
    Returns:
        str: Formatted JSON or error message
    """
    try:
        import json
        
        # Parse JSON
        data = json.loads(json_string)
        
        # Format with indentation
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Add some statistics
        def count_items(obj, item_type="items"):
            if isinstance(obj, dict):
                return len(obj)
            elif isinstance(obj, list):
                return len(obj)
            else:
                return 1
        
        stats = f"JSON Statistics:\n- Type: {type(data).__name__}\n- Items: {count_items(data)}"
        
        return f"{stats}\n\nFormatted JSON:\n```json\n{formatted}\n```"
        
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format - {str(e)}"
    except Exception as e:
        logger.error(f"JSON formatter error: {e}")
        return f"Error formatting JSON: {str(e)}"
