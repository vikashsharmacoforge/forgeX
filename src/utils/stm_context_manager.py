import sys
import os
clients_path = os.path.abspath("../mcp-clients")
if clients_path not in sys.path:
    sys.path.append(clients_path)
from stmhttp_client import MCPClient
from typing import Any
import asyncio
import json


async def store_messages(_uuid:str , state: str , response: dict[str,Any] , persona: dict[str,Any] | None = None) -> None:
    "Store messages in the STM server."
    try:
        client_stm = MCPClient()
        await client_stm.connect_to_streamable_http_server("http://localhost:6000/mcp/")

        # available_tools = await client_stm.session.list_tools()
        # print("Available tools:", available_tools)
    # Call the tool with properly formatted input
        await client_stm.session.call_tool("store_conversation",{"conversation_id": _uuid, "state": state, "message": response, "persona": persona})
    except Exception as e:
        print(f"Error storing messages in STM: {e}")
        raise e
    finally:
        if client_stm:
            await client_stm.cleanup()
            
    
async def get_conversation(_uuid:str , state: str , messages: int = 1 , persona: int = 0) -> dict[str, Any]:
    """
    Retrieve the conversation messages from persistent storage.

    Args:
        _uuid (str): Unique identifier for the conversation.
        state (str): Current state of the conversation.
        messages (int | None, optional): Number of messages to retrieve. If None, retrieves the last message.

    Returns:
        dict: The conversation messages.
    """
    try:
        client_stm = MCPClient()
        await client_stm.connect_to_streamable_http_server("http://localhost:6000/mcp/")
        response = await client_stm.session.read_resource(f"data://{_uuid}/{state}/{messages}/{persona}/get")
        persona_res = json.loads(response.contents[0].text).get("persona",{})
        message = json.loads(response.contents[0].text).get("message",[])
        response = {"response": message}
        if persona:
            response['persona'] = persona_res
        return response
    except Exception as e:
        print(f"Error retrieving stm wrapper conversation: {e}")
        return {"error": "Failed to retrieve conversation"}
    finally:
        if client_stm:
            await client_stm.cleanup()


# print(asyncio.run(get_conversation("test_conversation","START",4,1)))
# asyncio.run(store_messages("test_conversation","START",{"role":"user","content":"hi"},{
# "Project_Requirement": 
#     {
#         "Project_Name": "Nova has to have Analytics",
#         "project_description": "its a secret project",
#     },
# "User_Story":
#     {
#         "User_Story_Tools": ["ClickUp"]
#     }
# }))