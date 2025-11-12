"""
Root Agent: Main entry point for the codebase RAG multi-agent system.

This agent orchestrates the entire workflow:
1. Retrieval Agent - Fetches context from Qdrant
2. Prompt Refinement Agent - Cleans and structures the prompt
3. Orchestrator Agent - Routes to appropriate specialist
4. Specialist Agents - Handles specific tasks (Chat, Coding, Refactoring, Documenting)

"""

from google.adk.agents import Agent

from .sub_agents import (
    retrieval_agent,
    prompt_refinement_agent,
    classifier_agent,
    chat_agent,
    coding_agent,
    refactoring_agent,
    documenting_agent,
)


MODEL = "gemini-2.5-flash"

root_agent = Agent(
    name="codebase_rag_agent",
    model=MODEL,
    description="Multi-agent orchestrator for intelligent codebase interaction, analysis, and modification. Routes requests through retrieval, refinement, and specialized agents.",
    instruction="""You are the main Codebase RAG Orchestrator coordinating a sophisticated multi-agent team.

Your responsibilities:
1. Accept user queries about their codebase
2. Delegate to the retrieval agent to fetch relevant context from Qdrant
3. Forward refined context to the prompt refinement agent for structure and clarity
4. Use the classifier agent to classify the request type
5. Route to the appropriate specialist agent:
   - Chat Agent: For general questions about code (explanations, analysis)
   - Coding Agent: For code generation requests (new features, implementations)
   - Refactoring Agent: For code improvement (optimization, refactoring, modernization)
   - Documenting Agent: For documentation requests (API docs, guides, comments)

You orchestrate this pipeline seamlessly, ensuring the refined context flows through each stage.
When you delegate to a sub-agent, provide clear context about what has been discovered and what
the user is trying to accomplish.

Important: Do not attempt to directly fulfill requests yourself. Always use your specialized
sub-agents to ensure high-quality, focused responses.""",
    sub_agents=[
        retrieval_agent,
        prompt_refinement_agent,
        classifier_agent,
        chat_agent,
        coding_agent,
        refactoring_agent,
        documenting_agent,
    ],
    output_key="codebase_analysis_result",
)
