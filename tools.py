"""
========================================================
TOOLS LAYER (GOOGLE MCP STYLE)
========================================================

This file defines ALL tools used by the agent.

Two types of tools:
1. Local tools (Python functions)
2. MCP tools (Google Maps via API)

WHY THIS DESIGN?
✔ Separation of concerns
✔ Easy to extend
✔ Enterprise-ready

========================================================
"""

import os
import re
import dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# MCP imports (Google official)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams


# ------------------------------------------------------
# STEP 1: Load environment variables
# ------------------------------------------------------
dotenv.load_dotenv()

# Get API key securely from .env file
MAPS_API_KEY = os.getenv("MAPS_API_KEY", "no_key_found")

# Google hosted MCP endpoint
MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"


# ------------------------------------------------------
# STEP 2: Create MCP Toolset (Google Maps)
# ------------------------------------------------------
def get_maps_mcp_toolset():
    """
    PURPOSE:
    Create a connection to Google Maps MCP server

    WHY?
    - No need to run your own server
    - Google manages everything
    """

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,

            # API Key passed securely in header
            headers={
                "X-Goog-Api-Key": MAPS_API_KEY
            },

            # Timeout settings
            timeout=30.0,
            sse_read_timeout=300.0
        )
    )

    print("✅ Maps MCP Toolset initialized")

    return tools


# ------------------------------------------------------
# LOCAL TOOL: Tavily Search
# ------------------------------------------------------
tavily_tool = TavilySearchResults(max_results=10)


# ------------------------------------------------------
# TOOL 1: Extract Filters
# ------------------------------------------------------
def extract_filters(query: str):
    """
    Extract location and budget from user query

    Example:
    "2BHK in Whitefield under 80 lakh"
    """

    query_lower = query.lower()

    location = None
    budget = None

    # Extract location after "in"
    if " in " in query_lower:
        location = query_lower.split(" in ")[-1].strip()

    # Extract budget using regex
    match = re.search(r'(\d+)\s*(cr|crore|lakh|lac)', query_lower)

    if match:
        value = int(match.group(1))
        unit = match.group(2)

        if "cr" in unit:
            budget = value * 10000000
        elif "lakh" in unit or "lac" in unit:
            budget = value * 100000

    return location, budget


# ------------------------------------------------------
# TOOL 2: Search Properties
# ------------------------------------------------------
def search_tool(query: str):
    """
    Use Tavily to fetch real estate projects
    """

    try:
        if "project" not in query.lower():
            query += " real estate projects apartments builders"

        results = tavily_tool.invoke({"query": query})

        projects = []

        for r in results:
            projects.append({
                "name": r.get("title", ""),
                "link": r.get("url", ""),
                "description": r.get("content", "")
            })

        return projects

    except Exception as e:
        return [{"error": str(e)}]


# ------------------------------------------------------
# TOOL 3: Filter Results
# ------------------------------------------------------
def filter_tool(results, location):
    """
    Keep only results matching location
    """

    if not location:
        return results

    return [
        r for r in results
        if location.lower() in (r["name"] + r["description"]).lower()
    ]


# ------------------------------------------------------
# TOOL 4: Remove Duplicates
# ------------------------------------------------------
def dedupe_tool(results):
    """
    Remove duplicate project names
    """

    seen = set()
    unique = []

    for r in results:
        if r["name"] not in seen:
            seen.add(r["name"])
            unique.append(r)

    return unique


# ------------------------------------------------------
# TOOL REGISTRY
# ------------------------------------------------------
TOOLS = {
    "extract": extract_filters,
    "search": search_tool,
    "filter": filter_tool,
    "dedupe": dedupe_tool,
}
