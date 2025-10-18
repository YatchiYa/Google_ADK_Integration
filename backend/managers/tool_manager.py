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
        
        # Register built-in tools
        self._register_builtin_tools()
        
        logger.info("Tool registry initialized")

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
            # Check if tool already exists
            if name in self._tools and not force_replace:
                logger.warning(f"Tool '{name}' already exists. Use force_replace=True to override")
                return False
            
            # Validate tool
            if not self._validate_tool(tool):
                logger.error(f"Tool '{name}' validation failed")
                return False
            
            # Extract description if not provided
            if not description:
                description = self._extract_description(tool)
            
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
            
            # Register tool
            self._tools[name] = tool_info
            
            # Update category index
            if category not in self._categories:
                self._categories[category] = []
            if name not in self._categories[category]:
                self._categories[category].append(name)
            
            # Register dependencies
            if dependencies:
                self._tool_dependencies[name] = dependencies
            
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
                          agent_manager=None) -> List[Union[Callable, BaseTool, Type]]:
        """Get tools for an agent with dependency resolution"""
        tools = []
        resolved_names = set()
        
        def resolve_tool(name: str):
            if name in resolved_names:
                return
            
            # Check if it's an agent tool (starts with "agent:")
            if name.startswith("agent:") and agent_manager:
                agent_id = name[6:]  # Remove "agent:" prefix
                try:
                    from utils.agent_tool import create_agent_tool
                    agent_tool = create_agent_tool(agent_id, agent_manager)
                    tools.append(agent_tool)
                    resolved_names.add(name)
                    logger.info(f"Created agent tool for agent {agent_id}")
                    return
                except Exception as e:
                    logger.error(f"Failed to create agent tool for {agent_id}: {e}")
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
        for name in tool_names:
            resolve_tool(name)
        
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
                try:
                    from google.adk.tools import google_search as adk_google_search
                    self.register_tool(
                        name="google_search",
                        tool=adk_google_search,
                        description="Google ADK built-in Google Search tool. Search the web using Google Search grounding.",
                        category="search",
                        author="google_adk"
                    )
                    logger.info("Registered Google ADK built-in google_search")
                except ImportError:
                    # Fallback to our custom implementation
                    from tools.google_adk_tools import google_search
                    self.register_tool(
                        name="google_search",
                        tool=google_search,
                        description="Custom Google Search tool. Returns relevant search results with titles, snippets, and URLs.",
                        category="search",
                        author="system"
                    )
                    logger.info("Registered custom google_search (ADK built-in not available)")
                
                # Try to register built-in code execution
                try:
                    from google.adk.code_executors import BuiltInCodeExecutor
                    # Note: Code executor is handled differently, not as a regular tool
                    logger.info("Google ADK built-in code executor available")
                except ImportError:
                    logger.warning("Google ADK built-in code executor not available")
                
                # Register our custom tools
                from tools.google_adk_tools import custom_calculator, text_analyzer
                
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
                
                logger.info("Registered custom tools")
                
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
