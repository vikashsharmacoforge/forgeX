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
from langchain_core.prompts import PromptTemplate


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
    You are an expert assistant specialized in analyzing project requirements and generating comprehensive user stories.
    The conversation history provided will always contain the finalized project requirements. 
    Your task is to identify and extract the finalized project requirements from the history (look for the message that contains the finalized requirements).
    Analyze these requirements to cover all types: functional (features, behaviors, user interactions) and non-functional (performance, security, usability, scalability, compliance, etc.).
    For each requirement, generate clear, concise, and actionable user stories in the format:
    "As a <user role>, I want <feature/requirement> so that <benefit/value>."
    For each user story, provide a set of acceptance criteria that clearly define when the story can be considered complete and successful.
    Ensure all relevant requirements are covered and that the user stories and acceptance criteria are understandable for both technical and non-technical stakeholders.
    If any requirement is ambiguous, note it as a clarification needed.
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
    # print({"response": response})
    
    try:
        await  store_messages(uuid , state , {"role":"assistant","content": response})  
    except Exception as e:
        print(f"Error storing messages: {e}")
        return {"error": "Failed to store messages"}
    
    
    # change state to HITL- Human in the loop
    return {"state": "HITL"} 



mcp.run(transport='streamable-http')