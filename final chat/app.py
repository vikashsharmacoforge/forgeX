from shiny.express import ui
from shiny import reactive
import requests
import json
import sys
import os
import uuid
sys.path.append(os.path.abspath("../src/utils"))
from stm_context_manager import store_messages , get_conversation

chat = ui.Chat(id="agent_chat")

chat.ui()

INITIAL_STATE = 'START'
state = reactive.Value(INITIAL_STATE)
uuid = reactive.Value(str(uuid.uuid4()))

@chat.on_user_submit
async def handle_user_input(user_input:str):
    
    try:
        await store_messages(uuid.get(), state.get(), {"role":"user","content":user_input})  
    except Exception as e:
        print(f"Error storing messages: {e}")
        
    response = requests.post(
        "http://localhost:5678/webhook/77ab886c-4239-4cc7-8e1d-00e20c26a4b8",
        json={"data":{"messages": [{"role":"user","content":user_input}] , "state": state.get() , "_uuid": uuid.get()}},)
    
    if response.status_code == 200:
        response_data = response.json()
        # Extract data from the nested structure
        if 'stdout' in response_data:
            try:
                # Parse the stdout string as JSON
                stdout_data = json.loads(response_data['stdout'])
                if 'response' in stdout_data:
                    state.set(stdout_data['response'].get("state",str))
                assistant_msg = await get_conversation(uuid.get(), state.get())
                print("assistant_msg:", assistant_msg)
                await chat.append_message_stream(assistant_msg['response'][0].get('content',str))    
            except json.JSONDecodeError as e:
                print(f"Error parsing stdout JSON: {e}")
                await chat.append_message_stream("Error processing response")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        