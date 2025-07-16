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
        You are an expert assistant responsible for updating and managing user stories based on detailed user feedback.
        The user may refer to user stories by their number, title, or by describing their content. Carefully analyze the user's input to identify which specific user stories are being referenced.

        Your tasks are as follows:
        1. For each user story that the user explicitly mentions, describes, or provides feedback on, update the content of that user story to reflect the user's suggestions, corrections, or requests for additional information.
        2. For all user stories that are not mentioned or described by the user, leave them unchanged.
        3. Always return the full, complete list of all user stories you are working on, not just the ones that are updated.
        4. Clearly label every user story in your response:
            - If you have updated a user story based on the user's feedback, add the label [UPDATED] at the beginning of that user story.
            - If a user story was not changed, add the label [ACCEPTED FOR NOW] at the beginning of that user story.
        5. Always return the full, complete list of user stories, including both updated and unchanged stories, each with the appropriate label.
        6. Do not omit or summarize any user stories; include the full text of every user story in your response.
        7. Organize your response in a clear, numbered list, and ensure that each user story is easy to read and understand.
        8. Do not add any extra commentary or explanation outside of the user stories themselves.
        9.If you feel that all user stories have been  finalized, explicitly state whether the conversation state needs to be changed to proceed to the next phase or if more information is still needed
        you should return a json object at the end of your response stating:
        "state": 'change state to next state' or 'don't change the state'
        10. Always return the state json as json object in the format ```json {"state": "change state to next state"}``` at the end of your response.

        Your goal is to make it easy for the user to see exactly which user stories were updated and which remain unchanged.
    """
    
    classifier_prompt = """
        You are a classifier agent that determines if the state needs to be changed to the next state or not.
        You are give a input message and bases on that you have to classify whether the state needs to be changed or not.
        Now once , decided about the state change, You reponse should be :
        'yes' if the state needs to be changed 
        'no' if the state does not need to be changed
        Do not return anything else.
    """
    
    finalize_prompt = """
        You are a helpful assistant tasked with finalizing user stories for presentation.
        Your job is to take the list of user stories and make them as presentable as possible for stakeholders.
        Perform the following tasks:
        1. Remove any labels or markdowns such as [UPDATED] or [ACCEPTED FOR NOW].
        2. Ensure each user story is clearly and consistently numbered.
        3. Format the stories in a clean, professional, and easy-to-read style.
        4. Correct any formatting inconsistencies, such as spacing or indentation.
        5. Use concise and clear language, improving readability where possible without altering the meaning.
        6. Ensure the stories are ready to be shared or presented to stakeholders.
        Do not include any extra commentary or explanation—just the finalized, polished user stories.
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
    
    # extract state json from the response which is present as ```json{"state": "change state to next state"}```
    state_json = response.split("```json")[1].split("```")[0].strip()
    response = response.split("```json")[0].strip()
    print("state_json:", state_json,"\nlength:", len(state_json))
    
    check = llm_classifier.invoke(input = state_json , sys_prompt = classifier_prompt)
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