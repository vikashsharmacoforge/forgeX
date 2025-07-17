import json
import os
import sys
clients_path = os.path.abspath("../mcp-clients")
if clients_path not in sys.path:
    sys.path.append(clients_path)
from stmhttp_client import MCPClient



async def lightrag_query(prompt: str , domain: str ,user_prompt:str , history: list = []):
    

    context = ""
    try:
        client = MCPClient()
        await client.connect_to_streamable_http_server("http://localhost:6001/mcp/")
        
        context_res = await client.session.call_tool(
            name="lightrag_new_tool", 
            arguments={
                        "question": prompt,
                        "domain": domain,
                        "history": history,
                        "user_prompt": user_prompt
                    }
        )
        
        context = json.loads(context_res.content[0].text).get('LightRAG',str)
        # print("context:", context)
        return context
    finally:
        if client:
            await client.cleanup()