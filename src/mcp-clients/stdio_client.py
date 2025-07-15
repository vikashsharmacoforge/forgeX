"""MCP Client for Stdio Communication"""
# https://modelcontextprotocol.io/quickstart/client
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.server_process = None
 
    async def connect_to_server(self, server_cmd: list[str]):
        """Connect to an MCP server over stdio"""
 
        self.server_params = StdioServerParameters(
            command=server_cmd[0],
            args=[server_cmd[1]]
        )
 
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
       
        await self.session.initialize()
       
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print(tools)
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        
    async def process_query(self):
        """Process a query using the MCP client"""
        if not self.session:
            raise RuntimeError("Client session is not initialized. Call connect_to_server first.")
        
        # Example of calling a tool
        response = await self.session.call_tool(
            name="extract_memory",
            arguments={"user_id":"alice"}
        )
        
        return response
 
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
            
  
async def main():
    client = MCPClient()
    try:
        # Connect to the MCP server (update the command as needed)
        await client.connect_to_server(["python",
            r"D:\OneDrive - Coforge Limited\Desktop\ForgeX\mcp-server\mem0\main.py"
        ])
        # Example: call a tool
        while(True):
            query = input("Enter here: ")
            if query.lower() == "exit":
                break
            response =  await client.process_query()
            print("Response:", response)
    finally:
        await client.cleanup()          
            
if __name__ == "__main__":
    # Example usage
    asyncio.run(main())
