"""
Custom Tools for Google ADK Integration
Provides fallback implementations and custom tools
"""

import re
import ast
import operator
import requests
from typing import Dict, Any, List
from loguru import logger


def google_search(query: str, num_results: int = 5) -> str:
    """
    Custom Google Search tool (fallback implementation)
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        str: Formatted search results
    """
    try:
        # This is a mock implementation - in production you'd use actual search API
        logger.info(f"Performing Google search for: {query}")
        
        # Mock search results
        results = [
            {
                "title": f"Search Result {i+1} for '{query}'",
                "snippet": f"This is a mock search result snippet for query '{query}'. It contains relevant information about the topic.",
                "url": f"https://example.com/result-{i+1}",
                "source": f"example{i+1}.com"
            }
            for i in range(min(num_results, 5))
        ]
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. **{result['title']}**\n"
                f"   {result['snippet']}\n"
                f"   Source: {result['source']}\n"
                f"   URL: {result['url']}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error in google_search: {e}")
        return f"Error performing search: {str(e)}"


def custom_calculator(expression: str) -> str:
    """
    Safe calculator for mathematical expressions
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        str: Calculation result or error message
    """
    try:
        # Define allowed operators and functions
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        allowed_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
        }
        
        def safe_eval(node):
            if isinstance(node, ast.Constant):  # Numbers
                return node.value
            elif isinstance(node, ast.BinOp):  # Binary operations
                left = safe_eval(node.left)
                right = safe_eval(node.right)
                op = allowed_operators.get(type(node.op))
                if op:
                    return op(left, right)
                else:
                    raise ValueError(f"Unsupported operation: {type(node.op)}")
            elif isinstance(node, ast.UnaryOp):  # Unary operations
                operand = safe_eval(node.operand)
                op = allowed_operators.get(type(node.op))
                if op:
                    return op(operand)
                else:
                    raise ValueError(f"Unsupported unary operation: {type(node.op)}")
            elif isinstance(node, ast.Call):  # Function calls
                func_name = node.func.id
                if func_name in allowed_functions:
                    args = [safe_eval(arg) for arg in node.args]
                    return allowed_functions[func_name](*args)
                else:
                    raise ValueError(f"Unsupported function: {func_name}")
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")
        
        # Clean the expression
        expression = expression.strip()
        
        # Parse and evaluate
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree.body)
        
        logger.info(f"Calculator: {expression} = {result}")
        return f"Result: {result}"
        
    except ZeroDivisionError:
        return "Error: Division by zero"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return f"Error: Invalid expression - {str(e)}"


def text_analyzer(text: str) -> str:
    """
    Analyze text for various metrics
    
    Args:
        text: Text to analyze
        
    Returns:
        str: Analysis results
    """
    try:
        if not text or not text.strip():
            return "Error: No text provided for analysis"
        
        # Basic metrics
        word_count = len(text.split())
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        sentence_count = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Average metrics
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        avg_chars_per_word = char_count_no_spaces / max(word_count, 1)
        
        # Simple sentiment analysis (basic keyword approach)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'joy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'disappointed']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        # Reading time estimate (average 200 words per minute)
        reading_time_minutes = word_count / 200
        
        # Most common words (simple approach)
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only count words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Format results
        analysis = f"""Text Analysis Results:
        
📊 **Basic Metrics:**
- Words: {word_count:,}
- Characters: {char_count:,} (with spaces), {char_count_no_spaces:,} (without spaces)
- Sentences: {sentence_count}
- Paragraphs: {paragraph_count}

📈 **Averages:**
- Words per sentence: {avg_words_per_sentence:.1f}
- Characters per word: {avg_chars_per_word:.1f}

😊 **Sentiment Analysis:**
- Overall sentiment: {sentiment}
- Positive indicators: {positive_count}
- Negative indicators: {negative_count}

⏱️ **Reading Time:**
- Estimated reading time: {reading_time_minutes:.1f} minutes

🔤 **Most Common Words:**"""

        for word, count in top_words:
            analysis += f"\n- {word}: {count} times"
        
        logger.info(f"Analyzed text with {word_count} words")
        return analysis
        
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        return f"Error analyzing text: {str(e)}"


def web_scraper(url: str, max_length: int = 1000) -> str:
    """
    Simple web scraper tool
    
    Args:
        url: URL to scrape
        max_length: Maximum length of content to return
        
    Returns:
        str: Scraped content or error message
    """
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return "Error: Invalid URL format. Must start with http:// or https://"
        
        # Make request with timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simple text extraction (in production, use BeautifulSoup)
        content = response.text
        
        # Basic HTML tag removal
        import re
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        logger.info(f"Scraped {len(content)} characters from {url}")
        return f"Content from {url}:\n\n{content}"
        
    except requests.exceptions.Timeout:
        return "Error: Request timeout - the website took too long to respond"
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to fetch URL - {str(e)}"
    except Exception as e:
        logger.error(f"Web scraper error: {e}")
        return f"Error scraping website: {str(e)}"


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
