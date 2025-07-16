import sys    
import os  
import json
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
    
    # get the conversation messages and persona from persistent storage
    history = []
    persona = {}
    try:
        conversation = await get_conversation(uuid , state , msgs , persona = True )
        persona = conversation.get("persona", {})
        history_res = conversation.get("response", [])
        # remove the 'context' key from the history if it exists
        for h in history_res:
            if 'context' in h:
                h.pop('context')
            history.append(h)
    except Exception as e:
        print(f"Error retrieving conversation and persona: {e}")
        return {"error": "Failed to retrieve conversation and persona"}
    
    #get context from the rag knowledge base
    context = ""
    try:
        client = MCPClient()
        await client.connect_to_streamable_http_server("http://localhost:6001/mcp/")
        context_res = await client.session.call_tool(
            name="lightrag_new_tool", 
            arguments={
                        "question": prompt,
                        "domain": "User Stories",
                        "history": [],
                        "user_prompt": json.dumps(persona)
                    }
        )
        
        context = json.loads(context_res.content[0].text).get('LightRAG',str)
        print("context:", context)
    finally:
        if client:
            await client.cleanup()
             
    
    
    sys_prompt = f"""
    You are an expert assistant in converting project requirements into user stories.

    Your task:
    1. Review the conversation history to find the message containing the finalized project requirements.
    2. Analyze these requirements and identify both:
        - Functional requirements (features, behaviors, user interactions)
        - Non-functional requirements (performance, security, usability, scalability, compliance, etc.)
    3. For each requirement, write a user story using this format:
        "As a <user role>, I want <feature/requirement> so that <benefit/value>."
    4. For each user story, list clear acceptance criteria that define when the story is complete and successful.
    5. Make sure all requirements are covered. Write user stories and acceptance criteria in a way that both technical and non-technical people can understand.
    6. If any requirement is unclear or ambiguous, note it as "Clarification needed".

    Additional context about writing user stories from project requirements:
    {context}

    If the above context contains relevant information, use it when creating user stories. If not, rely on your own understanding as described above.
    """
    
    
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