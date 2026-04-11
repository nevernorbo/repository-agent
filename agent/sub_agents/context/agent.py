from google.adk.agents import SequentialAgent

from .sub_agents import (
    prompt_refinement_agent,
    retrieval_agent,
)

context_agent = SequentialAgent(
    name="context_agent",
    description="""Retrieves and prepares all codebase context needed for processing by querying agent memory with the user's prompt,
then returns all relevant code snippets, documentation and metadata for use by specialist agents.""",
    sub_agents=[
        retrieval_agent,
        prompt_refinement_agent,
    ],
)
