from fastmcp import FastMCP
from .weather import weather_mcp
from .iceland import iceland_mcp


main_mcp = FastMCP("Axians MCP")
main_mcp.mount("weather", weather_mcp)
main_mcp.mount("iceland", iceland_mcp)