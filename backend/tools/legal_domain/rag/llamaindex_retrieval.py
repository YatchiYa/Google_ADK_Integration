

import requests
from typing import Dict, Any, List, Optional
from loguru import logger 
import json



def annuaire_de_lois_civile_algerien(query: str):
    """
    Query the Legal-Index semantic RAG API to retrieve relevant legal articles.

    Args:
        query (str): The user's legal question or topic.

    Returns:
        str: The extracted legal response text or an error message.
    """
    url = "https://legal-index.com/api/agent/tools/semantic_rag_search"

    payload = {
        "tool_type": "simple",
        "question": query,
        "collection_name": "code_civil"
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        logger.info(f"Response status code: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        logger.info(f"Response JSON keys: {list(data.keys())}")

        if data.get("status") == "success":
            result_text = data.get("data", "").strip()
            logger.info(f"Retrieved response length: {len(result_text)} characters")
            return result_text or "No data returned from API."
        else:
            logger.warning(f"API returned non-success status: {data}")
            return f"API returned non-success status: {data}"

    except requests.exceptions.RequestException as e:
        logger.error(f"Error while connecting to endpoint: {e}")
        return f"Error while connecting to endpoint: {e}"
    except json.JSONDecodeError:
        logger.error("Invalid JSON received from API.")
        return "Invalid JSON received from API."