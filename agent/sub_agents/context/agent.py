from google.adk.agents import ParallelAgent

from .sub_agents import (
    prompt_refinement_agent,
    retrieval_agent,
)

# Stage 1: Parallel Context Retrieval
# Both retrieval and prompt refinement happen simultaneously
context_agent = ParallelAgent(
    name="context_agent",
    description="""Retrieves and prepares all codebase context needed for processing by querying agent memory with the user's prompt,
then returns all relevant code snippets, documentation and metadata for use by specialist agents.""",
    sub_agents=[
        retrieval_agent,
        prompt_refinement_agent,
    ],
)
