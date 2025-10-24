
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

import asyncio
import aiohttp


url = "https://legal-index.com/light_rag/query/stream"
user_prompt = """
    ⚖️ Rôle et objectif
        Vous êtes un assistant juridique spécialisé dans le droit algérien.
        Votre mission est d’identifier et de restituer les articles de loi, codes, ordonnances ou décrets officiels du droit algérien qui répondent le plus précisément à la question de l’utilisateur.

        📚 Sources
        Votre base documentaire contient exclusivement des textes juridiques officiels : Code civil, Code pénal, Code de commerce, Code du travail, Code de la famille, ainsi que d’autres lois, ordonnances et décrets en vigueur en Algérie.

        🧠 Instructions de recherche

        Recherchez les articles de loi exacts qui définissent, régissent ou encadrent la situation décrite dans la question.

        Incluez également les articles complémentaires, interprétatifs ou restrictifs qui pourraient éclairer le sujet.

        Évitez les documents hors du champ juridique ou qui ne présentent qu’une ressemblance lexicale.

        Ne modifiez, ne résumez et n’interprétez jamais le texte juridique.

        Restituez l’intégralité du contenu de l’article, tel qu’il apparaît dans la base de données (sans omission ni reformulation).

        📄 Format de restitution attendu
        Pour chaque résultat pertinent, indiquez :

        Le titre de la source (ex. : Code civil).

        Le numéro de l’article.

        Le texte complet de l’article, sans aucune altération.

        🔍 Critères de pertinence

        La correspondance juridique avec la question est prioritaire sur la similarité de mots.

        Les articles les plus spécifiques et applicables doivent être classés en premier.

        🗣️ Question de l’utilisateur :
        {user_query}
    """

def annuaire_du_code_algerien(query: str):  
    """
    Search and retrieve information from the Algerian Civil Code using RAG.
    
    Args:
        query (str): The legal question or topic to search for
        
    Returns:
        str: Legal information and analysis from Algerian Civil Code
    """
    
    payload = {
        "mode": "global",
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

async def annuaire_du_code_algerien_avancee(
    query: str,  
) -> str:
    """
    ASYNC VERSION: Search and retrieve information from the Algerian Civil Code using RAG.
    This is an async tool that collects streaming chunks and returns the complete result.
    Note: ADK doesn't support AsyncGenerator for regular tools, only for live video/audio streaming.
    
    Args:
        query (str): The legal question or topic to search for
        
    Returns:
        str: Complete legal information from Algerian Civil Code
    """ 

    payload = {
        "mode": "global",
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                logger.info(f"[ASYNC STREAMING] Response status code: {response.status}")
                response.raise_for_status()
                
                references = []
                response_text = ""
                
                # Collect all chunks from stream
                async for line in response.content:
                    if line:
                        # Decode bytes to string
                        line_str = line.decode('utf-8').strip()
                        
                        if not line_str:
                            continue
                        
                        try:
                            # Parse each JSON line
                            json_line = json.loads(line_str)
                            
                            # Handle references (usually comes first)
                            if 'references' in json_line:
                                references = json_line['references']
                                logger.info(f"[ASYNC STREAMING] Received {len(references)} references")
                            
                            # Handle response chunks - accumulate them
                            if 'response' in json_line:
                                chunk = json_line['response']
                                response_text += chunk
                                logger.debug(f"[ASYNC STREAMING] Accumulated chunk: {len(response_text)} chars total")
                        
                        except json.JSONDecodeError:
                            logger.warning(f"[ASYNC STREAMING] Could not parse line as JSON: {line_str[:100]}")
                            continue
                
                # Format final response with references
                final_response = response_text
                if references:
                    final_response += "\n\n📚 References:\n"
                    for i, ref in enumerate(references, 1):
                        final_response += f"{i}. {ref}\n"
                
                logger.info(f"[ASYNC STREAMING] Completed. Total response length: {len(final_response)} characters")
                return final_response
                
    except Exception as e:
        logger.error(f"[ASYNC STREAMING] Error while connecting to endpoint: {e}")
        return f"❌ Error while connecting to legal database: {str(e)}"

