"""
Image Serving Router
Serves generated images and provides image management endpoints
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from auth.dependencies import get_current_user


router = APIRouter(prefix="/api/v1/images", tags=["images"])

# Base directory for generated images
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/serve/{filename}")
async def serve_image(filename: str, current_user: dict = Depends(get_current_user)):
    """
    Serve a generated image file
    
    Args:
        filename: Name of the image file
        current_user: Current authenticated user
        
    Returns:
        FileResponse: The image file
    """
    try:
        # Security: Only allow certain file extensions
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        file_path = IMAGES_DIR / filename
        
        if not file_path.suffix.lower() in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Additional security: Ensure file is within images directory
        if not str(file_path.resolve()).startswith(str(IMAGES_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Serving image: {filename} to user {current_user.get('username', 'unknown')}")
        
        return FileResponse(
            path=str(file_path),
            media_type=f"image/{file_path.suffix[1:]}",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve image")


@router.get("/metadata/{filename}")
async def get_image_metadata(filename: str, current_user: dict = Depends(get_current_user)):
    """
    Get metadata for a generated image
    
    Args:
        filename: Name of the image file (without extension)
        current_user: Current authenticated user
        
    Returns:
        Dict: Image metadata
    """
    try:
        # Remove extension if provided
        base_name = Path(filename).stem
        metadata_path = IMAGES_DIR / f"{base_name}.json"
        
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Metadata not found")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        logger.debug(f"Retrieved metadata for {filename}")
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata for {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metadata")


@router.get("/list")
async def list_generated_images(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    List all generated images with metadata
    
    Args:
        limit: Maximum number of images to return
        offset: Number of images to skip
        current_user: Current authenticated user
        
    Returns:
        Dict: List of images with metadata
    """
    try:
        # Get all image files
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        image_files = []
        
        for file_path in IMAGES_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_info = {
                    "filename": file_path.name,
                    "created_at": file_path.stat().st_ctime,
                    "size": file_path.stat().st_size,
                    "url": f"/api/v1/images/serve/{file_path.name}"
                }
                
                # Try to get metadata
                metadata_path = file_path.with_suffix('.json')
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        image_info["metadata"] = metadata
                    except Exception as e:
                        logger.warning(f"Failed to read metadata for {file_path.name}: {e}")
                
                image_files.append(image_info)
        
        # Sort by creation time (newest first)
        image_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total = len(image_files)
        paginated_images = image_files[offset:offset + limit]
        
        logger.info(f"Listed {len(paginated_images)} images (total: {total}) for user {current_user.get('username', 'unknown')}")
        
        return {
            "images": paginated_images,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        raise HTTPException(status_code=500, detail="Failed to list images")


@router.delete("/{filename}")
async def delete_image(filename: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a generated image and its metadata
    
    Args:
        filename: Name of the image file
        current_user: Current authenticated user
        
    Returns:
        Dict: Success message
    """
    try:
        file_path = IMAGES_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Security check
        if not str(file_path.resolve()).startswith(str(IMAGES_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete image file
        file_path.unlink()
        
        # Delete metadata file if it exists
        metadata_path = file_path.with_suffix('.json')
        if metadata_path.exists():
            metadata_path.unlink()
        
        logger.info(f"Deleted image {filename} by user {current_user.get('username', 'unknown')}")
        
        return {"message": f"Image {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")


@router.get("/gallery")
async def get_image_gallery(current_user: dict = Depends(get_current_user)):
    """
    Get a gallery view of recent images
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict: Gallery data with thumbnails
    """
    try:
        # Get recent images
        images_response = await list_generated_images(limit=20, offset=0, current_user=current_user)
        images = images_response["images"]
        
        # Format for gallery display
        gallery_items = []
        for image in images:
            gallery_item = {
                "id": Path(image["filename"]).stem,
                "filename": image["filename"],
                "url": image["url"],
                "thumbnail_url": image["url"],  # For now, same as full image
                "created_at": image["created_at"],
                "size": image["size"]
            }
            
            # Add metadata if available
            if "metadata" in image:
                metadata = image["metadata"]
                gallery_item.update({
                    "prompt": metadata.get("prompt", ""),
                    "model": metadata.get("model_id", ""),
                    "generation_type": metadata.get("generation_type", ""),
                    "timestamp": metadata.get("timestamp", "")
                })
            
            gallery_items.append(gallery_item)
        
        return {
            "gallery": gallery_items,
            "total": len(gallery_items)
        }
        
    except Exception as e:
        logger.error(f"Error getting image gallery: {e}")
        raise HTTPException(status_code=500, detail="Failed to get image gallery")
