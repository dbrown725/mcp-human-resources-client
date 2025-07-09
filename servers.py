from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio
import os

# https://github.com/dbrown725/mcp-human-resources
# Server running on laptop
mcp_human_resources_server = MCPServerSSE(url="http://localhost:8081/sse")

# https://github.com/microsoft/playwright-mcp
playwright_mcp_server = MCPServerStdio(
    command= "npx",
    args=[
        "@playwright/mcp@latest",
        ]
)
