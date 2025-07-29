#!/usr/bin/env python3
"""Async Media Agent MCP Server - A Model Context Protocol server for media processing with async support.

This server provides 9 async tools for media processing using threading:
1. TOS - Save content as URL
2. Video Concat - Concatenate two videos
3. Video Last Frame - Get the last frame from a video
4. Seedream - Creating images (AI model)
5. Seedance (lite & pro) - Creating videos (AI model)
6. Seededit - Maintain the main character (AI model)
7. Seed1.6 (VLM) - Do vision tasks in workflow (AI model)
8. Image Selector - Choose the best one from images
9. Video Selector - Choose the best video from videos

All tools are wrapped with threading to provide async functionality without modifying original functions.
"""

import argparse
import asyncio
import logging
from typing import List, Optional
import json
from dotenv import load_dotenv
import uvicorn

from mcp.server.fastmcp import FastMCP

# Import async wrappers
from media_agent_mcp.async_wrapper import (
    async_video_concat_tool,
    async_video_last_frame_tool,
    async_seedream_generate_image_tool,
    async_seedance_generate_video_tool,
    async_seededit_tool,
    async_vlm_vision_task_tool,
    async_image_selector_tool,
    async_video_selector_tool,
    async_tos_save_content_tool,
    cleanup_executor
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (will be configured in main function)
load_dotenv()
mcp = FastMCP("Media-Agent-MCP-Async")


@mcp.tool()
async def video_concat_tool_async(video_urls: List[str]) -> str:
    """
    Asynchronously concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate in order
    
    Returns:
        JSON string with status, data, and message
    """
    return await async_video_concat_tool(video_urls)


@mcp.tool()
async def video_last_frame_tool_async(video_url: str) -> str:
    """
    Asynchronously extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL or path to the video file
        
    Returns:
        JSON string with status, data, and message
    """
    return await async_video_last_frame_tool(video_url)


@mcp.tool()
async def seedream_generate_image_tool_async(prompt: str, size: str = "1024x1024") -> str:
    """
    Asynchronously generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
    
    Returns:
        JSON string with status, data, and message
    """
    return await async_seedream_generate_image_tool(prompt, size)


@mcp.tool()
async def seedance_generate_video_tool_async(prompt: str, first_frame_image: str, 
                                            last_frame_image: str = None, duration: int = 5, 
                                            resolution: str = "720p") -> str:
    """
    Asynchronously generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
    
    Returns:
        JSON string with status, data, and message
    """
    return await async_seedance_generate_video_tool(prompt, first_frame_image, last_frame_image, duration, resolution)


@mcp.tool()
async def seededit_tool_async(image_url: str, prompt: str, seed: int = -1, 
                             scale: float = 0.5, charactor_keep: bool = False) -> str:
    """
    Asynchronously edit an image using Seededit model.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        seed: Random seed for reproducibility (-1 for random)
        scale: Influence degree of text description (0-1)
        charactor_keep: whether to keep the main character in this image, if you wanna change the main character, please keep False
        
    Returns:
        JSON string with status, data, and message
    """
    return await async_seededit_tool(image_url, prompt, seed, scale, charactor_keep)


@mcp.tool()
async def vlm_vision_task_tool_async(messages: List) -> str:
    """
    Asynchronously perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
        
    Returns:
        JSON string with status, data, and message
    """
    return await async_vlm_vision_task_tool(messages)


@mcp.tool()
async def image_selector_tool_async(image_paths: List[str], prompt: str) -> str:
    """
    Asynchronously select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
        
    Returns:
        JSON string with status, data, and message
    """
    return await async_image_selector_tool(image_paths, prompt)


@mcp.tool()
async def video_selector_tool_async(video_paths: List[str], prompt: str) -> str:
    """
    Asynchronously select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
    
    Returns:
        JSON string with status, data, and message
    """
    return await async_video_selector_tool(video_paths, prompt)


@mcp.tool()
async def tos_save_content_tool_async(content: str, file_extension: str = "txt", 
                                     object_key: Optional[str] = None) -> str:
    """
    Asynchronously save content to TOS and return URL.
    
    Args:
        content: Content to save
        file_extension: File extension for the content (default: txt)
        object_key: Optional key to use for the object in TOS
        
    Returns:
        JSON string with status, data, and message
    """
    return await async_tos_save_content_tool(content, file_extension, object_key)


# Utility function for concurrent execution
async def run_multiple_tools_concurrently(*coroutines):
    """
    Run multiple async tools concurrently.
    
    Args:
        *coroutines: Variable number of coroutines to run concurrently
        
    Returns:
        List of results from all coroutines
    """
    return await asyncio.gather(*coroutines, return_exceptions=True)


# Example usage function
async def example_concurrent_usage():
    """
    Example of how to use multiple tools concurrently.
    """
    # Example: Generate image and process video concurrently
    image_task = seedream_generate_image_tool_async("A beautiful sunset", "1024x1024")
    video_task = video_last_frame_tool_async("https://example.com/video.mp4")
    
    # Run both tasks concurrently
    results = await run_multiple_tools_concurrently(image_task, video_task)
    
    return results


def main():
    """Main entry point for the Async MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Async Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='sse',
                        help='Transport method: sse or stdio (default: sse)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8001)')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    
    args = parser.parse_args()
    
    if args.version:
        print("Async Media Agent MCP Server v0.1.0")
        return
    
    logger.info("Starting Async Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")
    
    logger.info("Available async tools:")
    logger.info("  1. video_last_frame_tool_async - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool_async - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool_async - Generate images with AI (async)")
    logger.info("  4. seedance_generate_video_tool_async - Generate videos with AI (async)")
    logger.info("  5. seededit_tool_async - Edit images while maintaining character (async)")
    logger.info("  6. vlm_vision_task_tool_async - Perform vision tasks with OpenAI-compatible messages (async)")
    logger.info("  7. image_selector_tool_async - Select best image using VLM model (async)")
    logger.info("  8. video_selector_tool_async - Select best video using VLM model (async)")
    logger.info("  9. tos_save_content_tool_async - Save content to TOS and return URL (async)")
    logger.info("")
    logger.info("All tools support concurrent execution using asyncio.gather() or run_multiple_tools_concurrently()")
    
    try:
        # Start the server with specified transport
        if args.transport == 'sse':
            logger.info(f"Starting async SSE server on {args.host}:{args.port}")
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            mcp.run(transport="sse")
        else:
            # Default stdio transport
            mcp.run(transport="stdio")
    finally:
        # Clean up thread pool executor on shutdown
        logger.info("Cleaning up thread pool executor...")
        cleanup_executor()


if __name__ == "__main__":
    main()