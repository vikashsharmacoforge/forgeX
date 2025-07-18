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
from lightrag_wrapper import lightrag_query
from typing import Any
from langchain_core.prompts import PromptTemplate


llm = CustomLLM()


mcp = FastMCP(name = "Project Requirements Get Assistant", 
              instructions="Get project requirements from the user",
              port = 5051,
              host ="localhost"
            )

msgs = 3


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
        conversation = await get_conversation(uuid , state , msgs , persona = 1 )
        persona = conversation.get("persona", {})
        history_res = conversation.get("response", [])
        # remove the 'context' key from the history if it exists
        for h in history_res:
            if 'context' in h:
                h.pop('context')
            history.append(h)
    except Exception as e:
        print(f"Error retrieving conversation cus_agent and persona: {e}")
        return {"error": "Failed to retrieve conversation and persona"}
    
    print("persona cus:",persona)
    
    #get context from the rag knowledge base
    rag_user_prompt = f"""
    You are a product manager assistant specializing in extracting user story creation guidelines from a knowledge base. I will provide a JSON object called 'persona' that contains specific preferences, priorities, and requirements for user story creation.

    Your directive:
    - Carefully review the persona JSON to understand the user's preferences (e.g., preferred format, level of detail, grouping, terminology, acceptance criteria style, etc.).
    - From the provided knowledge base, extract only the guidelines, best practices, and instructions relevant to creating user stories that match these preferences.
    - Focus on extracting actionable advice, templates, examples, and recommendations that align with the persona's requirements.
    - If the persona specifies grouping (e.g., by epics or modules), extract guidelines related to such organization.
    - Use the language, tone, and structure indicated in the persona when presenting the extracted guidelines.
    - If any preference is unclear, note it as "Clarification needed" in your output.

    Here is the persona JSON:
    {json.dumps(persona)}

    Output:
    - A summary of user story creation guidelines from the knowledge base, customized to the persona's preferences
    - Grouped and formatted as specified in the persona
    - Acceptance criteria guidelines aligned with persona requirements
    """
    
    try:
        context = await lightrag_query(prompt, domain="User Stories", user_prompt=rag_user_prompt,history=history)
    except Exception as e:
        print(f"Error querying LightRAG US knowledge base: {e}")
        context = "No relevant context found."
        
             
    
    
    sys_prompt = f"""
    You are an expert assistant in converting project requirements into comprehensive user stories.

    Your task:
    1. Carefully review the conversation history and identify ALL finalized project requirements, both functional and non-functional.
    2. For each requirement, ensure it is clearly understood and not missed. If any requirement is ambiguous or incomplete, explicitly note it as "Clarification needed".
    3. For every requirement, write a user story using this format:
        "As a <user role>, I want <feature/requirement> so that <benefit/value>."
    4. For each user story, provide detailed and clear acceptance criteria that define when the story is complete and successful.
    5. Double-check that every requirement from the conversation is converted into a user story and acceptance criteria. Do not omit any requirement.
    6. Write user stories and acceptance criteria in a way that both technical and non-technical people can understand.
    7. If requirements are grouped (e.g., by epics or modules), organize user stories accordingly.

    Additional context about writing user stories from project requirements:
    {context}

    Important: Do not mention or refer to the context provided above in your output. Only use it to inform your response.
    If the above context contains relevant information, use it when creating user stories. If not, rely on your own understanding as described above.
    Carefully ensure completeness and clarity in your output.
    """
    
    print("context:",context)
    response = llm.invoke(sys_prompt=sys_prompt,input = prompt , history = history[:-1])
    # print({"response": response})
    
    try:
        await  store_messages(uuid , state , {"role":"assistant","content": response,"context":context})  
    except Exception as e:
        print(f"Error storing messages: {e}")
        return {"error": "Failed to store messages"}
    
    
    # change state to HITL- Human in the loop
    return {"state": "HITL"} 



mcp.run(transport='streamable-http')