import sys    
import os  
import json
from mcp.server.fastmcp import FastMCP
from typing import Any

llm_path = os.path.abspath("../llm")
if llm_path not in sys.path:
    sys.path.append(llm_path)
utils = os.path.abspath("../utils")
if utils not in sys.path:
    sys.path.append(utils)
clients_path = os.path.abspath("../mcp-clients")
if clients_path not in sys.path:
    sys.path.append(clients_path)
from stmhttp_client import MCPClient
from customllm import CustomLLM
from stm_context_manager import store_messages , get_conversation
from langchain_core.prompts import PromptTemplate
# from langchain_mcp_adapters.tools import convert_mcp_tool_to_langchain_tool , load_mcp_tools
# from langchain_core.prompts import PromptTemplate

msgs = 6

mcp = FastMCP(name = "Project Requirements Get Assistant", 
              instructions="Get project requirements from the user",
              port = 5050,
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
async def handle_prompt(prompt: str,state:str , uuid: str)-> dict[str,Any]:
    """
    This tool helps get project requirements from the user
    and generate the user stories once the project requirements are completed.
    Args:
        prompt (str): user input message 
        state (str): current state of the conversation.
        _uuid (str): unique identifier for the conversation.
    Returns:
        dict : dictionary containing the updated state as response.
    """
    
    #get context from the rag knowledge base
    context = ""
    try:
        client = MCPClient()
        await client.connect_to_streamable_http_server("http://localhost:6001/mcp/")
        context_res = await client.session.call_tool(
            name="lightrag_new_tool", 
            arguments={
                        "question": prompt,
                        "domain": "Project Management",
                        "history": []
                    }
        )
        
        context = json.loads(context_res.content[0].text).get('LightRAG',str)
        print("context:", context)
    finally:
        if client:
            await client.cleanup()
    
    sys_prompt = f"""
        Below is the relevant to the user input prompt.
        {context}
        Make sure to use the context in providing suggestions for creating project requirements.
        You are an assistant agent for Project owner that helps get project requirements from user also helping user with suggestions from the given context and other possibel suggestions.
        You have to get the  project requirements detials from the user and finalize them after asking for suggestions using the provided context.
        Every time the user shares any project requirements add them to the previous ones.
        End task is to finalize the project requirement from the user.
        Once, the user has finalized the project requirements, Your task is to ask him to 
        confirm that he wants to create user stories from the finalized project requirements.
    """
    
    classifier_prompt = """
        You are just a expert classifier agent that can classify if the last user input has finalized the project requirements or not.
        If the user is trying to add new requirements or not satisfied with current project requirements he surely hasn't finalized the project requirements.
        Your only task is to classify last user input into 'yes' or 'no' by extracting the user sentiments on finalizing the project requirements from the provided input message.
        If there is some update going on or some kind of suggestions are asked from the user about project requirements, then most probably the user hasn't finalized the project requirements yet.
        Please identify if the project requirements are updated or finalised in the give prompt from the user.
        if the project requirements are finalized return 'yes' else return 'no'.
        Your only outputs are : either 'yes' or 'no'.
    """
        

    # get the conversation messages from persistent storage
    history  = []
    try:
        conversation = await get_conversation(uuid , state , msgs )
        history = conversation.get("response", [])
    except Exception as e:
        # print(f"Error retrieving conversation: {e}")
        return {"error": "Failed to retrieve conversation"}

    
    response = llm.invoke(input = prompt , sys_prompt = sys_prompt,history = history[:-1])
    check = 'no'
    # if(len(history[:-1])>=3):
    check = llm_classifier.invoke(input = response  , sys_prompt = classifier_prompt , history = history[-min(3,len(history)):-1] )
    print(response , "\ncheck:", check)
    
    # change state based on the classifier response to 'CUS'
    try:
        if('yes' in check.lower() ): 
            state = 'CUS'
        await  store_messages(uuid , state , {"role":"assistant","content": response,"context": context})
            
        
    except Exception as e:
        print(f"Error storing messages: {e}")
        return {"error": "Failed to store messages"}
    
    return {"state":state }


mcp.run(transport='streamable-http')