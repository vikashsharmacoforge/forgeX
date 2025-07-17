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
from lightrag_wrapper import lightrag_query
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
    
    # get the conversation messages and persona from persistent storage
    history  = []
    persona = {}
    try:
        conversation = await get_conversation(uuid , state , msgs , persona = 1)
        persona = conversation.get("persona", {})
        history_res = conversation.get("response", [])
        # remove the 'context' key from the history if it exists
        for h in history_res:
            if 'context' in h:
                h.pop('context')
            history.append(h)
            
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return {"error": "Failed to retrieve getpr conversation and persona"}
    
    print("persona pr:",persona)

    
    #get context from the rag knowledge base
    rag_user_prompt = f"""
    You are a project analysis assistant. I am providing a JSON document that contains detailed requirements and specifications for a new project. Your task is to analyze this input and generate a comprehensive context that includes:
 
    1. A summary of the project's goals and scope.
    2. A breakdown of key functional and non-functional requirements.
    3. Identification of potential modules or components.
    4. Any dependencies, risks, or considerations that should be addressed.
    5. Recommendations for how to proceed with implementation or planning.
    
    Please ensure the output is structured, clear, and actionable for project planning purposes.
    
    Here is the input JSON:
    {json.dumps(persona['Project_Requirement'] if 'Project_Requirement' in persona else {})}
    
    Output:
    - Structured context summary
    - Requirement breakdown
    - Suggested next steps
    """
    try:
        context = await lightrag_query(prompt, domain="Project Management", user_prompt=rag_user_prompt,history=history)
    except Exception as e:
        print(f"Error querying LightRAG PM knowledge base: {e}")
        context = "No relevant context found."
             
    
    
    sys_prompt = f"""
        You are a highly skilled assistant for a Project Owner, specializing in gathering, clarifying, and finalizing project requirements.

        Your tasks are:
        1. Carefully analyze the user's input and the provided context below to understand the project domain and requirements.
        2. Proactively suggest improvements, additions, or clarifications to the requirements using both the provided context and your own expertise.
        3. If you notice missing details or ambiguities, ask targeted questions to ensure all requirements are captured accurately and completely.
        4. Each time the user provides new or updated requirements, append it to the current list and confirm any changes or additions.
        5. Encourage the user to review and finalize the requirements. If the user indicates the requirements are finalized, explicitly ask for confirmation to proceed with creating user stories based on these finalized requirements.
        6. Always be helpful, concise, and focused on ensuring the requirements are clear, complete, and actionable.
        7. Every time you need to check if project requirements have been gathered and finalized, explicitly ask the decision of the user whether the conversation state needs to be changed to proceed to the next phase (such as creating user stories), or if more information is still needed.
        8. Always return a json object at the end of your response stating:
        ```json
        "state": 'change state to next state'  
        ```
        or 
        ```json
        "state": 'don't change state to next state'  
        ```
        
        
        Important: Do not mention or refer to the context provided above in your output. Only use it to inform your response.

        Provided context:
        {context}
    """
    
    classifier_prompt = """
        You are a classifier agent that determines if the state needs to be changed to the next state or not.
        You are give a input message and bases on that you have to classify whether the state needs to be changed or not.
        Now once , decided about the state change, You reponse should be :
        'yes' if the state needs to be changed 
        'no' if the state does not need to be changed
        Do not return anything else.
    """
        

    
    response = llm.invoke(input = prompt , sys_prompt = sys_prompt,history = history[:-1])
    check = 'no'
    print("response:", response)
    
    # extract state json from the response which is present as ```json{"state": "change state to next state"}```
    state_json = response.split("```json")[1].split("```")[0].strip()
    response = response.split("```json")[0].strip()
    print("state_json:", state_json,"\nlength:", len(state_json))
    
    
    
    check = llm_classifier.invoke(input = state_json , sys_prompt = classifier_prompt )
    # print(response ,"\nstate:",state_json, "\ncheck:", check)
    
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