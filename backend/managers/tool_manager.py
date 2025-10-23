"""
Dynamic Tool Registry for Google ADK
Allows runtime registration and management of tools for agents
"""

import inspect
import importlib
from typing import Dict, List, Any, Callable, Optional, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

from google.adk.tools import BaseTool


@dataclass
class ToolInfo:
    """Information about a registered tool"""
    name: str
    tool: Union[Callable, BaseTool, Type]
    description: str
    category: str = "general"
    version: str = "1.0.0"
    author: str = "system"
    registered_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    is_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolManager:
    """
    Dynamic tool registry for managing agent tools
    Supports runtime registration, categorization, and tool lifecycle management
    """
    
    def __init__(self):
        """Initialize tool registry"""
        self._tools: Dict[str, ToolInfo] = {}
        self._categories: Dict[str, List[str]] = {}
        self._tool_dependencies: Dict[str, List[str]] = {}
        
        # Debug tracking
        self._tool_registration_count = 0
        self._tool_usage_stats = {}
        
        # Register built-in tools
        logger.debug("DEBUG: ToolManager.__init__ - Starting built-in tools registration")
        self._register_builtin_tools()
        
        logger.info("Tool registry initialized")
        logger.debug(f"DEBUG: ToolManager.__init__ - Initialized with {len(self._tools)} tools, {len(self._categories)} categories")

    def register_tool(self, 
                     name: str,
                     tool: Union[Callable, BaseTool, Type],
                     description: str = "",
                     category: str = "custom",
                     version: str = "1.0.0",
                     author: str = "user",
                     dependencies: Optional[List[str]] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     force_replace: bool = False) -> bool:
        """
        Register a new tool
        
        Args:
            name: Unique tool name
            tool: Tool function, class, or instance
            description: Tool description
            category: Tool category
            version: Tool version
            author: Tool author
            dependencies: List of required tool names
            metadata: Additional metadata
            force_replace: Whether to replace existing tool
            
        Returns:
            bool: Success status
        """
        try:
            self._tool_registration_count += 1
            reg_id = f"reg_{self._tool_registration_count}"
            
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Registering tool '{name}'")
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Tool type: {type(tool)}, Category: {category}")
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Dependencies: {dependencies}, Force replace: {force_replace}")
            
            # Check if tool already exists
            if name in self._tools and not force_replace:
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Tool '{name}' already exists, not replacing")
                logger.warning(f"Tool '{name}' already exists. Use force_replace=True to override")
                return False
            
            # Validate tool
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Validating tool '{name}'")
            if not self._validate_tool(tool):
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Tool '{name}' validation failed")
                logger.error(f"Tool '{name}' validation failed")
                return False
            
            # Extract description if not provided
            if not description:
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Extracting description for '{name}'")
                description = self._extract_description(tool)
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Extracted description: '{description[:100]}...'")
            
            # Create tool info
            tool_info = ToolInfo(
                name=name,
                tool=tool,
                description=description,
                category=category,
                version=version,
                author=author,
                metadata=metadata or {}
            )
            
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Created ToolInfo for '{name}'")
            
            # Register tool
            self._tools[name] = tool_info
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Tool '{name}' stored in registry")
            
            # Update category index
            if category not in self._categories:
                self._categories[category] = []
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Created new category '{category}'")
            if name not in self._categories[category]:
                self._categories[category].append(name)
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Added '{name}' to category '{category}'")
            
            # Register dependencies
            if dependencies:
                self._tool_dependencies[name] = dependencies
                logger.debug(f"DEBUG: register_tool ({reg_id}) - Registered dependencies for '{name}': {dependencies}")
            
            # Update usage stats
            self._tool_usage_stats[name] = {
                "registered_at": datetime.now(),
                "registration_id": reg_id,
                "category": category,
                "author": author,
                "usage_count": 0
            }
            
            logger.debug(f"DEBUG: register_tool ({reg_id}) - Registration complete. Total tools: {len(self._tools)}")
            logger.info(f"Registered tool '{name}' in category '{category}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool '{name}': {e}")
            return False

    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool"""
        try:
            if name not in self._tools:
                logger.warning(f"Tool '{name}' not found")
                return False
            
            tool_info = self._tools[name]
            
            # Remove from category index
            if tool_info.category in self._categories:
                if name in self._categories[tool_info.category]:
                    self._categories[tool_info.category].remove(name)
                
                # Remove empty categories
                if not self._categories[tool_info.category]:
                    del self._categories[tool_info.category]
            
            # Remove dependencies
            self._tool_dependencies.pop(name, None)
            
            # Remove tool
            del self._tools[name]
            
            logger.info(f"Unregistered tool '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister tool '{name}': {e}")
            return False

    def get_tool(self, name: str) -> Optional[Union[Callable, BaseTool, Type]]:
        """Get tool by name"""
        tool_info = self._tools.get(name)
        if tool_info and tool_info.is_enabled:
            # Increment usage count
            tool_info.usage_count += 1
            return tool_info.tool
        return None

    def get_tool_info(self, name: str) -> Optional[ToolInfo]:
        """Get tool information"""
        return self._tools.get(name)

    def list_tools(self, 
                  category: Optional[str] = None,
                  enabled_only: bool = True) -> List[ToolInfo]:
        """List available tools"""
        tools = []
        
        for tool_info in self._tools.values():
            # Filter by enabled status
            if enabled_only and not tool_info.is_enabled:
                continue
            
            # Filter by category
            if category and tool_info.category != category:
                continue
            
            tools.append(tool_info)
        
        return sorted(tools, key=lambda x: x.name)

    def get_tools_for_agent(self, 
                          tool_names: List[str],
                          resolve_dependencies: bool = True,
                          agent_manager=None,
                          memory_manager=None,
                          user_id: Optional[str] = None,
                          agent_id: Optional[str] = None) -> List[Union[Callable, BaseTool, Type]]:
        """Get tools for an agent with dependency resolution"""
        logger.debug(f"DEBUG: get_tools_for_agent - Requested tools: {tool_names}")
        logger.debug(f"DEBUG: get_tools_for_agent - Resolve dependencies: {resolve_dependencies}")
        logger.debug(f"DEBUG: get_tools_for_agent - Agent manager: {type(agent_manager) if agent_manager else None}")
        logger.debug(f"DEBUG: get_tools_for_agent - Memory manager: {type(memory_manager) if memory_manager else None}")
        logger.debug(f"DEBUG: get_tools_for_agent - User ID: {user_id}, Agent ID: {agent_id}")
        
        tools = []
        resolved_names = set()
        resolution_order = []
        
        def resolve_tool(name: str):
            logger.debug(f"DEBUG: resolve_tool - Resolving tool: {name}")
            
            if name in resolved_names:
                logger.debug(f"DEBUG: resolve_tool - Tool {name} already resolved, skipping")
                return
            
            resolution_order.append(name)
            
            # Check if it's an agent tool (starts with "agent:")
            if name.startswith("agent:") and agent_manager:
                target_agent_id = name[6:]  # Remove "agent:" prefix
                logger.debug(f"DEBUG: resolve_tool - Processing agent tool for agent: {target_agent_id}")
                
                try:
                    # Use Google ADK AgentTool for proper delegation
                    from google.adk.tools.agent_tool import AgentTool
                    logger.debug(f"DEBUG: resolve_tool - Imported Google ADK AgentTool")
                    
                    target_agent = agent_manager.get_agent(target_agent_id)
                    logger.debug(f"DEBUG: resolve_tool - Retrieved target agent: {type(target_agent) if target_agent else None}")
                    
                    if target_agent:
                        agent_tool = AgentTool(agent=target_agent)
                        tools.append(agent_tool)
                        resolved_names.add(name)
                        logger.debug(f"DEBUG: resolve_tool - Created Google ADK AgentTool for agent {target_agent_id}")
                        logger.info(f"Created Google ADK AgentTool for agent {target_agent_id}")
                        return
                    else:
                        logger.debug(f"DEBUG: resolve_tool - Target agent {target_agent_id} not found")
                        logger.warning(f"Target agent {target_agent_id} not found for AgentTool")
                        return
                except ImportError:
                    # Fallback to custom agent tool if ADK AgentTool not available
                    try:
                        from utils.agent_tool import create_agent_tool
                        agent_tool = create_agent_tool(target_agent_id, agent_manager)
                        tools.append(agent_tool)
                        resolved_names.add(name)
                        logger.info(f"Created custom agent tool for agent {target_agent_id}")
                        return
                    except Exception as e:
                        logger.error(f"Failed to create agent tool for {target_agent_id}: {e}")
                        return
                except Exception as e:
                    logger.error(f"Failed to create Google ADK AgentTool for {target_agent_id}: {e}")
                    return
            
            # Check if it's a shared memory tool
            if name in ["shared_memory", "search_shared_memory", "cross_agent_memory", "session_memory_bridge"]:
                if memory_manager and user_id and agent_id:
                    try:
                        from tools.shared_memory_tools import create_shared_memory_tools
                        shared_tools = create_shared_memory_tools(memory_manager, user_id, agent_id)
                        
                        # Map tool names to functions
                        tool_map = {
                            "shared_memory": shared_tools[0],
                            "search_shared_memory": shared_tools[1], 
                            "cross_agent_memory": shared_tools[2],
                            "session_memory_bridge": shared_tools[3]
                        }
                        
                        if name in tool_map:
                            tools.append(tool_map[name])
                            resolved_names.add(name)
                            logger.info(f"Created shared memory tool: {name}")
                            return
                    except Exception as e:
                        logger.error(f"Failed to create shared memory tool {name}: {e}")
                        return
                else:
                    logger.warning(f"Shared memory tool '{name}' requires memory_manager, user_id, and agent_id")
                    return
            
            # Resolve dependencies first
            if resolve_dependencies and name in self._tool_dependencies:
                for dep_name in self._tool_dependencies[name]:
                    resolve_tool(dep_name)
            
            # Add tool if available
            tool = self.get_tool(name)
            if tool:
                tools.append(tool)
                resolved_names.add(name)
            else:
                logger.warning(f"Tool '{name}' not found or disabled")
        
        # Resolve all requested tools
        logger.debug(f"DEBUG: get_tools_for_agent - Starting resolution of {len(tool_names)} tools")
        
        for name in tool_names:
            logger.debug(f"DEBUG: get_tools_for_agent - Processing tool request: {name}")
            resolve_tool(name)
        
        # Update usage stats
        for name in resolved_names:
            if name in self._tool_usage_stats:
                self._tool_usage_stats[name]["usage_count"] += 1
        
        logger.debug(f"DEBUG: get_tools_for_agent - Resolution complete")
        logger.debug(f"DEBUG: get_tools_for_agent - Resolution order: {resolution_order}")
        logger.debug(f"DEBUG: get_tools_for_agent - Resolved tools: {resolved_names}")
        logger.debug(f"DEBUG: get_tools_for_agent - Tool types: {[type(tool).__name__ for tool in tools]}")
        
        logger.info(f"Resolved {len(tools)} tools for agent: {', '.join(resolved_names)}")
        return tools

    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories and their tools"""
        return dict(self._categories)

    def enable_tool(self, name: str) -> bool:
        """Enable a tool"""
        if name in self._tools:
            self._tools[name].is_enabled = True
            logger.info(f"Enabled tool '{name}'")
            return True
        return False

    def disable_tool(self, name: str) -> bool:
        """Disable a tool"""
        if name in self._tools:
            self._tools[name].is_enabled = False
            logger.info(f"Disabled tool '{name}'")
            return True
        return False

    def search_tools(self, query: str) -> List[ToolInfo]:
        """Search tools by name or description"""
        query_lower = query.lower()
        matches = []
        
        for tool_info in self._tools.values():
            if not tool_info.is_enabled:
                continue
            
            # Search in name and description
            if (query_lower in tool_info.name.lower() or 
                query_lower in tool_info.description.lower()):
                matches.append(tool_info)
        
        return sorted(matches, key=lambda x: x.usage_count, reverse=True)

    def register_from_module(self, 
                           module_path: str,
                           category: str = "imported",
                           prefix: str = "") -> int:
        """Register tools from a Python module"""
        try:
            module = importlib.import_module(module_path)
            registered_count = 0
            
            # Find all callable objects in module
            for name, obj in inspect.getmembers(module):
                if name.startswith('_'):
                    continue
                
                if inspect.isfunction(obj) or inspect.isclass(obj):
                    tool_name = f"{prefix}{name}" if prefix else name
                    
                    if self.register_tool(
                        name=tool_name,
                        tool=obj,
                        category=category,
                        author=f"module:{module_path}"
                    ):
                        registered_count += 1
            
            logger.info(f"Registered {registered_count} tools from module '{module_path}'")
            return registered_count
            
        except Exception as e:
            logger.error(f"Failed to register tools from module '{module_path}': {e}")
            return 0

    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool registry statistics"""
        total_tools = len(self._tools)
        enabled_tools = sum(1 for t in self._tools.values() if t.is_enabled)
        
        # Usage statistics
        usage_stats = {}
        for tool_info in self._tools.values():
            usage_stats[tool_info.name] = tool_info.usage_count
        
        # Category statistics
        category_stats = {}
        for category, tools in self._categories.items():
            category_stats[category] = len(tools)
        
        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "disabled_tools": total_tools - enabled_tools,
            "categories": len(self._categories),
            "category_breakdown": category_stats,
            "most_used_tools": sorted(
                usage_stats.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "total_usage": sum(usage_stats.values())
        }

    def _validate_tool(self, tool: Union[Callable, BaseTool, Type]) -> bool:
        """Validate tool before registration"""
        try:
            # Check if it's callable or a BaseTool
            if not (callable(tool) or isinstance(tool, BaseTool) or 
                   (inspect.isclass(tool) and issubclass(tool, BaseTool))):
                return False
            
            # Additional validation can be added here
            return True
            
        except Exception:
            return False

    def _extract_description(self, tool: Union[Callable, BaseTool, Type]) -> str:
        """Extract description from tool"""
        try:
            if hasattr(tool, '__doc__') and tool.__doc__:
                return tool.__doc__.strip()
            elif hasattr(tool, 'description'):
                return tool.description
            else:
                return f"Tool: {getattr(tool, '__name__', str(tool))}"
        except Exception:
            return "No description available"

    def _register_builtin_tools(self):
        """Register built-in tools"""
        try:
            # Load memory tool
            def load_memory_tool(query: str) -> str:
                """Load relevant information from memory"""
                return f"Memory search results for: {query}"
            
            self.register_tool(
                name="load_memory",
                tool=load_memory_tool,
                description="Search and load relevant information from memory",
                category="memory",
                author="system"
            )
            
                # Register Google ADK built-in tools
            try:
                # Try to import Google ADK built-in tools 
                from google.adk.tools import google_search  
                self.register_tool(
                    name="google_search",
                    tool=google_search,
                    description="Google ADK built-in Google Search tool. Search the web using Google Search grounding.",
                    category="search",
                    author="google_adk"
                )
                logger.info("Registered Google ADK built-in google_search")
                
                # Register our custom tools
                from tools.google_adk_tools import (
                    custom_calculator, 
                    text_analyzer,
                    product_hunt_search,
                    yahoo_finance_data,
                    call_document_rag_code_civile_algerian
                )
                
                # Register Gemini image tools
                from tools.gemini_image_tool import (
                    gemini_image_generator,
                    gemini_text_to_image,
                    gemini_image_editor
                )
                
                # Register Meta publisher tools
                from tools.meta_publisher_tool import (
                    meta_publish_content,
                    meta_publish_text,
                    meta_publish_image,
                    meta_publish_text_and_image,
                    meta_get_account_info,
                    update_meta_tokens
                )
                
                self.register_tool(
                    name="custom_calculator",
                    tool=custom_calculator,
                    description="Safe calculator for mathematical expressions. Supports basic arithmetic operations.",
                    category="utility",
                    author="system"
                )
                
                self.register_tool(
                    name="text_analyzer",
                    tool=text_analyzer,
                    description="Analyze text for word count, sentiment, and other metrics.",
                    category="analysis",
                    author="system"
                )
                
                self.register_tool(
                    name="product_hunt_search",
                    tool=product_hunt_search,
                    description="Search Product Hunt for products, posts, and collections. Supports query types: search, posts, collections.",
                    category="api",
                    author="system"
                )
                
                self.register_tool(
                    name="yahoo_finance_data",
                    tool=yahoo_finance_data,
                    description="Get real-time and historical financial data from Yahoo Finance. Supports stocks, crypto, and other symbols.",
                    category="finance",
                    author="system"
                )

                self.register_tool(
                    name="call_document_rag_code_civile_algerian",
                    tool=call_document_rag_code_civile_algerian,
                    description="Search and retrieve information from the Algerian Civil Code using RAG (Retrieval-Augmented Generation). Provides expert legal analysis and context from Algerian civil law documents.",
                    category="document_rag",
                    author="system"
                )
                
                # Register Gemini image generation tools
                self.register_tool(
                    name="gemini_image_generator",
                    tool=gemini_image_generator,
                    description="Advanced image generation and editing using Google Gemini AI. Supports text-to-image, image editing, restoration, colorization, and iterative editing.",
                    category="ai_image",
                    author="system"
                )
                
                self.register_tool(
                    name="gemini_text_to_image",
                    tool=gemini_text_to_image,
                    description="Simple text-to-image generation using Google Gemini AI. Generate images from text descriptions.",
                    category="ai_image",
                    author="system"
                )
                
                self.register_tool(
                    name="gemini_image_editor",
                    tool=gemini_image_editor,
                    description="Edit existing images using Google Gemini AI. Modify images with text prompts.",
                    category="ai_image",
                    author="system"
                )
                
                # Register Meta publisher tools
                self.register_tool(
                    name="meta_publish_content",
                    tool=meta_publish_content,
                    description="Universal Meta publishing tool for Facebook and Instagram. Supports text, images, and combined content.",
                    category="social_media",
                    author="system"
                )
                
                self.register_tool(
                    name="meta_publish_text",
                    tool=meta_publish_text,
                    description="Publish text content to Facebook (Instagram requires images).",
                    category="social_media",
                    author="system"
                )
                
                self.register_tool(
                    name="meta_publish_image",
                    tool=meta_publish_image,
                    description="Publish image content to Facebook and Instagram with optional caption.",
                    category="social_media",
                    author="system"
                )
                
                self.register_tool(
                    name="meta_publish_text_and_image",
                    tool=meta_publish_text_and_image,
                    description="Publish text with image to Facebook and Instagram.",
                    category="social_media",
                    author="system"
                )
                
                self.register_tool(
                    name="meta_get_account_info",
                    tool=meta_get_account_info,
                    description="Get information about configured Meta accounts (Facebook page and Instagram account).",
                    category="social_media",
                    author="system"
                )
                
                self.register_tool(
                    name="update_meta_tokens",
                    tool=update_meta_tokens,
                    description="Update Meta authentication tokens from frontend Facebook login.",
                    category="social_media",
                    author="system"
                )
                
                logger.info("Registered custom tools including Product Hunt, Yahoo Finance, Gemini Image, and Meta Publisher tools")
                
            except ImportError as e:
                logger.warning(f"Could not register tools: {e}")
            
            logger.info("Registered built-in tools")
            
        except Exception as e:
            logger.error(f"Failed to register built-in tools: {e}")

    def export_registry_config(self) -> Dict[str, Any]:
        """Export registry configuration"""
        export_data = {
            "tools": {},
            "categories": dict(self._categories),
            "dependencies": dict(self._tool_dependencies),
            "exported_at": datetime.now().isoformat()
        }
        
        for name, tool_info in self._tools.items():
            export_data["tools"][name] = {
                "name": tool_info.name,
                "description": tool_info.description,
                "category": tool_info.category,
                "version": tool_info.version,
                "author": tool_info.author,
                "is_enabled": tool_info.is_enabled,
                "usage_count": tool_info.usage_count,
                "metadata": tool_info.metadata
            }
        
        return export_data

    def clear_registry(self, keep_builtin: bool = True):
        """Clear all tools from registry"""
        if keep_builtin:
            # Keep only built-in tools
            builtin_tools = {
                name: info for name, info in self._tools.items()
                if info.author in ["system", "google_adk"]
            }
            self._tools = builtin_tools
        else:
            self._tools.clear()
        
        # Rebuild category index
        self._categories.clear()
        self._tool_dependencies.clear()
        
        for tool_info in self._tools.values():
            if tool_info.category not in self._categories:
                self._categories[tool_info.category] = []
            self._categories[tool_info.category].append(tool_info.name)
        
        logger.info(f"Cleared tool registry (kept builtin: {keep_builtin})")
