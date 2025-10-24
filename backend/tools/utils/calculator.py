
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
