import sys
import json
import os
clients_path = os.path.abspath("../mcp-clients")
if clients_path not in sys.path:
    sys.path.append(clients_path)
from stmhttp_client import MCPClient
from typing import Any


async def connect_to_mcp_agent(data:dict , url: str , tool_name: str)-> dict[str, Any]:
    client = None
    messages = None
    state = data.get('state',str)
    _uuid = data.get('_uuid',str)
    try:
        # Process the received data here
        print(data)
        client = MCPClient()
        await client.connect_to_streamable_http_server(url)
        
        # print(await client.session.list_tools())
        
        # Extract the last user message as input
        messages = data.get('messages', [])
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        
        if not user_messages:
            return {"error": "No user message found"}
    
        
        # Call the tool with properly formatted input
        response = await client.session.call_tool(
            name=tool_name, 
            arguments={"prompt": user_messages[-1].get("content",str),
                        "state": state,
                        "uuid": _uuid
                    }
        )
        # Extract text from the response
        print(response)
        state = (json.loads(response.content[0].text).get('state', str))
        print("new_state:",state)
        
        return {"response" :{'state':state , "_uuid":_uuid}}
    finally:
        if client:
            await client.cleanup()
