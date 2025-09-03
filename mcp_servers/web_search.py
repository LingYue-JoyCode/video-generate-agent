from pydantic_ai.mcp import MCPServerSSE
import dotenv
import os

dotenv.load_dotenv(".env")

tavilyApi = os.getenv("TAVILY_API") or ''

web_search_tools = MCPServerSSE(url=tavilyApi)
