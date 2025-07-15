import sys    
import os  
from mcp.server.fastmcp import FastMCP
from typing import Any

llm_path = os.path.abspath("../llm")
if llm_path not in sys.path:
    sys.path.append(llm_path)
utils = os.path.abspath("../utils")
if utils not in sys.path:
    sys.path.append(utils)
from customllm import CustomLLM
from stm_context_manager import store_messages , get_conversation

# from langchain_mcp_adapters.tools import convert_mcp_tool_to_langchain_tool , load_mcp_tools
# from langchain_core.prompts import PromptTemplate

msgs = 6

mcp = FastMCP(name = "Project Requirements Get Assistant", 
              instructions="Get project requirements from the user",
              port = 5052,
              host ="localhost"
            )

llm = CustomLLM()
llm_classifier = CustomLLM()

# from langchain_openai import AzureChatOpenAI , AzureOpenAI
# llm = AzureOpenAI()  

# from langchain_mcp_adapters.client import MultiServerMCPClient
# client = MultiServerMCPClient({
#     "user_stories_server": {
#             # Make sure you start your weather server on port 8000
#             "url": "http://localhost:5051/mcp/",
#             "transport": "streamable_http",
#         }
# })



@mcp.tool()
async def hitl(prompt: str,state:str , uuid: str)-> dict[str,Any]:
    """
    This tool helps update the created user stories based on the feedback from the user.
    Args:
        prompt (str): user input message 
        state (str): current state of the conversation.
        _uuid (str): unique identifier for the conversation.
    Returns:
        dict : dictionary containing the updated state as response.
    """
    
    sys_prompt = """
        You are a human assistant agent that helps update the user stories based on the feedback from the user.
        The user may point out to some mistakes in particular user stories or may ask to add more content to some user stories.
        Only update the user stories based on the user input feedback ; which can be identified using user story number or its description by the user ;  and keep the rest as it is.
        Only update the user stories which are pointed out by the user.
        You markdown the user stories which have been updateds as [UPDATED] and the ones which are not updated as [ACCEPTED FOR NOW].
        Always return all the stories including the [UPDATED] ones and the [ACCEPTED FOR NOW] ones.
        All the updated stories and accpeted for now stories must be present in the response.  
    """
    
    classifier_prompt = """
        You are a classifier agent that helps classify the user input as 'yes' or 'no'.
        If the user input contains any feedback or suggestions for the user stories then classify it as 'no' else classify it as 'yes'.
        You are given a sequence of messages , analyse based on them if the user is suggest some suggestions or feedback for the user stories
        or he/she is satisfied with the created stories.
        Only work as a classifier and return the response as a 'yes' or a 'no'.
    """
    
    finalize_prompt = """
        You are a helpful assistant that helps finalize the user stories.
        Your task is to make the user stories ready to be presentable in the best format.
        You have to beautify the appearance of the finalized user stories.
        Remove any kind of markdowns like [UPDATED] or [ACCEPTED FOR NOW] from the user stories and 
        make them look presentable. 
    """
    
    # get the conversation messages from persistent storage
    history  = []
    try:
        conversation = await get_conversation(uuid , state , msgs )
        history = conversation.get("response", [])
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return {"error": "Failed to retrieve conversation"}

    
    response = llm.invoke(input = prompt , sys_prompt = sys_prompt ,history = history[:-1])
    check = 'no'
    # if(len(history[:-1])>=3):
    check = llm_classifier.invoke(input = response  , sys_prompt = classifier_prompt, history = history[-min(len(history),3):-1] )
    print(response , "\ncheck:", check)
    
    # change state based on the classifier response to 'CUS'
    try:
        if('yes' in check.lower() ): 
            state = 'FINALIZED'
            response = llm.invoke(input = response , sys_prompt = finalize_prompt)
        await  store_messages(uuid , state , {"role":"assistant","content": response})
            
        
    except Exception as e:
        print(f"Error storing messages: {e}")
        return {"error": "Failed to store messages"}
    
    return {"state":state }


mcp.run(transport='streamable-http')