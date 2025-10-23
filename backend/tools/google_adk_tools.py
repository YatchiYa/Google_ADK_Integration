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


def product_hunt_search(query: str, query_type: str = "search", first: int = 5) -> str:
    """
    Product Hunt API tool for retrieving information about products
    
    Args:
        query: Search query for products/posts
        query_type: Type of query (search, posts, collections)
        first: Number of items to return (max 20)
        
    Returns:
        str: Formatted product information
    """
    try:
        logger.info(f"Product Hunt {query_type} for: {query}")
        
        # Mock implementation - in production, use actual Product Hunt GraphQL API
        # You would need PRODUCT_HUNT_API_TOKEN environment variable
        
        if query_type == "search":
            results = [
                {
                    "name": f"AI Product {i+1}",
                    "tagline": f"Revolutionary AI tool for {query}",
                    "description": f"This product helps with {query} using advanced AI technology",
                    "url": f"https://www.producthunt.com/posts/ai-product-{i+1}",
                    "votes_count": 150 - (i * 10),
                    "topics": ["AI", "Productivity", "Developer Tools"]
                }
                for i in range(min(first, 5))
            ]
        elif query_type == "posts":
            results = [
                {
                    "name": f"Today's Product {i+1}",
                    "tagline": f"Featured product of the day",
                    "description": f"Top trending product in the {query} category",
                    "url": f"https://www.producthunt.com/posts/product-{i+1}",
                    "votes_count": 200 - (i * 15),
                    "topics": ["Featured", "Trending"]
                }
                for i in range(min(first, 5))
            ]
        else:
            return f"Unsupported query_type: {query_type}"
        
        # Format results
        formatted_results = []
        for product in results:
            formatted_results.append(
                f"• **{product['name']}**\n"
                f"  {product['tagline']}\n"
                f"  Topics: {', '.join(product['topics'])}\n"
                f"  Votes: {product['votes_count']}\n"
                f"  URL: {product['url']}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error in product_hunt_search: {e}")
        return f"Error searching Product Hunt: {str(e)}"


def yahoo_finance_data(symbol: str, interval: str = "5m", range_type: str = "today") -> str:
    """
    Yahoo Finance tool for retrieving financial data
    
    Args:
        symbol: Stock symbol (e.g., BTC-USD, AAPL, GOOGL)
        interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d)
        range_type: Type of date range (today, week, month, ytd)
        
    Returns:
        str: Formatted financial data
    """
    try:
        logger.info(f"Fetching Yahoo Finance data for {symbol} with {interval} interval")
        
        # Create Ticker object
        ticker = yf.Ticker(symbol)
        
        # Get date range
        ny_tz = pytz.timezone('America/New_York')
        now = datetime.now(ny_tz)
        
        if range_type == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_type == "week":
            start = now - timedelta(days=7)
            end = now
        elif range_type == "month":
            start = now - timedelta(days=30)
            end = now
        elif range_type == "ytd":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            start = now - timedelta(days=1)
            end = now
        
        # Get historical data
        hist = ticker.history(start=start, end=end, interval=interval)
        
        if hist.empty:
            return f"No data available for {symbol}"
        
        # Get stock info
        info = ticker.info
        
        # Format the data
        hist.index = hist.index.tz_convert('America/New_York')
        
        # Get latest data point
        latest = hist.iloc[-1]
        first = hist.iloc[0]
        
        # Calculate change
        price_change = latest['Close'] - first['Open']
        price_change_pct = (price_change / first['Open']) * 100
        
        result = f"""
**{symbol} - {info.get('shortName', symbol)}**

**Latest Data ({latest.name.strftime('%Y-%m-%d %H:%M:%S %Z')})**
- Open: ${latest['Open']:.2f}
- High: ${latest['High']:.2f}
- Low: ${latest['Low']:.2f}
- Close: ${latest['Close']:.2f}
- Volume: {int(latest['Volume']):,}

**Period Summary ({range_type})**
- Data Points: {len(hist)}
- Price Change: ${price_change:.2f} ({price_change_pct:+.2f}%)
- Period High: ${hist['High'].max():.2f}
- Period Low: ${hist['Low'].min():.2f}
- Avg Volume: {int(hist['Volume'].mean()):,}

**Stock Info**
- Exchange: {info.get('exchange', 'N/A')}
- Currency: {info.get('currency', 'N/A')}
- Sector: {info.get('sector', 'N/A')}
- Industry: {info.get('industry', 'N/A')}
"""
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error in yahoo_finance_data: {e}")
        return f"Error fetching Yahoo Finance data: {str(e)}"



def call_document_rag_code_civile_algerian(query: str, mode: str = "global", user_prompt: str = "expert in laws retrieving"):  
    """
    Search and retrieve information from the Algerian Civil Code using RAG.
    
    Args:
        query (str): The legal question or topic to search for
        mode (str): Search mode - "global" for comprehensive search
        user_prompt (str): Context for the search expert role
        
    Returns:
        str: Legal information and analysis from Algerian Civil Code
    """
    url = "http://0.0.0.0:9621/query/stream"

    payload = {
        "mode": mode,
        "response_type": "Multiple Paragraphs",
        "top_k": 40,
        "chunk_top_k": 20,
        "max_entity_tokens": 6000,
        "max_relation_tokens": 8000,
        "max_total_tokens": 30000,
        "only_need_context": False,
        "only_need_prompt": False,
        "stream": True,
        "history_turns": 0,
        "user_prompt": user_prompt,
        "enable_rerank": True,
        "query": query,
        "conversation_history": []
    }

    headers = {"Content-Type": "application/json"}

    try:
        with requests.post(url, headers=headers, data=json.dumps(payload), stream=True, timeout=120) as response:
            logger.info(f"Response status code: {response.status_code}")
            response.raise_for_status()
            full_text = ""
            
            for line in response.iter_lines():
                if line:
                    # Decode bytes to string if necessary
                    if isinstance(line, bytes):
                        line_str = line.decode('utf-8')
                    else:
                        line_str = str(line)
                    
                    logger.info(f"Response line: {line_str}")
                    full_text += line_str + "\n"
            
            result = full_text.strip()
            logger.info(f"Final response length: {len(result)} characters")
            
            # Try to parse JSON response and extract the actual content
            try:
                json_response = json.loads(result)
                if isinstance(json_response, dict):
                    if 'response' in json_response:
                        actual_response = json_response['response']
                        references = json_response.get('references', [])
                        
                        # Format the response with references if available
                        formatted_response = actual_response
                        if references:
                            formatted_response += "\n\nReferences:\n"
                            for i, ref in enumerate(references, 1):
                                formatted_response += f"{i}. {ref}\n"
                        
                        logger.info(f"Parsed JSON response successfully")
                        return formatted_response
                    else:
                        logger.info(f"JSON response doesn't contain 'response' field")
                        return result
                else:
                    logger.info(f"Response is not a JSON object")
                    return result
            except json.JSONDecodeError:
                logger.info(f"Response is not valid JSON, returning as-is")
                return result
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while connecting to endpoint: {e}")
        return f"Error while connecting to endpoint: {e}"
