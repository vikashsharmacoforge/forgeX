from mem0 import Memory , AsyncMemory
from typing import List , Any
import asyncio
import configparser
import dotenv
dotenv.load_dotenv()
import json

LIMIT_TOPK = 5  # Default limit for search results
default_user = "Aadarsh"
memory_config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": 'bolt://localhost:7687',
            "username": 'neo4j',
            "password": "Ap28@28pa",
            "database": 'forgexgraphdb'
        }
    },
    "llm": {
        "provider": "azure_openai",
        "config": {
            "temperature": 0.1,
            "max_tokens": 2000
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "mxbai-embed-large:latest",
            "embedding_dims": 1024,
        }
    },
    "version": "v1.1"
}


class LongTermMemory():
    def __init__(self, name: str = "long-term memory",config: dict = None ):
        self.name = name
        self.memory_type = "long-term"
        self.description = "This is a long-term memory module for storing persistent data."
        self.long_term_memory = Memory.from_config(memory_config) # Placeholder for long-term memory storage
    
    def add_to_memory(self, messages : List[dict], user_id: str = default_user  , meta_data: dict = None):
        # Logic to store data in long-term memory
        if(meta_data):
            self.long_term_memory.add(messages,user_id = user_id,metadata = meta_data)
        else:
            self.long_term_memory.add(messages,user_id= user_id)        
    
    def search_memory(self, query:str , user_id: str = default_user) -> List[dict]:
        # Logic to retrieve data from long-term memory
        results = self.long_term_memory.search(query,user_id = user_id )
        
        # formatted_results = [{"id": result["id"], "memory": result["memory"] , "metadata" : result["metadata"] , "user_id": result["user_id"]} for result in results]
        
        return results
    
    def extract_memory(self , user_id: str = default_user) -> List[dict]:
        # Logic to extract all memories for a user
        
        results = self.long_term_memory.get_all(user_id = user_id)
        
        # formatted_results = [{"id": result["id"], "memory": result["memory"] , "metadata" : result["metadata"] , "user_id": result["user_id"]} for result in results]
        
        return results
    
    def delete_memory(self, memory_id: str, user_id: str = None):
        # Logic to delete a specific memory
        # self.long_term_memory.delete(memory_id, user_id)
        pass
    


    
class AsyncLongTermMemory():
    
    def __init__(self, name: str = "long-term memory",config: dict = None ):
        self.name = name
        self.memory_type = "long-term"
        self.description = "This is a long-term memory module for storing persistent data."
        self.long_term_memory = asyncio.run(AsyncMemory.from_config(memory_config)) # Placeholder for long-term memory storage
    
    async def add_to_memory(self, messages : Any, user_id: str  , meta_data: dict=None):
        # Logic to store data in long-term memory
        if(meta_data):
            await self.long_term_memory.add(messages,user_id = user_id,metadata=meta_data)
        else:
            await self.long_term_memory.add(messages,user_id = user_id)
            
        
    
    async def search_memory(self, query:str , user_id: str ) -> list[dict]:
        # Logic to retrieve data from long-term memory
            
        results = (await self.long_term_memory.search(query,user_id=user_id,limit = LIMIT_TOPK))['results']
        
        formatted_results = [{"id": result["id"], "memory": result["memory"] , "metadata" : result["metadata"] , "user_id": result["user_id"]} for result in results]
        
        return formatted_results
    
    async def extract_memory(self , user_id: str  ) -> list[dict]:
        # Logic to extract all memories for a user
        results = await (await self.long_term_memory.get_all(user_id = user_id,limit = LIMIT_TOPK))['results']
        
        formatted_results = [{"id": result["id"], "memory": result["memory"] , "metadata" : result["metadata"] , "user_id": result["user_id"]} for result in results]
        
        return formatted_results
    
    def delete_memory(self, memory_id: str, user_id: str = None):
        # Logic to delete a specific memory
        # self.long_term_memory.delete(memory_id, user_id)
        pass
    

persona = {
        "Project_Requirement": {
            "Project_Description": "application for rates management",
            "Requirements": {
                "Functional": [
                    "user roles (editor, reviewer, admin)",
                    "login functionality",
                    "role based access",
                    "rates report page",
                    "charts and visualizations for changing rates",
                    "notification feature",
                    "rate approval workflow",
                    "editor can make rate changes and send request to reviewer",
                    "reviewer can approve or reject with comments",
                    "rejected requests sent back to editor",
                    "approved requests go to admin",
                    "admin can append comments and approve/reject",
                    "admin approval sends notification to reviewer and editor",
                    "admin rejection follows back same process",
                    "notifications via email and website"
                ]
            },
            "Project_Constraints": "user should not have access to view complete history of all actions and comments for rate audit"
        },
        "User_Story": {
            "User_Story_Guidelines": "create user stories",
            "User_Story_Detail_Level": "shorter",
            "User_Story_Layout": "i am ____ wants to ____ so that ____ acceptance criteria"
        }
    }

# mem0 = LongTermMemory()

# mem0.add_to_memory(json.dumps(persona))
# ans = mem0.search_memory(" rates management application")



# ans = asyncio.run(mem0.extract_memory(user_id = "alice"))
# print("ans:",ans)


