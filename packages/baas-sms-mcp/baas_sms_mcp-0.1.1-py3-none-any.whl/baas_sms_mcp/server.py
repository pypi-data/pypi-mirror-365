#!/usr/bin/env python3
"""
BaaS SMS/MMS MCP Server

Model Context Protocol server for SMS and MMS messaging services.
This server provides tools for sending SMS/MMS messages, checking message status,
and retrieving sending history through BaaS API integration.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Create the FastMCP instance for SMS/MMS messaging service
mcp = FastMCP("baas-mcp")

# Configuration
API_BASE_URL = os.getenv("BAAS_API_BASE_URL", "https://api.aiapp.link")
BAAS_API_KEY = os.getenv("BAAS_API_KEY", "")
PROJECT_ID = os.getenv("PROJECT_ID", "")

# HTTP client setup
client = httpx.AsyncClient(timeout=30.0)

@mcp.tool()
async def send_sms(
    recipients: List[Dict[str, str]],
    message: str,
    callback_number: str,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send SMS message to one or multiple recipients
    
    Args:
        recipients: List of recipients with phone_number and member_code
        message: SMS message content (max 2000 characters)
        callback_number: Sender callback number
        project_id: Project UUID (optional, uses env var if not provided)
    
    Returns:
        Dictionary with success status, group_id, and sending statistics
    """
    try:
        # Use provided project_id or fallback to environment variable
        current_project_id = project_id or PROJECT_ID
        if not current_project_id:
            return {
                "success": False,
                "error": "PROJECT_ID is required",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate input
        if not recipients or len(recipients) > 1000:
            return {
                "success": False,
                "error": "Recipients count must be between 1 and 1000",
                "error_code": "INVALID_RECIPIENTS_COUNT"
            }
        
        if len(message) > 2000:
            return {
                "success": False,
                "error": "Message length exceeds 2000 characters",
                "error_code": "MESSAGE_TOO_LONG"
            }
        
        # Prepare API request
        payload = {
            "recipients": recipients,
            "message": message,
            "callback_number": callback_number,
            "project_id": current_project_id,
            "channel_id": 1  # SMS channel
        }
        
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call
        response = await client.post(
            f"{API_BASE_URL}/message/sms",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "group_id": result["data"]["group_id"],
                    "message": "SMS sent successfully",
                    "sent_count": len(recipients),
                    "failed_count": 0
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API call failed with status {response.status_code}",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to send SMS: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def send_mms(
    recipients: List[Dict[str, str]],
    message: str,
    subject: str,
    callback_number: str,
    image_urls: Optional[List[str]] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send MMS message with images to one or multiple recipients
    
    Args:
        recipients: List of recipients with phone_number and member_code
        message: MMS message content (max 2000 characters)
        subject: MMS subject line (max 40 characters)
        callback_number: Sender callback number
        image_urls: List of image URLs to attach (max 5 images)
        project_id: Project UUID (optional, uses env var if not provided)
        
    Returns:
        Dictionary with success status, group_id, and sending statistics
    """
    try:
        # Use provided project_id or fallback to environment variable
        current_project_id = project_id or PROJECT_ID
        if not current_project_id:
            return {
                "success": False,
                "error": "PROJECT_ID is required",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate input
        if not recipients or len(recipients) > 1000:
            return {
                "success": False,
                "error": "Recipients count must be between 1 and 1000",
                "error_code": "INVALID_RECIPIENTS_COUNT"
            }
        
        if len(message) > 2000:
            return {
                "success": False,
                "error": "Message length exceeds 2000 characters",
                "error_code": "MESSAGE_TOO_LONG"
            }
        
        if len(subject) > 40:
            return {
                "success": False,
                "error": "Subject length exceeds 40 characters",
                "error_code": "SUBJECT_TOO_LONG"
            }
        
        if image_urls and len(image_urls) > 5:
            return {
                "success": False,
                "error": "Maximum 5 images allowed",
                "error_code": "TOO_MANY_IMAGES"
            }
        
        # Prepare API request
        payload = {
            "recipients": recipients,
            "message": message,
            "subject": subject,
            "callback_number": callback_number,
            "project_id": current_project_id,
            "channel_id": 3,  # MMS channel
            "img_url_list": image_urls or []
        }
        
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call
        response = await client.post(
            f"{API_BASE_URL}/message/mms",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "group_id": result["data"]["group_id"],
                    "message": "MMS sent successfully",
                    "sent_count": len(recipients),
                    "failed_count": 0
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API call failed with status {response.status_code}",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to send MMS: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def get_message_status(group_id: int) -> Dict[str, Any]:
    """
    Get message sending status by group ID
    
    Args:
        group_id: Message group ID to check status
        
    Returns:
        Dictionary with group status and individual message details
    """
    try:
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Make API call to get message status
        response = await client.get(
            f"{API_BASE_URL}/message/send_history/sms/{group_id}/messages",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                messages = result.get("data", [])
                
                # Calculate statistics
                total_count = len(messages)
                success_count = sum(1 for msg in messages if msg.get("result") == "성공")
                failed_count = sum(1 for msg in messages if msg.get("result") == "실패")
                pending_count = total_count - success_count - failed_count
                
                # Determine overall status
                if pending_count > 0:
                    status = "전송중"
                elif failed_count == 0:
                    status = "성공"
                else:
                    status = "실패" if success_count == 0 else "부분성공"
                
                return {
                    "group_id": group_id,
                    "status": status,
                    "total_count": total_count,
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "pending_count": pending_count,
                    "messages": [
                        {
                            "phone": msg.get("phone", ""),
                            "name": msg.get("name", ""),
                            "status": msg.get("result", ""),
                            "reason": msg.get("reason")
                        }
                        for msg in messages
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Failed to get message status"),
                    "error_code": result.get("error_code", "UNKNOWN_ERROR")
                }
        else:
            return {
                "success": False,
                "error": f"API call failed with status {response.status_code}",
                "error_code": "API_ERROR"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get message status: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

@mcp.tool()
async def get_send_history(
    project_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
    message_type: str = "ALL"
) -> Dict[str, Any]:
    """
    Get message sending history for a project
    
    Args:
        project_id: Project UUID (optional, uses env var if not provided)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 20, max: 100)
        message_type: Filter by message type ("SMS", "MMS", "ALL")
        
    Returns:
        Dictionary with sending history data
    """
    try:
        # Use provided project_id or fallback to environment variable
        current_project_id = project_id or PROJECT_ID
        if not current_project_id:
            return {
                "success": False,
                "error": "PROJECT_ID is required",
                "error_code": "MISSING_PROJECT_ID"
            }
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        if message_type not in ["SMS", "MMS", "ALL"]:
            message_type = "ALL"
        
        headers = {
            "Authorization": f"Bearer {BAAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        params = {
            "offset": offset,
            "limit": limit,
            "message_type": message_type
        }
        
        # Make API call (Note: This endpoint needs to be implemented in the API)
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "project_id": current_project_id,
                "total_count": 0,
                "offset": offset,
                "limit": limit,
                "message_type": message_type,
                "history": []
            },
            "message": "Send history endpoint not yet implemented in API"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get send history: {str(e)}",
            "error_code": "INTERNAL_ERROR"
        }

# Cleanup function to close HTTP client
async def cleanup():
    await client.aclose()

def main():
    """Main entry point for the BaaS SMS/MCP server."""
    print("Starting BaaS SMS/MMS MCP Server...")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Project ID: {PROJECT_ID}")
    
    try:
        mcp.run(transport="stdio")
    finally:
        import asyncio
        asyncio.run(cleanup())

# Run the server if the script is executed directly
if __name__ == "__main__":
    main()