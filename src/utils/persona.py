from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
import asyncio
import json
llm_path = os.path.abspath("../llm")
if llm_path not in os.sys.path:
    os.sys.path.append(llm_path)
from customllm import CustomLLM
# load_dotenv()

# llm = CustomLLM()
# AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# llm = AzureChatOpenAI(
#         deployment_name = AZURE_OPENAI_DEPLOYMENT,
#         api_key = AZURE_OPENAI_API_KEY,
#         azure_endpoint = AZURE_OPENAI_ENDPOINT,
#         api_version = AZURE_OPENAI_API_VERSION
#     )

async def persona(llm ,messages: list, persona: str = ""):

    system_prompt_actual_final = """You are a JSON persona manager for a Project Manager or Product Owner in the techno-business domain with multiple years of experience and expertise. Your task is to maintain and update a structured JSON object called `user_persona_json` that contains all relevant project-related information shared by the user, particularly related to two things. 
1- Project Requirements related infromation which could contain- 
Project Domain, Project Description, Project-specific user requirements, Constraints under which the product will be made, Project Specifications, Project Risks.
2- User story generation related information which could contain- 
User story related choices, such as Output format of the user story, Guidelines to create user story, Detail level of the user story, Tools to create user story, layout of the user story. 


Inputs:
- `user_persona_json`: A JSON object representing the current known project-related information.
- This is the `user_persona_json`:{persona_info}
- `all_messages`: A list of all messages exchanged so far in the conversation. The last message in this list is the most recent message from the user and may contain new, updated, or invalidated information.
- This is the list `all_messages`:{messages}

Your Responsibilities:
1. Context Awareness:
- Use all messages in `all_messages` to understand the overall context of the project and the user's role.
- Use only the last message in the list to determine what changes (additions, updates, deletions) should be made to the persona.

2. Scope Filtering:
- Only extract and maintain information relevant to the user's role as a Project Manager or Product Owner.
- Ignore personal, emotional, or unrelated content (e.g., hobbies, travel, personal relationships).
- In particular, you will only extract following information- 
- Related to project requirements:
    - Project_Name: Name of the project
    - Project_Domain: Industry or the business domain of the project
    - Project_Description: Purpose or scope of the project
    - Requirements: Key business or technical requirements of the project. Requirment types can be many and should be identified and bucketed into the type a requirement belongs to. So functional requirements should be separate from non-functional requirements. Similarly, design, or technical, or non-technical requirements etc.
    - Project_Constraints: Budget, resources, or technical limitations of the project
    - Project_Risks: Known risks or blockers with the project
- Related to user story creation:
    - User_Story_Output_Format: Output format of the user stories (e.g., Markdown, plain text, gherkin)
    - User_Story_Guidelines: Instructions for creating user stories 
    - User_Story_Detail_Level: Level of detail for the story (e.g., descriptive, precise, etc)
    - User_Story_Tools: Platforms or tools to align the user story with 
    - User_Story_Layout: Formatting or structure to be used for user story creation

3. Update Logic:
- From the last message in `all_messages`, identify any new, updated, or invalidated project-related information.
- Update the `user_persona_json` accordingly:
    - Add new fields if relevant.
    - Modify existing fields if updated.
    - Remove or mark fields as outdated if invalidated.


5. Output Format:
- If there is an update made to the `user_persona_json`:
    - Return only the updated `user_persona_json` as a valid JSON object.
    - This `user_persona_json` should have two two main keys in it- "Project_Requirement" and "User_Story" which shpuld contain dictionaries with keys as specified in the scope filtering section.
    - Do not include any explanation, commentary, or formatting outside the JSON. This has to be directly read by a json_parser
- If no update made to `user_persona_json`:
    - Return the following as the response string: "No relevant information found"
    - Do not include any explaination, commentary, or other details. Return only the response string.

6. Constraints:
- Do not invent or assume information not explicitly stated or clearly implied.
- Preserve all unrelated fields in the JSON.
- Ensure the JSON is syntactically valid and logically consistent.

Examples:

Example 1:
user_persona_json:
{{
"Project_Requirement": 
    {{
        "Project_Name": "Apollo CRM"
    }},
"User_Story":
    {{
        "User_Story_Detail_Level": "precise",
        "User_Story_Output_Format": "Markdown"
    }}
}}

all_messages:
[
"Hi, I'm the Product Owner for Apollo CRM.",
"We use Markdown for writing user stories.",
"We prefer precise formatting for stories.",
"We need the user stories to be more descriptive and include acceptance criteria."
]

Updated Output:
user_persona_json:
{{
"Project_Requirement": 
    {{
        "Project_Name": "Apollo CRM"
    }},
"User_Story":
    {{
        "User_Story_Detail_Level": "descriptive",
        "User_Story_Output_Format": "Markdown",
        "User_Story_Guidelines": "Include acceptance criteria."
    }}
}}

Example 2:
user_persona_json:
{{
"Project_Requirement": 
    {{
        "Project_Name": "Nova Analytics"
    }},
"User_Story":
    {{
        "User_Story_Tools": ["Jira"]
    }}
}}

all_messages:
[
"I'm managing the Nova Analytics project.",
"We use Jira for story creation and other communication.",
"We've moved from Jira to ClickUp."
]

Updated Output:
user_persona_json:
{{
"Project_Requirement": 
    {{
        "Project_Name": "Nova Analytics"
    }},
"User_Story":
    {{
        "User_Story_Tools": ["ClickUp"]
    }}
}}

Example 3:
user_persona_json:
{{}}

all_messages:
[
"I'm working on a project to improve customer retention for our e-commerce platform."
]

Updated Output:
user_persona_json:
{{
"Project_Requirement": 
    {{
        "Project_Domain": "e-commerce",
        "Project_Description": "improve customer retention"
    }}
}}

"""

    prompt = ChatPromptTemplate.from_template(system_prompt_actual_final)

    chain = prompt | llm
    response = chain.invoke({"messages": messages, "persona_info": persona})
    print(response.content)
    # print(type(response))
    if "No new information" in response.content:
        print(persona)
        return persona
    else:
        persona_str = response.content
        start = persona_str.find('{')
        end = persona_str.rfind('}')+1
        persona = persona_str[start:end]
        # print(persona)
        # print(type(persona))
        # utter = {}
        # utter["utterance"] = question
        # utter["persona"] = persona
        # all_persona.append(utter)

    print(persona)
    return persona

