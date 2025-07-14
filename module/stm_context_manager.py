from clients.stmhttp_client import MCPClient
from typing import Any
import asyncio
import json


async def store_messages(_uuid:str , state: str , response: dict[str,Any])-> None:
    "Store messages in the STM server."
    try:
        client_stm = MCPClient()
        await client_stm.connect_to_streamable_http_server("http://localhost:6000/mcp/")
        # available_tools = await client_stm.session.list_tools()
        # print("Available tools:", available_tools)
    # Call the tool with properly formatted input
        await client_stm.session.call_tool("store_conversation",{"conversation_id": _uuid, "state": state, "message": response})
    finally:
        if client_stm:
            await client_stm.cleanup()
    
async def get_conversation(_uuid:str , state: str , messages: int = 1) -> dict[str, Any]:
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
        response = await client_stm.session.read_resource(f"data://{_uuid}/{state}/{messages}/get")
        message = json.loads(response.contents[0].text)["message"]
        return {"response": message}
    finally:
        if client_stm:
            await client_stm.cleanup()


# asyncio.run(get_conversation("test_conversation","START",4))