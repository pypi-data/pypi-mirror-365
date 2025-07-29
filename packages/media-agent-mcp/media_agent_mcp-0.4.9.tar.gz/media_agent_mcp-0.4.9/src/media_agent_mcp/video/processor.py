"""Video processing module.

This module provides video processing functionality including concatenation and frame extraction.
"""

import asyncio
import json
import logging
import os
import tempfile
import time
import uuid
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import cv2
import requests

from media_agent_mcp.storage.tos_client import upload_to_tos

logger = logging.getLogger(__name__)


def download_video_from_url(url: str) -> Dict[str, Any]:
    """Download video from URL to a temporary file.
    
    Args:
        url: URL of the video to download
        
    Returns:
        JSON response with status, data (file path), and message
    """
    try:
        # Parse URL to get file extension
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.mp4'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download the video
        logger.info(f"Downloading video from {url}...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Video downloaded to {temp_path}")
        return {
            "status": "success",
            "data": {"file_path": temp_path},
            "message": "Video downloaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error downloading video from {url}: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading video from {url}: {e}"
        }


def concat_videos(video_urls: list, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Concatenate multiple videos into one.
    
    Args:
        video_urls: List of URLs or paths to video files to concatenate in order
        output_path: Optional output path for the concatenated video
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_files = []
    video_captures = []
    
    try:
        if not video_urls or len(video_urls) == 0:
            return {
                "status": "error",
                "data": None,
                "message": "No video URLs provided"
            }
            
        if not output_path:
            output_path = f"concatenated_{int(time.time())}.mp4"
        
        # Download videos if they are URLs and prepare local paths
        video_paths = []
        for video_input in video_urls:
            if video_input.startswith(('http://', 'https://')):
                download_result = download_video_from_url(video_input)
                if download_result["status"] == "error":
                    return download_result
                video_path = download_result["data"]["file_path"]
                temp_files.append(video_path)
                video_paths.append(video_path)
            elif os.path.exists(video_input):
                video_paths.append(video_input)
            else:
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Video file {video_input} not found"
                }
        
        # Open all video captures
        for video_path in video_paths:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Could not open video {video_path}"
                }
            video_captures.append(cap)
        
        # Get video properties from the first video
        first_cap = video_captures[0]
        fps = first_cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            logger.warning("Invalid FPS detected, setting to 30.")
            fps = 30
        else:
            fps = int(fps)
        width = int(first_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(first_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create video writer with H.264 codec for better compatibility
        logger.info("Initializing video writer with 'avc1' (H.264) codec.")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Check if video writer was initialized successfully
        if not out.isOpened():
            logger.warning("Failed to initialize video writer with 'avc1' codec. Falling back to 'mp4v'.")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if not out.isOpened():
                logger.warning("Failed to initialize video writer with 'mp4v' codec. Falling back to 'XVID'.")
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                if not out.isOpened():
                    logger.error("Failed to initialize video writer with 'avc1', 'mp4v', or 'XVID' codecs.")
                    return {
                        "status": "error",
                        "data": None,
                        "message": "Could not initialize video writer with any of the supported codecs."
                    }
        logger.info("Video writer initialized successfully.")
        
        # Write frames from all videos in order
        for i, cap in enumerate(video_captures):
            logger.info(f"Processing video {i+1}/{len(video_captures)}...")
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                # Resize frame if dimensions don't match the first video
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))
                out.write(frame)
        
        # Release everything
        for cap in video_captures:
            cap.release()
        out.release()
        
        logger.info(f"Videos concatenated successfully: {output_path}")
        
        # Upload concatenated video to TOS
        try:
            tos_url = upload_to_tos(output_path)
            logger.info(f"Video uploaded to TOS: {tos_url}")
            
            # Clean up local concatenated file
            try:
                os.unlink(output_path)
                logger.info(f"Cleaned up local concatenated file: {output_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up local file {output_path}: {e}")
            
            return {
                "status": "success",
                "data": {"tos_url": tos_url},
                "message": "Videos concatenated and uploaded successfully"
            }
        except Exception as e:
            logger.error(f"Error uploading to TOS: {e}")
            return {
                "status": "error",
                "data": None,
                "message": f"Error uploading to TOS: {str(e)}"
            }
        
    except Exception as e:
        logger.error(f"Error concatenating videos: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error concatenating videos: {str(e)}"
        }
    finally:
        # Release any remaining video captures
        for cap in video_captures:
            if cap.isOpened():
                cap.release()
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")


def extract_last_frame(video_input: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract the last frame from a video as an image and upload to TOS.
    
    Args:
        video_input: URL or path to the video file
        output_path: Optional output path for the extracted frame
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_video_file = None
    
    try:
        # Handle URL or local file path
        if video_input.startswith(('http://', 'https://')):
            # Download video from URL
            download_result = download_video_from_url(video_input)
            if download_result["status"] == "error":
                return download_result
            video_path = download_result["data"]["file_path"]
            temp_video_file = video_path
        elif os.path.exists(video_input):
            video_path = video_input
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Video file {video_input} not found"
            }
        
        if not output_path:
            output_path = f"last_frame_{uuid.uuid4().hex}.jpg"
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                "status": "error",
                "data": None,
                "message": f"Could not open video {video_path}"
            }
        
        # Get total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Video has no frames"
            }
        
        # Set position to last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        
        # Read the last frame
        ret, frame = cap.read()
        
        if ret:
            # Save the frame
            cv2.imwrite(output_path, frame)
            cap.release()
            logger.info(f"Last frame extracted: {output_path}")
            
            # Upload frame to TOS
            try:
                tos_url = upload_to_tos(output_path)
                logger.info(f"Frame uploaded to TOS: {tos_url}")
                
                # Clean up local frame file
                try:
                    os.unlink(output_path)
                    logger.info(f"Cleaned up local frame file: {output_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up local file {output_path}: {e}")
                
                return {
                    "status": "success",
                    "data": {"tos_url": tos_url},
                    "message": "Last frame extracted and uploaded successfully"
                }
            except Exception as e:
                logger.error(f"Error uploading frame to TOS: {e}")
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error uploading to TOS: {str(e)}"
                }
        else:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Could not read the last frame"
            }
            
    except Exception as e:
        logger.error(f"Error extracting last frame: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error extracting last frame: {str(e)}"
        }
    finally:
        # Clean up temporary video file if downloaded
        if temp_video_file and os.path.exists(temp_video_file):
            try:
                os.unlink(temp_video_file)
                logger.info(f"Cleaned up temporary video file: {temp_video_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary video file {temp_video_file}: {e}")


if __name__ == '__main__':
    # Example usage
    video_urls = [
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4",
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205817458400000000000000000000ffffc0a850948120ae.mp4"
    ]

    concatenated_video = concat_videos(video_urls)
    print(f"Concatenated video URL: {concatenated_video}")

    last_frame_url = extract_last_frame(video_urls[0])
    print(f"Last frame URL: {last_frame_url}")