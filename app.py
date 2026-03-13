import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import create_agent



async def main():
    client = MultiServerMCPClient(
        {
            "postgres": {
                "transport": "stdio",  # Local subprocess communication
                "command": "uv",
                # Absolute path to your math_server.py file
                "args": [
				    "run",
				    "postgres-mcp",
				    "--access-mode=unrestricted"
			    ],
			    "env": {
				    "DATABASE_URI": "postgresql://agentic:Anurag2004@localhost:5432/blog"
			    },
			    "type": "stdio"
            }
        }
    )

    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    from langchain_groq import ChatGroq
    llm = ChatGroq(model="openai/gpt-oss-20b", api_key=api_key)

    tools = await client.get_tools()
    agent = create_agent(
        llm,
        tools  
    )

    query_response = await agent.ainvoke(
        {
            "messages": [HumanMessage(content="Can you define the structure of the table checkpoint_blobs, please describe it.")]
        }
    )

    print(query_response)


asyncio.run(main())