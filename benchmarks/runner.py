"""
Runner: Invokes the classifier_agent directly via ADK's InMemoryRunner.

Bypasses context_agent (no Qdrant retrieval).  Instead, synthetic values are
injected into the session state for `retrieved_context` and `refined_context`
so the classifier always has data to act on.

Routing detection — three-tier strategy (first match wins per event):
  1. Structured function_call object on a content Part  (fc.name in AGENT_TO_CATEGORY)
  2. JSON text part containing {"name": "transfer_to_agent", ...}  (ADK internal signal)
  3. event.author directly matching an AGENT_TO_CATEGORY key
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field

from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session
from google.genai import types as genai_types

from benchmarks.config import (
    AGENT_TO_CATEGORY,
    REQUEST_DELAY_SECONDS,
    SYNTHETIC_REFINED_CONTEXT,
    SYNTHETIC_RETRIEVED_CONTEXT,
)
from benchmarks.dataset import BenchmarkPrompt


@dataclass
class RunResult:
    """Holds the outcome of a single classifier invocation."""

    prompt: str
    expected_category: str
    is_ambiguous: bool
    routed_agent: str | None          # raw agent name, e.g. 'coding_agent'
    routed_category: str | None       # mapped label, e.g. 'coding'
    correct: bool
    classifier_reasoning: str         # text from classifier_decision state key
    raw_events: list[str] = field(default_factory=list)
    error: str | None = None
    latency_seconds: float = 0.0


# ── Routing detection ─────────────────────────────────────────────────────────

# Pattern that matches the transfer_to_agent JSON ADK emits as a text part,
# e.g.: {"name": "transfer_to_agent", "parameters": {"agent_name": "chat_agent"}}
_TRANSFER_PATTERN = re.compile(
    r'"name"\s*:\s*"transfer_to_agent".*?"agent_name"\s*:\s*"([^"]+)"',
    re.DOTALL,
)


def _detect_routed_agent(event) -> str | None:
    """
    Extract the specialist sub-agent name from an ADK event using three methods:

    1. Structured function_call Part  → fc.name in AGENT_TO_CATEGORY
    2. transfer_to_agent JSON in a text Part (ADK's internal routing signal)
    3. event.author directly matching a known agent name
    """
    content = getattr(event, "content", None)
    if content:
        for part in getattr(content, "parts", None) or []:
            # Tier 1: structured function_call object
            fc = getattr(part, "function_call", None)
            if fc:
                name = getattr(fc, "name", "") or ""
                if name in AGENT_TO_CATEGORY:
                    return name

            # Tier 2: transfer_to_agent JSON embedded in text
            text = getattr(part, "text", "") or ""
            if "transfer_to_agent" in text:
                match = _TRANSFER_PATTERN.search(text)
                if match:
                    agent_name = match.group(1)
                    if agent_name in AGENT_TO_CATEGORY:
                        return agent_name
                # Fallback: try full JSON parse if the text is valid JSON
                try:
                    payload = json.loads(text.strip())
                    if payload.get("name") == "transfer_to_agent":
                        agent_name = payload.get("parameters", {}).get("agent_name", "")
                        if agent_name in AGENT_TO_CATEGORY:
                            return agent_name
                except (json.JSONDecodeError, AttributeError):
                    pass

    # Tier 3: event.author is itself the agent name
    author = getattr(event, "author", "") or ""
    if author in AGENT_TO_CATEGORY:
        return author

    return None


async def run_single(
    runner: InMemoryRunner,
    session: Session,
    benchmark_prompt: BenchmarkPrompt,
) -> RunResult:
    """Run one prompt through the classifier and return the result."""
    start = time.perf_counter()
    routed_agent: str | None = None
    classifier_reasoning: str = ""
    raw_event_names: list[str] = []
    error: str | None = None

    try:
        user_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=benchmark_prompt.prompt)],
        )

        async for event in runner.run_async(
            user_id="benchmark",
            session_id=session.id,
            new_message=user_message,
        ):
            event_author: str = getattr(event, "author", "") or ""
            raw_event_names.append(event_author)

            detected = _detect_routed_agent(event)
            if detected:
                routed_agent = detected

        # Pull classifier reasoning from session state
        updated_session = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id="benchmark",
            session_id=session.id,
        )
        if updated_session and updated_session.state:
            classifier_reasoning = updated_session.state.get("classifier_decision", "")

    except Exception as exc:  # noqa: BLE001
        error = str(exc)

    latency = time.perf_counter() - start
    routed_category = AGENT_TO_CATEGORY.get(routed_agent) if routed_agent else None
    correct = routed_category == benchmark_prompt.expected_category

    return RunResult(
        prompt=benchmark_prompt.prompt,
        expected_category=benchmark_prompt.expected_category,
        is_ambiguous=benchmark_prompt.is_ambiguous,
        routed_agent=routed_agent,
        routed_category=routed_category,
        correct=correct,
        classifier_reasoning=classifier_reasoning,
        raw_events=raw_event_names,
        error=error,
        latency_seconds=latency,
    )


async def run_model_benchmark(
    model: str,
    prompts: list[BenchmarkPrompt],
    delay: float = REQUEST_DELAY_SECONDS,
    progress_callback=None,
) -> list[RunResult]:
    """
    Run the full prompt dataset against a single model.

    Builds a fresh InMemoryRunner with classifier_agent patched to `model`,
    then runs each prompt sequentially with `delay` seconds between calls.
    """
    # Patch the classifier model at runtime without mutating the live agent
    # permanently — we swap the model attribute, run, and restore it.
    from agent.sub_agents.classifier.agent import classifier_agent  # noqa: PLC0415

    original_model = classifier_agent.model
    classifier_agent.model = model

    try:
        runner = InMemoryRunner(
            agent=classifier_agent,
            app_name=f"benchmark_{model.replace('.', '_').replace('-', '_')}",
        )

        results: list[RunResult] = []

        for idx, bp in enumerate(prompts):
            # Fresh session per prompt — avoids state bleed between prompts
            session = await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id="benchmark",
                state={
                    "retrieved_context": SYNTHETIC_RETRIEVED_CONTEXT,
                    "refined_context": SYNTHETIC_REFINED_CONTEXT,
                },
            )

            result = await run_single(runner, session, bp)
            results.append(result)

            if progress_callback:
                progress_callback(model=model, idx=idx + 1, total=len(prompts), result=result)

            if idx < len(prompts) - 1:
                await asyncio.sleep(delay)

        return results

    finally:
        # Always restore the original model
        classifier_agent.model = original_model
