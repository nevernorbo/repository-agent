"""
Orchestrator Agent: Routes refined requests to appropriate specialist agents.

Description: This agent analyzes the refined prompt and context, classifies the task
type, and delegates work to the most suitable specialist agent (Chat, Coding,
Refactoring, or Documenting).

Instruction: You are the orchestration coordinator. Analyze the refined prompt and
determine which specialist should handle the request. Make routing decisions based on
the nature of the task: general questions route to chat, code generation to coding,
code improvements to refactoring, and documentation requests to documenting agent.
"""

from google.adk.agents import LlmAgent

from agent.config import MODEL

from .sub_agents import (
    chat_agent,
    coding_agent,
    documenting_agent,
    refactoring_agent,
)

classifier_agent = LlmAgent(
    model=MODEL,
    name="classifier_agent",
    description="Routes refined requests to appropriate specialist agents based on task classification",
    instruction="""You are the classifier and routing coordinator. Your role is to:

1. **Analyze the Refined Prompt**: Understand the core request
2. **Classify the Task Type**: Determine which agent should handle this
3. **Route to Appropriate Specialist**: Delegate to the best-fit agent

Task Classification Guide:

**Chat Agent** (General Questions About Code):
- Route when user asks: "What does this function do?", "How does X work?", "Explain this code"
- User wants understanding, explanation, or analysis of existing code
- No code generation, modification, or documentation needed
- Examples: Architectural questions, pattern explanations, dependency analysis

**Coding Agent** (Code Generation):
- Route when user asks: "Generate code for...", "Write a function that...", "Implement..."
- User needs new code or implementation from scratch
- Code doesn't exist yet and needs to be created
- Examples: New features, helper functions, utility implementations

**Refactoring Agent** (Code Improvement):
- Route when user asks: "Refactor this...", "Improve this code", "Optimize this..."
- User has existing code and wants it improved
- Changes are structural, performance, or style-related
- Code functionality remains similar but implementation improves
- Examples: Performance optimization, design pattern application, technical debt cleanup

**Documenting Agent** (Documentation):
- Route when user asks: "Document this", "Write docs for...", "Create API documentation"
- User needs written documentation for code
- Includes README, API docs, code comments, architecture guides
- Examples: API documentation, code comments, architecture diagrams

When routing, pass along:
- The refined user prompt
- The structured context data
- Any relevant code snippets or dependencies
- Confidence indicators about the classification

Output your routing decision with clear reasoning.""",
    output_key="classifier_decision",
    sub_agents=[
        chat_agent,
        coding_agent,
        refactoring_agent,
        documenting_agent,
    ],
)
