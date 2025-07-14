from langchain.agents import AgentExecutor, create_tool_calling_agent
from customllm import CustomLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureOpenAI
import dotenv
import os

dotenv.load_dotenv()

# llm = CustomLLM()
llm = AzureOpenAI(
    deployment_name= "gpt-4o",
)

 
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant"),
#         ("placeholder", "{chat_history}"),
#         ("human", "{input}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ]
# )

class ToolCallingAgent:
    def __init__(self, tools, prompt:str):
        self.tools = tools
        refined_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.agent = create_tool_calling_agent(llm=llm, tools=self.tools,prompt = refined_prompt)

    def invoke(self, input_text: str) -> str:
        """Run the agent with the provided input text."""
        agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)
        response = agent_executor.run(input_text)
        return response