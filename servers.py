from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio
import os
from dotenv import load_dotenv

load_dotenv() 

BACKEND_SERVER_URL = os.getenv("BACKEND_SERVER_URL", "http://localhost:8081")

# https://github.com/dbrown725/mcp-human-resources
# Server running on laptop
mcp_human_resources_server = MCPServerSSE(url=f"{BACKEND_SERVER_URL}/sse")

# https://github.com/microsoft/playwright-mcp
playwright_mcp_server = MCPServerStdio(
    command= "npx",
    args=[
        "@playwright/mcp@latest",
        ]
)

# https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem
filesystem_mcp_server = MCPServerStdio(
    command= "npx",
    args=[
        "@modelcontextprotocol/server-filesystem",
        os.getenv('LOCAL_FILE_STORAGE'),
        ]
)
