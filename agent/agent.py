"""
Root Agent: Main entry point for the codebase RAG multi-agent system.

This agent orchestrates the entire workflow:
1. Retrieval Agent - Fetches context from Qdrant
2. Prompt Refinement Agent - Cleans and structures the prompt
3. Orchestrator Agent - Routes to appropriate specialist
4. Specialist Agents - Handles specific tasks (Chat, Coding, Refactoring, Documenting)

"""

from google.adk.agents import SequentialAgent

from .sub_agents import (
    classifier_agent,
    context_agent,
)

MODEL = "gemini-2.5-flash"

root_agent = SequentialAgent(
    name="codebase_rag_agent",
    description="Multi-agent orchestrator for intelligent codebase interaction, analysis, and modification. Routes requests through retrieval, refinement and specialized agents.",
    sub_agents=[
        context_agent,
        classifier_agent,
    ],
    # output_key="codebase_analysis_result",
)
