import sys    
import os  
llm_path = os.path.abspath("../llm")
if llm_path not in sys.path:
    sys.path.append(llm_path)
utils = os.path.abspath("../utils")
if utils not in sys.path:
    sys.path.append(utils)
from mcp.server.fastmcp import FastMCP
from customllm import CustomLLM 
from stm_context_manager import store_messages, get_conversation
from typing import Any


llm = CustomLLM()


mcp = FastMCP(name = "Project Requirements Get Assistant", 
              instructions="Get project requirements from the user",
              port = 5051,
              host ="localhost"
            )

msgs = 6


@mcp.tool()
async def create_user_stories(prompt: str , state: str , uuid: str)-> dict[str, Any]:
    """
    This tool helps create user stories based on the provided project requirements.
    Args:
        prompt (str): project requirements input
        state (str): current state of the project
        uuid (str): unique identifier for the request
        
    Returns:
        dict : dictionary containing the updated state as response.
    """
    sys_prompt = """
    You are a helpful assistant that helps create user storeis form the input project requirements.
    Analyse the project requirements and the collect functional and non-functional requirements.
    Once all the requirements are extracted , generate user stories based on these requirements.
    """
    # get the conversation messages from persistent storage
    history  = []
    try:
        conversation = await get_conversation(uuid , state , msgs )
        history = conversation.get("response", [])
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return {"error": "Failed to retrieve conversation"}
    
    
    response = llm.invoke(sys_prompt=sys_prompt,input = prompt , history = history[:-1])
    print({"response": response})
    
    try:
        await  store_messages(uuid , state , {"role":"assistant","content": response})  
    except Exception as e:
        print(f"Error storing messages: {e}")
        return {"error": "Failed to store messages"}
    
    
    # change state to HITL- Human in the loop
    return {"state": "HITL"} 



mcp.run(transport='streamable-http')