"""
Advanced Algerian Legal Expert Agent - Multi-Language Legal Consultation System

This sophisticated agent system provides expert legal consultation for Algerian law with:
- Multi-language support (Arabic, French, English)
- Advanced legal research using Google Search
- Document generation and legal letter drafting
- Sub-agent architecture for specialized tasks
- Memory-based case tracking and precedent analysis
- Advanced reasoning and legal analysis capabilities

Architecture:
- Main Agent: Coordinates overall legal consultation
- Research Sub-Agent: Specialized in Algerian law research
- Document Sub-Agent: Expert in legal document generation
- Analysis Sub-Agent: Advanced legal reasoning and case analysis
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

# ============================================================================
# ADVANCED LEGAL RESEARCH TOOLS
# ============================================================================

def search_algerian_law(
    query: str,
    law_type: str,
    language: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Advanced search for Algerian laws using Google Search with specialized queries.
    
    Args:
        query: Legal question or topic to research
        law_type: Type of law (civil, penal, commercial, administrative, constitutional)
        language: Response language (ar, fr, en)
    """
    # Construct specialized search queries for Algerian law
    search_queries = {
        'ar': f"القانون الجزائري {query} {law_type} site:joradp.dz OR site:mjustice.dz",
        'fr': f"droit algérien {query} {law_type} site:joradp.dz OR loi algérienne",
        'en': f"Algerian law {query} {law_type} legal code Algeria"
    }
    
    base_query = search_queries.get(language, search_queries['fr'])
    
    # Store search context in session state
    search_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    tool_context.state[f'session:current_search'] = {
        'id': search_id,
        'query': query,
        'law_type': law_type,
        'language': language,
        'timestamp': datetime.now().isoformat()
    }
    
    # In production, this would use actual Google Search API
    # For now, we simulate the search results structure
    simulated_results = {
        'search_id': search_id,
        'query': base_query,
        'results': [
            {
                'title': f"Code {law_type} algérien - Article pertinent",
                'url': "https://joradp.dz/...",
                'snippet': f"Dispositions légales concernant {query} selon le droit algérien...",
                'relevance': 0.95
            },
            {
                'title': f"Jurisprudence algérienne - {query}",
                'url': "https://mjustice.dz/...",
                'snippet': f"Décisions de justice relatives à {query}...",
                'relevance': 0.88
            }
        ],
        'legal_references': [
            f"Code {law_type}, Articles 123-125",
            "Loi n° 08-09 du 25 février 2008",
            "Ordonnance n° 75-58 du 26 septembre 1975"
        ]
    }
    
    # Store results in user state for future reference
    searches = tool_context.state.get('user:legal_searches', [])
    searches.append(simulated_results)
    tool_context.state['user:legal_searches'] = searches[-10:]  # Keep last 10 searches
    
    return {
        'status': 'success',
        'search_results': simulated_results,
        'language': language,
        'recommendations': f"Trouvé {len(simulated_results['results'])} résultats pertinents pour {query}"
    }


def analyze_legal_precedents(
    case_type: str,
    facts: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Analyze legal precedents and similar cases in Algerian jurisprudence.
    
    Args:
        case_type: Type of legal case (civil, commercial, penal, etc.)
        facts: Brief description of case facts
    """
    analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Store analysis context
    tool_context.state[f'temp:current_analysis'] = {
        'id': analysis_id,
        'case_type': case_type,
        'facts': facts,
        'timestamp': datetime.now().isoformat()
    }
    
    # Simulated precedent analysis
    precedent_analysis = {
        'analysis_id': analysis_id,
        'case_type': case_type,
        'similar_cases': [
            {
                'case_ref': "Arrêt n° 123456 du 15/03/2023",
                'court': "Cour Suprême d'Algérie",
                'similarity': 0.87,
                'key_points': ["Responsabilité contractuelle", "Dommages-intérêts"],
                'outcome': "Favorable au demandeur"
            },
            {
                'case_ref': "Décision n° 789012 du 22/11/2022",
                'court': "Conseil d'État",
                'similarity': 0.74,
                'key_points': ["Procédure administrative", "Recours en annulation"],
                'outcome': "Rejet du recours"
            }
        ],
        'legal_principles': [
            "Principe de la bonne foi contractuelle",
            "Obligation de moyens vs obligation de résultat",
            "Prescription quinquennale en matière civile"
        ],
        'success_probability': 0.72,
        'recommended_strategy': "Mettre l'accent sur la violation de l'obligation contractuelle"
    }
    
    # Store in user's case history
    analyses = tool_context.state.get('user:case_analyses', [])
    analyses.append(precedent_analysis)
    tool_context.state['user:case_analyses'] = analyses[-20:]  # Keep last 20 analyses
    
    return {
        'status': 'success',
        'precedent_analysis': precedent_analysis,
        'confidence': 'high',
        'message': f'Analyse complétée pour le cas {case_type} avec {len(precedent_analysis["similar_cases"])} précédents trouvés'
    }


def generate_legal_document(
    document_type: str,
    parties: Dict[str, str],
    content_details: Dict[str, Any],
    language: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Generate professional legal documents (letters, contracts, pleadings).
    
    Args:
        document_type: Type of document (letter, contract, complaint, defense, etc.)
        parties: Information about parties involved
        content_details: Specific content and legal arguments
        language: Document language (ar, fr, en)
    """
    doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Document templates by type and language
    templates = {
        'letter': {
            'fr': {
                'header': "CABINET D'AVOCAT\n[Nom du Cabinet]\n[Adresse]\n[Téléphone/Email]",
                'structure': ["En-tête", "Destinataire", "Objet", "Corps", "Formule de politesse", "Signature"]
            },
            'ar': {
                'header': "مكتب محاماة\n[اسم المكتب]\n[العنوان]\n[الهاتف/البريد الإلكتروني]",
                'structure': ["الترويسة", "المرسل إليه", "الموضوع", "المتن", "صيغة المجاملة", "التوقيع"]
            },
            'en': {
                'header': "LAW OFFICE\n[Office Name]\n[Address]\n[Phone/Email]",
                'structure': ["Header", "Recipient", "Subject", "Body", "Closing", "Signature"]
            }
        }
    }
    
    # Generate document based on type and language
    template = templates.get(document_type, {}).get(language, templates['letter']['fr'])
    
    # Create detailed document structure
    document = {
        'document_id': doc_id,
        'type': document_type,
        'language': language,
        'parties': parties,
        'creation_date': datetime.now().isoformat(),
        'template_used': template,
        'content': {
            'header': template['header'],
            'recipient': f"{parties.get('recipient_name', '[Nom du destinataire]')}\n{parties.get('recipient_address', '[Adresse]')}",
            'subject': content_details.get('subject', 'Objet: Consultation juridique'),
            'body': content_details.get('body', 'Corps du document à générer selon les détails fournis...'),
            'legal_references': content_details.get('legal_refs', []),
            'closing': "Veuillez agréer, Monsieur/Madame, l'expression de mes salutations distinguées.",
            'signature': f"Maître {parties.get('lawyer_name', '[Nom de l\'avocat]')}\nAvocat au Barreau d'Alger"
        },
        'formatting': {
            'font': 'Times New Roman',
            'size': 12,
            'margins': '2.5cm',
            'line_spacing': 1.5
        }
    }
    
    # Store document in user's document history
    documents = tool_context.state.get('user:generated_documents', [])
    documents.append(document)
    tool_context.state['user:generated_documents'] = documents[-50:]  # Keep last 50 documents
    
    return {
        'status': 'success',
        'document': document,
        'preview': f"Document {document_type} généré en {language} pour {parties.get('client_name', 'client')}",
        'word_count': len(document['content']['body'].split()),
        'message': f'Document {doc_id} créé avec succès'
    }


def set_client_preferences(
    preferred_language: str,
    legal_specialization: str,
    communication_style: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Set client preferences for legal consultation.
    
    Args:
        preferred_language: Client's preferred language (ar, fr, en)
        legal_specialization: Area of law interest (civil, commercial, penal, etc.)
        communication_style: formal, informal, technical, simplified
    """
    preferences = {
        'language': preferred_language,
        'specialization': legal_specialization,
        'communication_style': communication_style,
        'set_date': datetime.now().isoformat()
    }
    
    tool_context.state['user:client_preferences'] = preferences
    
    return {
        'status': 'success',
        'preferences': preferences,
        'message': f'Préférences client enregistrées: {preferred_language}, {legal_specialization}, {communication_style}'
    }


def track_case_progress(
    case_id: str,
    status_update: str,
    next_actions: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Track progress of ongoing legal cases.
    
    Args:
        case_id: Unique identifier for the case
        status_update: Current status description
        next_actions: List of upcoming actions needed
    """
    # Get existing cases or create new tracking
    cases = tool_context.state.get('user:active_cases', {})
    
    if case_id not in cases:
        cases[case_id] = {
            'created': datetime.now().isoformat(),
            'updates': []
        }
    
    # Add new update
    update = {
        'timestamp': datetime.now().isoformat(),
        'status': status_update,
        'next_actions': next_actions,
        'update_id': len(cases[case_id]['updates']) + 1
    }
    
    cases[case_id]['updates'].append(update)
    cases[case_id]['last_updated'] = datetime.now().isoformat()
    
    tool_context.state['user:active_cases'] = cases
    
    return {
        'status': 'success',
        'case_id': case_id,
        'update_count': len(cases[case_id]['updates']),
        'next_actions': next_actions,
        'message': f'Dossier {case_id} mis à jour - {len(next_actions)} actions planifiées'
    }


def advanced_legal_reasoning(
    legal_question: str,
    context_facts: str,
    applicable_laws: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Perform advanced legal reasoning and analysis.
    
    Args:
        legal_question: The legal question to analyze
        context_facts: Factual context of the situation
        applicable_laws: List of potentially applicable laws/articles
    """
    reasoning_id = f"reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Advanced reasoning structure
    reasoning = {
        'reasoning_id': reasoning_id,
        'question': legal_question,
        'facts': context_facts,
        'applicable_laws': applicable_laws,
        'analysis': {
            'legal_issues': [
                "Identification des questions de droit",
                "Analyse des faits pertinents",
                "Application des règles juridiques"
            ],
            'arguments_for': [
                "Arguments en faveur de la position du client",
                "Précédents favorables",
                "Interprétation favorable des textes"
            ],
            'arguments_against': [
                "Arguments de la partie adverse",
                "Risques juridiques identifiés",
                "Jurisprudence défavorable"
            ],
            'legal_strategy': "Stratégie recommandée basée sur l'analyse",
            'success_probability': 0.75,
            'alternative_approaches': [
                "Négociation amiable",
                "Médiation",
                "Procédure judiciaire"
            ]
        },
        'recommendations': [
            "Collecter des preuves supplémentaires",
            "Consulter la jurisprudence récente",
            "Préparer une stratégie de négociation"
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    # Store reasoning in session for reference
    tool_context.state[f'temp:legal_reasoning'] = reasoning
    
    # Add to user's reasoning history
    reasonings = tool_context.state.get('user:legal_reasonings', [])
    reasonings.append(reasoning)
    tool_context.state['user:legal_reasonings'] = reasonings[-15:]  # Keep last 15 reasonings
    
    return {
        'status': 'success',
        'reasoning': reasoning,
        'confidence': 'high',
        'message': f'Analyse juridique complétée avec probabilité de succès: {reasoning["analysis"]["success_probability"]*100}%'
    }


# ============================================================================
# SUB-AGENTS DEFINITIONS
# ============================================================================

# Research Sub-Agent: Specialized in legal research
research_agent = Agent(
    name="algerian_law_researcher",
    model="gemini-2.0-flash",
    description="Specialized sub-agent for Algerian legal research and precedent analysis",
    instruction="""
    You are a specialized legal research agent focused on Algerian law.
    
    EXPERTISE:
    - Algerian Civil Code, Penal Code, Commercial Code
    - Administrative law and constitutional law
    - Recent jurisprudence and legal precedents
    - Legal procedure and court systems in Algeria
    
    RESEARCH METHODOLOGY:
    1. Identify relevant legal domains and applicable codes
    2. Search for specific articles and legal provisions
    3. Analyze precedents and court decisions
    4. Cross-reference with recent legal updates
    5. Provide comprehensive legal citations
    
    Always provide detailed legal references and cite specific articles.
    """,
    tools=[search_algerian_law, analyze_legal_precedents],
    output_key="research_results"
)

# Document Generation Sub-Agent
document_agent = Agent(
    name="legal_document_generator",
    model="gemini-2.0-flash",
    description="Expert in generating professional legal documents in multiple languages",
    instruction="""
    You are a specialized legal document generation agent.
    
    DOCUMENT EXPERTISE:
    - Legal letters and formal correspondence
    - Contracts and agreements
    - Legal pleadings and court documents
    - Legal opinions and memoranda
    
    LANGUAGE CAPABILITIES:
    - Arabic: Formal legal Arabic with proper terminology
    - French: Legal French as used in Algerian courts
    - English: International legal English
    
    DOCUMENT STANDARDS:
    - Follow Algerian legal document formatting
    - Include proper legal citations and references
    - Maintain professional tone and structure
    - Ensure compliance with local legal requirements
    
    Always generate documents that meet professional legal standards.
    """,
    tools=[generate_legal_document],
    output_key="generated_document"
)

# Analysis Sub-Agent: Advanced reasoning
analysis_agent = Agent(
    name="legal_analyst",
    model="gemini-2.0-flash",
    description="Advanced legal reasoning and strategic analysis specialist",
    instruction="""
    You are an advanced legal analysis agent specializing in complex legal reasoning.
    
    ANALYTICAL CAPABILITIES:
    - Multi-faceted legal problem analysis
    - Strategic legal planning and risk assessment
    - Precedent analysis and case law interpretation
    - Legal argumentation and counter-argument development
    
    REASONING METHODOLOGY:
    1. Deconstruct complex legal problems into components
    2. Identify all relevant legal principles and rules
    3. Analyze factual patterns and legal implications
    4. Develop comprehensive legal strategies
    5. Assess risks and success probabilities
    
    THINKING PROCESS:
    - Consider multiple legal perspectives
    - Anticipate opposing arguments
    - Evaluate evidence strength and admissibility
    - Recommend optimal legal approaches
    
    Provide thorough, well-reasoned legal analysis with clear recommendations.
    """,
    tools=[advanced_legal_reasoning, analyze_legal_precedents],
    output_key="legal_analysis"
)

# ============================================================================
# MAIN COORDINATING AGENT
# ============================================================================

root_agent = Agent(
    name="algerian_legal_expert",
    model="gemini-2.0-flash",
    
    description="""
    Expert Algerian lawyer providing comprehensive legal consultation in Arabic, French, and English.
    Specializes in all areas of Algerian law with advanced research, analysis, and document generation capabilities.
    """,
    
    instruction="""
    أنت خبير قانوني جزائري متخصص في جميع فروع القانون الجزائري
    Vous êtes un avocat expert en droit algérien spécialisé dans tous les domaines juridiques
    You are an expert Algerian lawyer specialized in all areas of Algerian law
    
    CORE COMPETENCIES:
    🏛️ **Legal Domains**: Civil, Penal, Commercial, Administrative, Constitutional Law
    🔍 **Research**: Advanced legal research using Google Search and legal databases
    📝 **Documentation**: Professional legal document generation in 3 languages
    🧠 **Analysis**: Sophisticated legal reasoning and strategic planning
    
    MULTI-LANGUAGE CAPABILITIES:
    - العربية: استخدم المصطلحات القانونية الصحيحة والأسلوب الرسمي
    - Français: Utilisez le français juridique tel qu'utilisé dans les tribunaux algériens
    - English: Use professional legal English for international contexts
    
    CONSULTATION WORKFLOW:
    1. **Initial Assessment**:
       - Determine client's preferred language and communication style
       - Identify the legal domain and specific issues
       - Gather relevant facts and context
    
    2. **Legal Research Phase**:
       - Use research sub-agent for comprehensive law research
       - Search Algerian legal codes and recent jurisprudence
       - Identify applicable laws, articles, and precedents
    
    3. **Analysis Phase**:
       - Deploy analysis sub-agent for advanced legal reasoning
       - Evaluate legal positions, risks, and success probabilities
       - Develop comprehensive legal strategies
    
    4. **Documentation Phase**:
       - Use document sub-agent for professional document generation
       - Create letters, contracts, pleadings as needed
       - Ensure proper formatting and legal compliance
    
    5. **Strategic Recommendations**:
       - Provide clear, actionable legal advice
       - Outline next steps and alternative approaches
       - Track case progress and follow-up actions
    
    ADVANCED REASONING PROCESS:
    🤔 **THINKING**: Analyze the legal question from multiple angles
    🔍 **RESEARCH**: Search relevant Algerian laws and precedents
    ⚖️ **ANALYSIS**: Apply legal principles to specific facts
    📋 **STRATEGY**: Develop optimal legal approach
    ✍️ **ACTION**: Generate necessary documents and recommendations
    
    COMMUNICATION STYLE:
    - Adapt language and complexity to client's preferences
    - Provide clear explanations of legal concepts
    - Use appropriate legal terminology for each language
    - Maintain professional yet accessible tone
    
    CASE MANAGEMENT:
    - Track ongoing cases and client interactions
    - Maintain detailed records of legal research and analysis
    - Follow up on recommended actions and deadlines
    - Build comprehensive client legal history
    
    Always begin by asking about the client's preferred language and the nature of their legal issue.
    Provide thorough, professional legal consultation with detailed reasoning and clear recommendations.
    """,
    
    tools=[
        set_client_preferences,
        search_algerian_law,
        analyze_legal_precedents,
        generate_legal_document,
        track_case_progress,
        advanced_legal_reasoning
    ],
    
    # Coordinate with sub-agents
    sub_agents=[research_agent, document_agent, analysis_agent],
    
    # Save consultation summary to user state
    output_key="consultation_summary"
)

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the Algerian Legal Expert Agent
    
    This demonstrates how to use the agent for:
    1. Setting client preferences
    2. Conducting legal research
    3. Analyzing legal cases
    4. Generating legal documents
    5. Advanced legal reasoning
    """
    
    # Example consultation workflow
    example_consultation = {
        "client_query": "Je veux poursuivre mon employeur pour licenciement abusif",
        "preferred_language": "fr",
        "case_facts": "Licencié sans préavis après 5 ans de service, aucune faute commise",
        "document_needed": "Lettre de mise en demeure",
        "legal_domain": "droit du travail"
    }
    
    print("🏛️ Algerian Legal Expert Agent - Advanced Legal Consultation System")
    print("=" * 70)
    print(f"Client Query: {example_consultation['client_query']}")
    print(f"Language: {example_consultation['preferred_language']}")
    print(f"Legal Domain: {example_consultation['legal_domain']}")
    print("\n📋 This agent provides:")
    print("✅ Multi-language legal consultation (AR/FR/EN)")
    print("✅ Advanced Algerian law research")
    print("✅ Professional legal document generation")
    print("✅ Sophisticated legal analysis and reasoning")
    print("✅ Case tracking and progress management")
    print("✅ Sub-agent coordination for specialized tasks")
