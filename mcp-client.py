import os
import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
import asyncio
from openai import AsyncOpenAI

# Apply nest_asyncio to allow nested event loops (needed for Jupyter/IPython)
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Global variables to store session state
session = None
exit_stack = AsyncExitStack()
openai_client = AsyncOpenAI()
stdio = None
write = None


async def connect_to_server(server_script_path: str = "server.py"):
    """Connect to an MCP server.

    Args:
        server_script_path: Path to the server script.
    """
    global session, stdio, write, exit_stack

    # Server configuration
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # Connect to the server
    stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
    stdio, write = stdio_transport
    session = await exit_stack.enter_async_context(ClientSession(stdio, write))

    # Initialize the connection
    await session.initialize()

    # List available tools
    tools_result = await session.list_tools()
    print("\nConnected to server with tools:")
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")


async def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get available tools from the MCP server in OpenAI format.

    Returns:
        A list of tools in OpenAI format.
    """
    global session

    tools_result = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools_result.tools
    ]


async def process_query(query: str) -> str:
    """Process a query using OpenAI and available MCP tools.

    Args:
        query: The user query.

    Returns:
        The response from OpenAI.
    """
    global session, openai_client

    # Get available tools
    tools = await get_mcp_tools()


    # Initial OpenAI API call
    response = await openai_client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_NAME"),
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="auto",
    )

    # Get assistant's response
    assistant_message = response.choices[0].message

    # Initialize conversation with user query and assistant response
    messages = [
        {"role": "user", "content": query},
        assistant_message,
    ]

    # Handle tool calls if present
    if assistant_message.tool_calls:
        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            # Execute tool call
            result = await session.call_tool(
                tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )

            # Add tool response to conversation
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content[0].text,
                }
            )

        # Get final response from OpenAI with tool results
        final_response = await openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME"),
            messages=messages,
            tools=tools,
            tool_choice="none",  # Don't allow more tool calls
        )

        return final_response.choices[0].message.content

    # No tool calls, just return the direct response
    return assistant_message.content


async def cleanup():
    """Clean up resources."""
    global exit_stack
    await exit_stack.aclose()


async def main():
    """Main entry point for the client."""
    #await connect_to_server("server.py")
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        global session
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("\nConnected to server with tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Example: Ask about company vacation policy
            query = "What is the current time?"
            print(f"\nQuery: {query}")

            response = await process_query(query)
            print(f"\nResponse: {response}")

            # Example: Extract entities from a query
            entity_query = "What events happened in Colombo, Sri Lanka on January 1st, 2023?"
            print(f"\nEntity Query: {entity_query}")
            entity_response = await session.call_tool(
                "extract_entities_tool", arguments={"query": entity_query}
            )
            print(f"\nEntity Response: {entity_response.content[0].text}")

            # Example: Refine a query
            refine_query = "What are the latest news about the president of Sri Lanka?"
            print(f"\nRefine Query: {refine_query}")
            refine_query_response = await session.call_tool(
                "refine_query_tool", arguments={"original_query": refine_query}
            )
            print(f"\nRefine Query Response: {refine_query_response.content[0].text}")

            # Example: Check relevance of a document to a query
            document = "This is a news article about the American tax implimentation."
            query = "Sri Lankan politics"
            print(f"\nRelevance Query: Document: '{document}', Query: '{query}'")
            relevance_response = await session.call_tool(
                "check_relevance", arguments={"text_chunk": document, "question": query}
            )
            print(f"\nRelevance Response: {relevance_response.content[0].text}")

    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
