from google.adk.agents import ParallelAgent

from .sub_agents import (
    retrieval_agent,
    prompt_refinement_agent,
)

MODEL_GEMINI_2_5_FLASH = "gemini-2.5-flash"

# Stage 1: Parallel Context Retrieval
# Both retrieval and prompt refinement happen simultaneously
context_agent = ParallelAgent(
    name="context_agent",
    description="""Retrieves and prepares all codebase context needed for intelligent
downstream processing by querying the vector database with the user's prompt,
then returning a structured bundle of relevant code snippets, documentation,
and dependency information enriched with relevance scores and relationship metadata for use by later agents.""",
    sub_agents=[
        retrieval_agent,
        prompt_refinement_agent,
    ],
)
