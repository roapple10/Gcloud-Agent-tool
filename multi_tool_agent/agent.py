"""
GCP Assistant Agent
This is the main agent module that integrates all GCP assistant functionality.
"""

from google.adk.agents import Agent
import asyncio
import json
from typing import Dict, Any

# Import our modular components
from .gcp_tool import gcp_tool

# Create the agent with all tools
root_agent = Agent(
    name="gcp_assistant",
    model="gemini-2.0-flash",
    description="Assistant that can provide weather, time information, and interact with Google Cloud Platform.",
    instruction="""
    I can answer questions about Google Cloud Platform resources.
    
    When I encounter queries about GCP that I don't understand, I will suggest gcloud commands that might help.
    These suggestions will be presented as alternative commands that the user can try.
    """,
    tools=[gcp_tool]
)

# Create a wrapper function to handle the agent's responses
async def enhanced_gcp_agent(user_query: str) -> Dict[str, Any]:
    """
    Wrapper for the root_agent that processes the agent's response and includes suggested commands when appropriate.
    
    Args:
        user_query: The user's query.
        
    Returns:
        Dict[str, Any]: A dictionary with the processed response.
    """
    # Process natural language query or direct gcloud command
    response = await root_agent.generate_response(user_query)
    
    # Process the response to include suggested commands if present
    if isinstance(response, dict):
        # If this is a response from gcp_tool
        if "status" in response:
            if response["status"] == "error" and "suggested_commands" in response:
                # Include suggested commands in the response
                return {
                    "status": "error",
                    "message": f"{response['error_message']}\n\n{response['suggested_commands']}"
                }
            elif response["status"] == "success" and "report" in response:
                return {
                    "status": "success",
                    "message": response["report"]
                }
            elif "result" in response:
                # Format result in a readable way
                if isinstance(response["result"], list):
                    formatted_result = "\n".join([json.dumps(item, indent=2) for item in response["result"]])
                else:
                    formatted_result = json.dumps(response["result"], indent=2) if isinstance(response["result"], (dict, list)) else str(response["result"])
                
                return {
                    "status": "success",
                    "message": formatted_result
                }
            elif "error_message" in response:
                return {
                    "status": "error", 
                    "message": response["error_message"]
                }
    
    # Return the original response if no processing was needed
    return {
        "status": "success",
        "message": response if isinstance(response, str) else json.dumps(response, indent=2)
    }

# Export the enhanced agent as the main agent
gcp_assistant = enhanced_gcp_agent