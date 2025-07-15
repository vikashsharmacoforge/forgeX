import os
import sys
import asyncio
import json
clients_path = os.path.abspath("./src/mcp-clients")
# rag_path = os.path.abspath("/src/memory/lightrag")
sys.path.append(clients_path)
from stmhttp_client import MCPClient
# sys.append(rag_path)



async def call_tool_():
    try:
        client = MCPClient()
        await client.connect_to_streamable_http_server("http://localhost:6001/mcp/")
        print( await client.session.list_tools())
        response = await client.session.call_tool(
            name="lightrag_new_tool", 
            arguments={
                        "domain": "Project Management",
                        "question": "what is rates hub? explain in brief",
                        "history": []
                    }
        )
        
        print("response:" , json.loads(response.content[0].text).get('LightRAG',str))
    finally:
        if client:
            await client.cleanup()
    

asyncio.run(call_tool_())
