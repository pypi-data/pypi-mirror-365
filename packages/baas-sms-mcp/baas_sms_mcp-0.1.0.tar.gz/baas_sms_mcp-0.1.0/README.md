# BaaS SMS/MCP Server

[![PyPI version](https://badge.fury.io/py/baas-sms-mcp.svg)](https://badge.fury.io/py/baas-sms-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for SMS and MMS messaging services. This server provides tools for sending SMS/MMS messages, checking message status, and retrieving sending history through BaaS API integration.

## Features

- **SMS Sending**: Send SMS messages to single or multiple recipients
- **MMS Sending**: Send MMS messages with image attachments  
- **Message Status**: Check sending status of message groups
- **Send History**: Retrieve message sending history for projects
- **Project Isolation**: Multi-tenant support with project-based access control
- **Error Handling**: Comprehensive error handling with detailed error codes

## Installation

### Using uv (Recommended)

```bash
uv add baas-sms-mcp
```

### Using pip

```bash
pip install baas-sms-mcp
```

### From Source

```bash
git clone https://github.com/your-org/baas-sms-mcp.git
cd baas-sms-mcp
uv sync
uv pip install -e .

## Configuration

Set the following environment variables:

```bash
export BAAS_API_BASE_URL="https://api.aiapp.link"
export BAAS_API_KEY="your_baas_api_key_here"  
export PROJECT_ID="your_project_uuid_here"
```

## Usage

### Command Line

After installation, you can run the server directly:

```bash
baas-sms-mcp
```

### With MCP Host (Claude Desktop, etc.)

Add this server to your MCP host configuration:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "baas-sms-mcp",
      "env": {
        "BAAS_API_BASE_URL": "https://api.aiapp.link",
        "BAAS_API_KEY": "your_api_key",
        "PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

### Programmatic Usage

```python
from baas_sms_mcp import main

# Run the MCP server
main()
```

## Available Tools

### 1. send_sms

Send SMS message to one or multiple recipients.

**Parameters:**
- `recipients`: List of recipients with `phone_number` and `member_code`
- `message`: SMS message content (max 2000 characters)
- `callback_number`: Sender callback number
- `project_id`: Project UUID (required)
- `baas_api_key`: BaaS API key for authentication (required)

**Example:**
```python
await send_sms(
    recipients=[
        {"phone_number": "010-1234-5678", "member_code": "user123"}
    ],
    message="Hello, this is a test SMS!",
    callback_number: "02-1234-5678"
)
```

**Response:**
```json
{
    "success": true,
    "group_id": 12345,
    "message": "SMS sent successfully",
    "sent_count": 1,
    "failed_count": 0
}
```

### 2. send_mms

Send MMS message with images to one or multiple recipients.

**Parameters:**
- `recipients`: List of recipients with `phone_number` and `member_code`
- `message`: MMS message content (max 2000 characters)
- `subject`: MMS subject line (max 40 characters)
- `callback_number`: Sender callback number
- `image_urls`: List of image URLs to attach (max 5 images, optional)
- `project_id`: Project UUID (optional, uses env var if not provided)

**Example:**
```python
await send_mms(
    recipients=[
        {"phone_number": "010-1234-5678", "member_code": "user123"}
    ],
    message="Check out this image!",
    subject: "Image MMS",
    callback_number: "02-1234-5678",
    image_urls: ["https://example.com/image.jpg"]
)
```

### 3. get_message_status

Get message sending status by group ID.

**Parameters:**
- `group_id`: Message group ID to check status

**Response:**
```json
{
    "group_id": 12345,
    "status": "1�",
    "total_count": 1,
    "success_count": 1,
    "failed_count": 0,
    "pending_count": 0,
    "messages": [
        {
            "phone": "010-1234-5678",
            "name": "���",
            "status": "1�",
            "reason": null
        }
    ]
}
```

### 4. get_send_history

Get message sending history for a project.

**Parameters:**
- `project_id`: Project UUID (optional, uses env var if not provided)
- `offset`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 20, max: 100)
- `message_type`: Filter by message type ("SMS", "MMS", "ALL")

## Error Handling

The server provides comprehensive error handling with the following error codes:

- `MISSING_PROJECT_ID`: PROJECT_ID is required
- `INVALID_RECIPIENTS_COUNT`: Recipients count must be between 1 and 1000
- `MESSAGE_TOO_LONG`: Message length exceeds maximum allowed
- `SUBJECT_TOO_LONG`: Subject length exceeds 40 characters
- `TOO_MANY_IMAGES`: Maximum 5 images allowed for MMS
- `API_ERROR`: External API call failed
- `INTERNAL_ERROR`: Internal server error

## API Integration

This MCP server integrates with the BaaS API endpoints:

- `POST /message/sms` - Send SMS messages
- `POST /message/mms` - Send MMS messages  
- `GET /message/send_history/sms/{group_id}/messages` - Get message status

## Development

### Installing Development Dependencies

```bash
uv sync --group dev
```

### Code Formatting

```bash
uv run black baas_sms_mcp/
```

### Type Checking

```bash
uv run mypy baas_sms_mcp/
```

### Testing

```bash
uv run pytest
```

### Building Package

```bash
uv build
```

### Publishing to PyPI

```bash
uv publish
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For support and questions, please contact: support@aiapp.link