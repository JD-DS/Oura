"""Agent orchestrator: tool-use loop and conversation management."""

from __future__ import annotations

import json

from components.agent.prompts import SYSTEM_PROMPT
from components.agent.providers import get_llm_client
from components.agent.tools import TOOL_DEFINITIONS, execute_tool

MAX_TOOL_ITERATIONS = 5


def run_assistant_turn(
    messages: list[dict],
    token: str,
    sandbox: bool,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    charts_out: list | None = None,
) -> tuple[str, list[dict]]:
    """
    Run one assistant turn. May involve multiple LLM calls if tools are used.
    Returns (final_text, updated_messages).
    If charts_out is provided, generate_chart tool appends {'fig_json': ...} for rendering.
    """
    client = get_llm_client()
    history = list(messages)
    iterations = 0
    charts = charts_out if charts_out is not None else []

    system = SYSTEM_PROMPT
    if start_date and end_date:
        system += f"\n\nThe user's selected date range is {start_date} to {end_date}. Use these dates when fetching Oura data unless the user specifies otherwise."

    while iterations < MAX_TOOL_ITERATIONS:
        iterations += 1
        response = client.chat_with_tools(history, TOOL_DEFINITIONS, system)
        text = response.get("text", "").strip()
        tool_calls = response.get("tool_calls", [])

        if not tool_calls:
            # Final response
            if text:
                history.append({"role": "assistant", "content": text})
            return (text, history)

        # Append assistant message with tool calls
        history.append({"role": "assistant", "content": text, "tool_calls": tool_calls})

        # Execute tools and append results
        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("input", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            result = execute_tool(name, args, token, sandbox, charts_out=charts)
            history.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": str(result)[:8000],  # Limit length
            })

    return ("I hit the tool limit. Please try a simpler question.", history)
