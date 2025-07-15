from mcp.server.fastmcp import FastMCP
from typing import Any , Optional
import sys
import os
import aiofiles
import json
    
mcp = FastMCP(name="STM Agent",
              instructions="This is a STM to store user conversations.",
              port = 6000,
              host = "localhost"
)


@mcp.tool()
async def store_conversation(conversation_id: str,state: str, message: dict[str,Any]) -> dict[str,Any]:
    """
    This tool stores the conversation messages in a persistent storage.
    
    Args:
        conversation_id (str): Unique identifier for the conversation.
        state (str): Current state of the conversation.
        message (str): The message to be stored.
        
    Returns:
        dict: Confirmation of the stored message.
    """
    existing_data = {"conversation":[]}
    # Here you would implement the logic to store the message in a database or file
        # dir_path = os.path.abspath(f"./../storage/{conversation_id}")
        # file_path = os.path.join(dir_path, f"{state}.json")
    dir_path = os.path.abspath(f"./../storage/")
    file_path = os.path.join(dir_path, f"{conversation_id}.json")
    # print("dir_path:", dir_path)
    # print("file_path:", file_path)
    if os.path.exists(file_path):
        # print("extracting data")
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            if content:
                existing_data = json.loads(content)
    else:
        os.makedirs(dir_path, exist_ok=True)

    # print(existing_data)
    existing_data['conversation'].append(message)

    async with aiofiles.open(file_path, "w") as f:
        await f.write(json.dumps(existing_data, indent=4))
        
    print(f"Storing message for conversation {conversation_id}: {message}.")
    return {"status": "success", "conversation_id": conversation_id, "message": message}



@mcp.resource(uri="data://{conversation_id}/{state}/{messages}/get"
              ,mime_type="application/json",
              description="Get conversation messages from persistent storage",
              name="Get Conversation Messages")
async def get_conversation(conversation_id: str,state: str, messages: int | None = None) -> dict[str,Any]:
    """
    This resource retrieves the conversation messages from persistent storage.

    Args:
        conversation_id (str): Unique identifier for the conversation.
        state (str): Current state of the conversation.
        messages (int | None, optional): Number of messages to retrieve. If None, retrieves the last message.

    Returns:
        dict[str,Any]: A dictionary containing the status, conversation ID, state, and the requested messages.
        If messages is None, returns the last message in the specified state.
    """
    
    existing_data = {"conversation":[]}
    # Here you would implement the logic to store the message in a database or file
        # dir_path = os.path.abspath(f"./../storage/{conversation_id}")
        # file_path = os.path.join(dir_path, f"{state}.json")
    dir_path = os.path.abspath(f"./../storage/")
    file_path = os.path.join(dir_path, f"{conversation_id}.json")

    if os.path.exists(file_path):
        # print("extracting data")
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            if content:
                existing_data = json.loads(content)

        
    # print(f"Getting messages for conversation {conversation_id}: last {messages} messages in state {state}")
    return {"status": "success", "conversation_id": conversation_id, "state": state, "message": existing_data['conversation'][-int(min(len(existing_data['conversation']),messages)):] if messages else existing_data['conversation'][-1]}






# print(asyncio.run(get_conversation("test_conversation", "START")))
    
# test resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"
    
mcp.run(transport='streamable-http')