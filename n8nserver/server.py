import sys
import json
import uuid
sys.path.append(r"D:\OneDrive - Coforge Limited\Desktop\ForgeX\agent Chat\module")
from clients.stmhttp_client import MCPClient

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# add a post request endpoint 
@app.post("/data/")
async def receive_data(data: dict)-> dict:
    client = None
    messages = None
    state = data.get('state',str)
    _uuid = data.get('_uuid',str)
    try:
        # Process the received data here
        print(data)
        client = MCPClient()
        await client.connect_to_streamable_http_server("http://localhost:5050/mcp/")
        
        # print(await client.session.list_tools())
        
        # Extract the last user message as input
        messages = data.get('messages', [])
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        
        if not user_messages:
            return {"error": "No user message found"}
    
        
        # Call the tool with properly formatted input
        response = await client.session.call_tool(
            name="handle_prompt", 
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
    
            

# start the server on port 8080
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)