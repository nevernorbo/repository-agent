"""
Retrieval Agent: Fetches contextual information from the Qdrant knowledge base.

Description: This agent initiates the multi-agent workflow by retrieving relevant
code context from the vector database based on the user's prompt.

Instruction: You are a retrieval specialist. Given a user prompt about a codebase,
call the 'search_codebase_api' tool to retrieve relevant code snippets, documentation,
and context from the knowledge base. Format the retrieved data nicely and pass it to
the next agent in the pipeline. Do not modify the content, just enhance it with
metadata about relevance and context relationships.
"""

from google.adk.agents import LlmAgent
from .search_tool import search_codebase_api

MODEL = "gemini-2.5-flash"

retrieval_agent = LlmAgent(
    model=MODEL,
    name="retrieval_agent",
    description="Retrieves contextual information from Qdrant knowledge base using API search",
    instruction="""You are a retrieval specialist agent. Your role is to:
1. Receive a user prompt about their codebase
2. Call the 'search_codebase_api' tool to search the knowledge base
3. Extract and format the returned code context, documentation, and dependencies
5. Pass the enriched context to the next agent

Important: Do not modify the actual code or documentation content, only enhance
its presentation with relationship information.""",
    tools=[search_codebase_api],
    output_key="retrieved_context",
)
