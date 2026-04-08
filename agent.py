"""
========================================================
AGENT LAYER (BRAIN OF SYSTEM)
========================================================

This is where:
- User query is processed
- Tools are used
- Final answer is generated

We use:
✔ Local tools (search/filter)
✔ MCP tools (Google Maps)

========================================================
"""

import os
import dotenv
from google.adk.agents import LlmAgent
from .tools import TOOLS, get_maps_mcp_toolset


# ------------------------------------------------------
# Load environment variables
# ------------------------------------------------------
dotenv.load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "not_set")


# ------------------------------------------------------
# Initialize MCP Toolset (Maps)
# ------------------------------------------------------
maps_toolset = get_maps_mcp_toolset()


# ------------------------------------------------------
# LOCAL TOOL WRAPPER
# ------------------------------------------------------
def handle_query(query: str):
    """
    This function handles:
    - Property search
    - Filtering
    - Formatting output

    NOTE:
    Maps will be handled by MCP tool automatically
    """

    # Step 1: Extract filters
    location, _ = TOOLS["extract"](query)

    # Step 2: Search properties
    results = TOOLS["search"](query)

    # Step 3: Filter results
    results = TOOLS["filter"](results, location)

    # Step 4: Remove duplicates
    results = TOOLS["dedupe"](results)

    # Step 5: Format response
    if not results:
        return "No matching projects found."

    response = "Here are some relevant projects:\n\n"

    for r in results[:5]:
        response += f"• {r['name']}\n{r['link']}\n\n"

    # Hint for LLM to use Maps MCP tool
    if location:
        response += f"\nYou can explore these in {location} using maps.\n"

    return response


# ------------------------------------------------------
# ROOT AGENT (ENTRY POINT)
# ------------------------------------------------------
root_agent = LlmAgent(
    model="gemini-3.1-pro-preview",

    name="real_estate_agent",

    instruction=f"""
You are an intelligent real estate assistant.

You have access to:
1. Local tools → for searching properties
2. Google Maps MCP tool → for location insights

Rules:
- Always give useful project results
- Avoid duplicates
- If location is present → use Maps tool
- Provide map links when helpful
""",

    # 🔥 IMPORTANT: BOTH tools added
    tools=[handle_query, maps_toolset],
)
