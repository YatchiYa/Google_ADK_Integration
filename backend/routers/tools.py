"""
Tools API Router
Handles tool management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger

from managers.tool_manager import ToolManager
from models.api_models import *
from auth.dependencies import get_current_user, require_permission


router = APIRouter()


def get_tool_manager() -> ToolManager:
    """Dependency to get tool manager"""
    from main import managers
    return managers["tool_manager"]


@router.get("/", response_model=ToolListResponse)
async def list_tools(
    category: Optional[str] = Query(None, description="Filter by category"),
    enabled_only: bool = Query(True, description="Only return enabled tools"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tools to return"),
    offset: int = Query(0, ge=0, description="Number of tools to skip"),
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """List all tools"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        tools = tool_manager.list_tools(category=category, enabled_only=enabled_only)
        
        # Apply pagination
        total = len(tools)
        tools = tools[offset:offset + limit]
        
        # Convert to response models
        tool_responses = []
        for tool in tools:
            tool_response = ToolInfoResponse(
                name=tool.name,
                description=tool.description,
                category=tool.category,
                version=tool.version,
                author=tool.author,
                registered_at=tool.registered_at,
                usage_count=tool.usage_count,
                is_enabled=tool.is_enabled,
                metadata=tool.metadata
            )
            tool_responses.append(tool_response)
        
        return ToolListResponse(
            success=True,
            message=f"Retrieved {len(tool_responses)} tools",
            tools=tool_responses,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_name}", response_model=ToolInfoResponse)
async def get_tool(
    tool_name: str,
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get tool by name"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        tool = tool_manager.get_tool_info(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return ToolInfoResponse(
            name=tool.name,
            description=tool.description,
            category=tool.category,
            version=tool.version,
            author=tool.author,
            registered_at=tool.registered_at,
            usage_count=tool.usage_count,
            is_enabled=tool.is_enabled,
            metadata=tool.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=BaseResponse)
async def register_tool(
    request: RegisterToolRequest,
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Register a new tool (placeholder - actual tool registration requires code)"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # This is a placeholder - in a real implementation, you'd need to handle
        # actual tool code registration, which is complex and requires security considerations
        
        return BaseResponse(
            success=False,
            message="Tool registration via API is not implemented. Use the tool manager directly or import from modules."
        )
        
    except Exception as e:
        logger.error(f"Error registering tool: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{tool_name}/enable", response_model=BaseResponse)
async def enable_tool(
    tool_name: str,
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Enable a tool"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = tool_manager.enable_tool(tool_name)
        if success:
            return BaseResponse(
                success=True,
                message=f"Tool '{tool_name}' enabled successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Tool not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tool_name}/disable", response_model=BaseResponse)
async def disable_tool(
    tool_name: str,
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Disable a tool"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = tool_manager.disable_tool(tool_name)
        if success:
            return BaseResponse(
                success=True,
                message=f"Tool '{tool_name}' disabled successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Tool not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{tool_name}", response_model=BaseResponse)
async def unregister_tool(
    tool_name: str,
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Unregister a tool"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success = tool_manager.unregister_tool(tool_name)
        if success:
            return BaseResponse(
                success=True,
                message=f"Tool '{tool_name}' unregistered successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Tool not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{query}", response_model=ToolListResponse)
async def search_tools(
    query: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Search tools by name or description"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        tools = tool_manager.search_tools(query)[:limit]
        
        # Convert to response models
        tool_responses = []
        for tool in tools:
            tool_response = ToolInfoResponse(
                name=tool.name,
                description=tool.description,
                category=tool.category,
                version=tool.version,
                author=tool.author,
                registered_at=tool.registered_at,
                usage_count=tool.usage_count,
                is_enabled=tool.is_enabled,
                metadata=tool.metadata
            )
            tool_responses.append(tool_response)
        
        return ToolListResponse(
            success=True,
            message=f"Found {len(tool_responses)} tools matching '{query}'",
            tools=tool_responses,
            total=len(tool_responses)
        )
        
    except Exception as e:
        logger.error(f"Error searching tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/list")
async def list_categories(
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """List all tool categories"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        categories = tool_manager.get_categories()
        
        return {
            "success": True,
            "message": f"Retrieved {len(categories)} categories",
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview", response_model=ToolStatsResponse)
async def get_tool_stats(
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get tool statistics"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        stats = tool_manager.get_tool_stats()
        
        return ToolStatsResponse(
            total_tools=stats["total_tools"],
            enabled_tools=stats["enabled_tools"],
            disabled_tools=stats["disabled_tools"],
            categories=stats["categories"],
            category_breakdown=stats["category_breakdown"],
            most_used_tools=stats["most_used_tools"],
            total_usage=stats["total_usage"]
        )
        
    except Exception as e:
        logger.error(f"Error getting tool stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-module", response_model=BaseResponse)
async def import_tools_from_module(
    module_path: str,
    category: str = "imported",
    prefix: str = "",
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Import tools from a Python module"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Security check - only allow certain modules for safety
        allowed_modules = [
            "tools.custom_tools",
            "tools.google_adk_tools",
            "google.adk.tools"
        ]
        
        if module_path not in allowed_modules:
            raise HTTPException(
                status_code=403,
                detail=f"Module '{module_path}' not in allowed list for security reasons"
            )
        
        registered_count = tool_manager.register_from_module(
            module_path=module_path,
            category=category,
            prefix=prefix
        )
        
        return BaseResponse(
            success=True,
            message=f"Imported {registered_count} tools from module '{module_path}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing tools from module: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/config")
async def export_tool_registry(
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Export tool registry configuration"""
    try:
        # Check permissions
        if not require_permission(current_user, "tools:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        config = tool_manager.export_registry_config()
        
        return {
            "success": True,
            "message": "Tool registry configuration exported",
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Error exporting tool registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear", response_model=BaseResponse)
async def clear_tool_registry(
    keep_builtin: bool = Query(True, description="Keep built-in tools"),
    tool_manager: ToolManager = Depends(get_tool_manager),
    current_user: dict = Depends(get_current_user)
):
    """Clear tool registry"""
    try:
        # Check permissions (admin only for this operation)
        if not require_permission(current_user, "admin:tools"):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        tool_manager.clear_registry(keep_builtin=keep_builtin)
        
        return BaseResponse(
            success=True,
            message=f"Tool registry cleared (kept builtin: {keep_builtin})"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing tool registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))
