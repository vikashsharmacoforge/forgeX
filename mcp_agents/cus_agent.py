import sys    
import os  
sys.path.append(r"D:\OneDrive - Coforge Limited\Desktop\ForgeX\agent Chat\module")

from mcp.server.fastmcp import FastMCP
from customllm import CustomLLM 


llm = CustomLLM()


mcp = FastMCP(name = "Project Requirements Get Assistant", 
              instructions="Get project requirements from the user",
              port = 5051,
              host ="localhost"
            )




@mcp.tool()
async def create_user_stories(prompt: str)-> dict:
    """
    This tool helps create user stories based on the provided project requirements.
    Args:
        prompt (str): project requirements input
    Returns:
        dict : String containing the assistant's response.
    """
    sys_prompt = """
    You are a helpful assistant that helps create user storeis form the input project requirements.
    Analyse the project requirements and the collect functional and non-functional requirements.
    Once all the requirements are extracted , generate user stories based on these requirements.
    """
    print("user_prompt:",prompt)
    
    response = llm.invoke(sys_prompt=sys_prompt,input = prompt)
    
    print({"response": response})
    
    # change state to USC- user storeis created
    return {"response": response,"state": "USC"} 



mcp.run(transport='streamable-http')