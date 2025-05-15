import datetime
import os
import json
import sys
import openai
import config
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Create an MCP server
mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

@mcp.tool()
def get_time_with_prefix():
    """Get the current date and time."""
    return str(datetime.datetime.now())

@mcp.tool()
def extract_entities_tool(query: str) -> str:
    """Extract entities from a given text query using OpenAI."""
    try:
        prompt = (
            "You are an entity extraction specialist. Analyze the following query and identify any named entities "
            "present, categorizing them by type. Focus on entities that would be important for searching "
            "news articles about Sri Lanka. Use the following categories:\n\n"
            "PERSON: Real people or fictional characters\n"
            "LOCATION: Countries, cities, states, mountains, bodies of water, etc.\n"
            "ORGANIZATION: Companies, agencies, institutions, etc.\n"
            "EVENT: Named events such as festivals, wars, sports events, etc.\n"
            "DATE: Absolute or relative dates or periods\n"
            "FACILITY: Buildings, airports, highways, bridges, etc.\n"
            "PRODUCT: Objects, vehicles, foods, etc. (Not services)\n"
            "WORK_OF_ART: Titles of books, songs, etc.\n\n"
            "Return your answer as a JSON object with entity types as keys and arrays of extracted entities as values. "
            "Only include categories where entities were found. If no entities are found, return an empty JSON object {}."
        )
        
        completion = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def refine_query_tool(original_query: str) -> str:
    """Refine a given text query using OpenAI."""
    try:

        prompt = (
            "You are a search query optimization agent. Your task is to refine and improve search queries "
            "about Sri Lanka news to make them more effective for vector search. Enhance specificity, add context, "
            "and clarify ambiguities. Keep the query concise. Return ONLY the refined query without explanations, "
            "and do not add any year or number randomly to the qyery"
        )

        response = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME"),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Original query: {original_query}"}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        refined_query = response.choices[0].message.content.strip()
        
        # If the refinement drastically changed the query, revert to original
        if len(refined_query) > len(original_query) * 3:
            return original_query
            
        return refined_query
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def check_relevance(question: str, text_chunk: str) -> float:
    """
    Check the relevance of a text chunk to a given question using an LLM.
    Returns a relevance score between 0 and 1.
    """
    try:
        
        # Truncate content for API efficiency (can be adjusted based on token limits)
        content_preview = text_chunk[:1000] + "..." if len(text_chunk) > 1000 else text_chunk

        prompt = f"""
        Task: Evaluate if this article is relevant to the user's query.

        User Query: "{question}"

        Article Content Preview: 
        "{content_preview}"

        Provide a relevance score from 0 to 1, where:
        - 0.0-0.3: Not relevant at all
        - 0.4-0.6: Somewhat relevant but missing key aspects
        - 0.7-1.0: Highly relevant to the query

        First provide your reasoning, then on a new line, output only 'SCORE: X.X' (a number between 0 and 1).
        """

        response = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME"),  # Can be adjusted based on requirements
            messages=[
                {"role": "system", "content": "You are an expert news curator that accurately evaluates if articles are relevant to user queries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        result_text = response.choices[0].message.content

        # Parse the score from the format "SCORE: X.X"
        try:
            # Find the score line
            score_line = [line for line in result_text.split('\n') if 'SCORE:' in line]
            if score_line:
                # Extract just the number
                score_text = score_line[0].split('SCORE:')[1].strip()
                relevance_score = float(score_text)
            else:
                # Fallback if format isn't followed
                relevance_score = 0.5

        except Exception as e:
            print(f"Error parsing relevance score: {e}")
            relevance_score = 0.5

        return float(relevance_score)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
