from fastapi import FastAPI
import os
import sys
sys.path.append(os.path.abspath("../utils"))
from agents_wrapper import connect_to_mcp_agent
app = FastAPI()





@app.get("/")
async def root():
    return {"message": "Hello World"}

# add a post request endpoint 
@app.post("/data/START")
async def receive_data(data: dict)-> dict:
    return await connect_to_mcp_agent(data, "http://localhost:5050/mcp/" , "handle_prompt")
                    
@app.post("/data/CUS")
async def receive_data(data: dict)-> dict:
    return await connect_to_mcp_agent(data, "http://localhost:5051/mcp/" , "create_user_stories")
    
@app.post("/data/HITL")
async def receive_data(data: dict)-> dict:
    return await connect_to_mcp_agent(data, "http://localhost:5052/mcp/" , "hitl")

# start the server on port 8080
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)