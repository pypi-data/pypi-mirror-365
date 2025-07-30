Axians MCP Server - Technical Documentation
Architecture Overview
The Axians MCP Server is built using the FastMCP framework and follows a modular architecture that makes it easy to extend with additional tools and services.

Core Components
axians_mcp/
├── __init__.py          # Entry point with CLI setup
├── servers/             # MCP server implementations
│   ├── __init__.py      # Server module exports
│   ├── main.py          # Main FastMCP server configuration
│   └── weather.py       # Weather service tools
Framework Integration
FastMCP Integration
The server uses FastMCP as its foundation:

python
from fastmcp import FastMCP

# Main server instance
main_mcp = FastMCP("Axians MCP")

# Weather service sub-server
weather_mcp = FastMCP(
    name="Weather MCP Service",
    description="Provides tools for interacting with Weather.gov."
)

# Mount weather service to main server
main_mcp.mount("weather", weather_mcp)
Tool Registration
Tools are registered using FastMCP decorators:

python
@weather_mcp.tool(tags={"weather"})
async def get_alerts(state: str) -> str:
    """Tool implementation"""
    pass
API Integration
National Weather Service API
The server integrates with the NWS API using the following patterns:

Base Configuration
python
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
HTTP Client Setup
python
headers = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json"
}
Request Pattern
python
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Standardized NWS API request with error handling"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
Available Tools
1. Weather Alerts Tool
Endpoint: /alerts/active/area/{state}

Function: get_alerts(state: str) -> str

Flow:

Validates state parameter (2-letter code)
Makes request to NWS alerts endpoint
Formats response data
Returns human-readable alert information
Response Format:

Event: {event_type}
Area: {affected_area}
Severity: {severity_level}
Description: {detailed_description}
Instructions: {safety_instructions}
2. Weather Forecast Tool
Endpoint: /points/{lat},{lon} → /forecast

Function: get_forecast(latitude: float, longitude: float) -> str

Flow:

First request to points endpoint to get forecast grid
Extract forecast URL from response
Second request to forecast endpoint
Format and return forecast periods
Response Format:

{Period Name}:
Temperature: {temp}°{unit}
Wind: {speed} {direction}
Forecast: {detailed_forecast}
Transport Support
The server supports multiple transport protocols:

STDIO Transport (Default)
Recommended for MCP client integration
Uses standard input/output for communication
Ideal for process-based communication
SSE (Server-Sent Events)
HTTP-based streaming
Suitable for web applications
Real-time updates capability
Streamable HTTP
HTTP streaming protocol
Good for REST-like integrations
Supports various HTTP clients
Configuration Management
Environment Variables
The server supports configuration via environment variables:

env
TRANSPORT=stdio          # Default transport method
LOG_LEVEL=INFO          # Logging level
CLI Configuration
Priority order: CLI arguments > Environment variables > Defaults

python
def _determine_transport(cli_transport: str, logger: logging.Logger) -> str:
    # CLI takes precedence over environment
    click_ctx = click.get_current_context(silent=True)
    if click_ctx and was_option_provided(click_ctx, "transport"):
        return cli_transport
    return os.getenv("TRANSPORT", "stdio").lower()
Error Handling
API Error Handling
The server implements robust error handling for external API calls:

python
async def make_nws_request(url: str) -> dict[str, Any] | None:
    try:
        response = await client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None  # Graceful degradation
Tool Error Responses
Tools return user-friendly error messages:

python
if not data or "features" not in data:
    return "Unable to fetch alerts or no alerts found."
Logging Configuration
Multi-level Logging
python
if verbose >= 2:
    log_level = logging.DEBUG
elif verbose == 1:
    log_level = logging.INFO
else:
    log_level = logging.WARNING
Logger Setup
python
def setup_logger(level: int) -> logging.Logger:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
Extension Guidelines
Adding New Tools
Create tool function with proper type hints
Add FastMCP decorator with appropriate tags
Implement error handling
Add to the appropriate service module
python
@weather_mcp.tool(tags={"weather"})
async def new_weather_tool(param: str) -> str:
    """New weather tool implementation"""
    try:
        # Implementation logic
        return result
    except Exception as e:
        return f"Error: {str(e)}"
Adding New Services
Create new service module in servers/
Create FastMCP instance for the service
Mount to main server in main.py
python
# In servers/new_service.py
new_service_mcp = FastMCP(name="New Service")

# In servers/main.py
main_mcp.mount("new_service", new_service_mcp)
Performance Considerations
Async/Await Pattern
All external API calls use async/await for non-blocking execution:

python
async with httpx.AsyncClient() as client:
    response = await client.get(url, headers=headers, timeout=30.0)
Connection Pooling
HTTPx automatically handles connection pooling within the async context manager.

Timeout Configuration
All requests include appropriate timeouts (30 seconds) to prevent hanging.

Security Considerations
API Rate Limiting
The NWS API has usage guidelines that should be respected:

Include proper User-Agent header
Reasonable request frequency
Handle rate limiting gracefully
Input Validation
All tool parameters are validated using Pydantic:

python
async def get_alerts(state: str) -> str:
    # FastMCP handles parameter validation automatically
Error Information Disclosure
Error messages are sanitized to avoid exposing sensitive information:

python
except Exception:
    return None  # Don't expose internal errors
Testing Strategy
Unit Testing
Test individual tools in isolation:

python
async def test_get_alerts():
    result = await get_alerts("CA")
    assert isinstance(result, str)
    assert len(result) > 0
Integration Testing
Test full MCP protocol communication:

python
async def test_mcp_protocol():
    # Test tool calls via MCP protocol
    pass
API Mocking
Mock external API calls for reliable testing:

python
@patch('httpx.AsyncClient.get')
async def test_api_failure(mock_get):
    mock_get.side_effect = httpx.HTTPError("API Error")
    result = await get_alerts("CA")
    assert "Unable to fetch" in result
Deployment
Docker Support
The server can be containerized for easy deployment:

dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["axians-mcp", "--transport=stdio"]
Production Considerations
Monitor API usage and respect rate limits
Implement proper logging and monitoring
Consider caching for frequently requested data
Use environment-specific configurations
