"""
Benchmark dataset: 40 prompts across 4 routing categories.

Each entry has:
  prompt            - The raw user message sent to the classifier
  expected_category - Ground-truth label ('chat'|'coding'|'refactoring'|'documenting')
  is_ambiguous      - True when two categories are plausible; scored leniently
  description       - Brief rationale for why this prompt belongs to its category
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkPrompt:
    prompt: str
    expected_category: str
    is_ambiguous: bool
    description: str


DATASET: list[BenchmarkPrompt] = [
    # ── CHAT (general questions / explanation) ────────────────────────────────
    BenchmarkPrompt(
        prompt="What does the `context_agent` do in this codebase?",
        expected_category="chat",
        is_ambiguous=False,
        description="Direct 'explain this component' question — clearly chat.",
    ),
    BenchmarkPrompt(
        prompt="How does the retrieval pipeline connect to Qdrant?",
        expected_category="chat",
        is_ambiguous=False,
        description="Architectural explanation of an existing data flow.",
    ),
    BenchmarkPrompt(
        prompt="What design patterns are used in the multi-agent orchestration?",
        expected_category="chat",
        is_ambiguous=False,
        description="Pattern analysis of existing architecture — explanatory.",
    ),
    BenchmarkPrompt(
        prompt="Can you explain the flow from user input to final response?",
        expected_category="chat",
        is_ambiguous=False,
        description="End-to-end workflow explanation, no code change requested.",
    ),
    BenchmarkPrompt(
        prompt="Where in the code is the Qdrant connection configured?",
        expected_category="chat",
        is_ambiguous=False,
        description="Code navigation / investigation question.",
    ),
    BenchmarkPrompt(
        prompt="What is the purpose of the `output_key` parameter on LlmAgent?",
        expected_category="chat",
        is_ambiguous=False,
        description="Conceptual question about framework usage — explanatory.",
    ),
    BenchmarkPrompt(
        prompt="Which sub-agents does the classifier route to?",
        expected_category="chat",
        is_ambiguous=False,
        description="Question about existing agent topology — no generation needed.",
    ),
    BenchmarkPrompt(
        prompt="How does the SequentialAgent differ from the LlmAgent in ADK?",
        expected_category="chat",
        is_ambiguous=False,
        description="Conceptual comparison, purely explanatory.",
    ),
    BenchmarkPrompt(
        prompt="Why does the prompt refinement agent set an output_key?",
        expected_category="chat",
        is_ambiguous=False,
        description="Question about the rationale of an existing design decision.",
    ),
    BenchmarkPrompt(
        prompt="What happens if the retrieval agent returns no results?",
        expected_category="chat",
        is_ambiguous=False,
        description="Behavioral analysis question — no code modification needed.",
    ),
    # ── CODING (new code generation) ─────────────────────────────────────────
    BenchmarkPrompt(
        prompt="Write a FastAPI health-check endpoint that returns service status.",
        expected_category="coding",
        is_ambiguous=False,
        description="Explicit 'write' instruction for new code that doesn't exist yet.",
    ),
    BenchmarkPrompt(
        prompt="Implement a retry decorator with exponential backoff in Python.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Implement' verb + new utility that doesn't exist in codebase.",
    ),
    BenchmarkPrompt(
        prompt="Generate a Pydantic model for a repository search response.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Generate' verb + new data model from scratch.",
    ),
    BenchmarkPrompt(
        prompt="Create a new ADK LlmAgent that summarises retrieved code snippets.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Create' verb + entirely new agent implementation.",
    ),
    BenchmarkPrompt(
        prompt="Write unit tests for the `search_codebase_api` tool.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Write tests' = generating new code files.",
    ),
    BenchmarkPrompt(
        prompt="Build a rate-limiter middleware for the repository API.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Build' verb + new middleware component.",
    ),
    BenchmarkPrompt(
        prompt="Implement a caching layer using Redis for Qdrant query results.",
        expected_category="coding",
        is_ambiguous=False,
        description="New integration from scratch — no existing cache code.",
    ),
    BenchmarkPrompt(
        prompt="Create a CLI script that runs the benchmark suite from the terminal.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Create a script' — new artifact from scratch.",
    ),
    BenchmarkPrompt(
        prompt="Write a function that extracts all import statements from a Python file.",
        expected_category="coding",
        is_ambiguous=False,
        description="New utility function requested explicitly.",
    ),
    BenchmarkPrompt(
        prompt="Add a new `analytics_agent` that logs routing decisions to a database.",
        expected_category="coding",
        is_ambiguous=False,
        description="'Add new agent' = code generation of a new component.",
    ),
    # ── REFACTORING (improving existing code) ────────────────────────────────
    BenchmarkPrompt(
        prompt="Refactor the `classifier_agent` to use a switch-case pattern instead of long if-else chains.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="'Refactor' verb + structural improvement of existing code.",
    ),
    BenchmarkPrompt(
        prompt="Optimize the Qdrant search query to reduce latency.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="'Optimize' verb + existing functionality being improved.",
    ),
    BenchmarkPrompt(
        prompt="Extract the model configuration into a shared base class to avoid duplication across agents.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="DRY refactoring of repeated config — existing code restructure.",
    ),
    BenchmarkPrompt(
        prompt="Clean up the `retrieval_agent` instructions to be more concise.",
        expected_category="refactoring",
        is_ambiguous=True,
        description="Ambiguous: 'clean up instructions' could be refactoring or documenting.",
    ),
    BenchmarkPrompt(
        prompt="Improve error handling in the search tool to surface meaningful messages.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="'Improve error handling' = restructuring existing code paths.",
    ),
    BenchmarkPrompt(
        prompt="Consolidate the four specialist agents into a single base class with shared logic.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="Structural consolidation of existing code — classic refactoring.",
    ),
    BenchmarkPrompt(
        prompt="Apply the Strategy design pattern to make the classifier routing logic pluggable.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="Design pattern application to existing code — refactoring.",
    ),
    BenchmarkPrompt(
        prompt="Remove the commented-out dead code from `agent/__init__.py`.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="Code cleanup of existing file — refactoring.",
    ),
    BenchmarkPrompt(
        prompt="Split the large classifier instruction string into smaller, reusable constants.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="Code organisation improvement of existing source — refactoring.",
    ),
    BenchmarkPrompt(
        prompt="Make the `context_agent` pipeline asynchronous for better throughput.",
        expected_category="refactoring",
        is_ambiguous=False,
        description="Performance refactoring of existing pipeline.",
    ),
    # ── DOCUMENTING (writing documentation) ──────────────────────────────────
    BenchmarkPrompt(
        prompt="Write a README for the `agent` directory explaining the multi-agent architecture.",
        expected_category="documenting",
        is_ambiguous=False,
        description="'Write a README' — clear documentation task.",
    ),
    BenchmarkPrompt(
        prompt="Generate docstrings for all public functions in `search_tool.py`.",
        expected_category="documenting",
        is_ambiguous=False,
        description="'Generate docstrings' — documentation generation.",
    ),
    BenchmarkPrompt(
        prompt="Create API documentation for the repository search endpoint.",
        expected_category="documenting",
        is_ambiguous=False,
        description="'Create API docs' — standard documenting task.",
    ),
    BenchmarkPrompt(
        prompt="Add inline comments explaining each step of the retrieval pipeline.",
        expected_category="documenting",
        is_ambiguous=False,
        description="'Add inline comments' = documentation within existing code.",
    ),
    BenchmarkPrompt(
        prompt="Write an architecture guide explaining how the agents communicate via session state.",
        expected_category="documenting",
        is_ambiguous=False,
        description="Architecture guide writing — documentation task.",
    ),
    BenchmarkPrompt(
        prompt="Document the environment variables required by the agent service.",
        expected_category="documenting",
        is_ambiguous=False,
        description="'Document environment variables' — pure documentation.",
    ),
    BenchmarkPrompt(
        prompt="Improve the docstring on the `classifier_agent` to better describe its routing logic.",
        expected_category="documenting",
        is_ambiguous=True,
        description="Ambiguous: improving an existing docstring overlaps with refactoring.",
    ),
    BenchmarkPrompt(
        prompt="Write a CHANGELOG entry describing the new benchmark framework.",
        expected_category="documenting",
        is_ambiguous=False,
        description="'Write CHANGELOG' — explicit documentation artifact.",
    ),
    BenchmarkPrompt(
        prompt="Create a sequence diagram showing the agent orchestration flow.",
        expected_category="documenting",
        is_ambiguous=False,
        description="Architecture diagram documentation.",
    ),
    BenchmarkPrompt(
        prompt="Add type annotations and docstrings to the `run_benchmark.py` script.",
        expected_category="documenting",
        is_ambiguous=True,
        description="Ambiguous: adding type hints could be refactoring; docstrings are documenting.",
    ),
]
