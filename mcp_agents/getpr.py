import sys    
import os  
import asyncio
sys.path.append(os.path.abspath("../module"))
from customllm import CustomLLM
from mcp.server.fastmcp import FastMCP
from typing import Any
from clients.stmhttp_client import MCPClient
from stm_context_manager import store_messages , get_conversation
# from customllm import CustomLLM
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_openai import AzureChatOpenAI , AzureOpenAI
# from langchain_mcp_adapters.tools import convert_mcp_tool_to_langchain_tool , load_mcp_tools
# from langchain.agents.react.agent import create_react_agent
# from langchain_core.prompts import PromptTemplate

msgs = 5

mcp = FastMCP(name = "Project Requirements Get Assistant", 
              instructions="Get project requirements from the user",
              port = 5050,
              host ="localhost"
            )

llm = CustomLLM()
llm_classifier = CustomLLM()

# llm = AzureOpenAI()  

# client = MultiServerMCPClient({
#     "user_stories_server": {
#             # Make sure you start your weather server on port 8000
#             "url": "http://localhost:5051/mcp/",
#             "transport": "streamable_http",
#         }
# })



@mcp.tool()
async def handle_prompt(prompt: str,state:str , uuid: str)-> dict[str,Any]:
    """
    This tool helps get project requirements from the user
    and generate the user stories once the project requirements are completed.
    Args:
        prompt (str): user input message 
        state (str): current state of the conversation.
        _uuid (str): unique identifier for the conversation.
    Returns:
        dict : String containing the assistant's response.
    """
    
    sys_prompt = """
        You are an assistant agent for Project owner that helps get project requirements from user.
        You have to get the  project requirements detials form the user and finalize them after asking for suggestions.
        Every time the user shares any project requirements add them to the previous ones.
        End task is to finalize the project requirement from the user.
        Once, the user has finalized the project requirements, Your task is to ask him to 
        confirm that he wants to create user stories from the finalized project requirements.
    """
    
    classifier_prompt = """
        You are just a classifier agent that can classify if the last user input has finalized the project requirements and return the response as 'yes' or 'no'.
        Your only task is to classify last user input into 'yes' or 'no' by extracting the user sentiments on finalizing the project requirements form the provided history of messages.
        Please identify is the project requirements are updated or finalised in the give prompt from the user.
        if the project requirements are finalized return 'yes' else return 'no'.
    """
    
    # get the conversation messages from persistent storage
    history  = []
    try:
        conversation = await get_conversation(uuid , state , msgs )
        history = conversation.get("response", [])
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return {"error": "Failed to retrieve conversation"}

    
    response = llm.invoke(input = prompt , sys_prompt = sys_prompt )
    check = 'no'
    # if(len(history[:-1])>=3):
    check = llm_classifier.invoke(input = response  , sys_prompt = classifier_prompt )
    print(response , "\ncheck:", check)
    
    # change state based on the classifier response to 'CUS'
    try:
        if('yes' in check.lower() ): 
            state = 'CUS'
        await  store_messages(uuid , state , {"role":"assistant","content": response})
            
        
    except Exception as e:
        print(f"Error storing messages: {e}")
        return {"error": "Failed to store messages"}
    
    return {"state":state }


mcp.run(transport='streamable-http')