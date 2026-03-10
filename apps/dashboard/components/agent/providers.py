"""LLM provider abstraction for Anthropic and OpenAI."""

from __future__ import annotations

import json

from config import AI_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY


def _messages_to_anthropic(msgs: list[dict]) -> list[dict]:
    """Convert internal message format to Anthropic API format."""
    out = []
    i = 0
    while i < len(msgs):
        m = msgs[i]
        role = m.get("role", "")
        content = m.get("content", "")

        if role == "system":
            i += 1
            continue  # system handled separately

        if role == "assistant" and "tool_calls" in m:
            blocks = []
            if content:
                blocks.append({"type": "text", "text": content})
            for tc in m["tool_calls"]:
                blocks.append({
                    "type": "tool_use",
                    "id": tc.get("id", ""),
                    "name": tc.get("name", ""),
                    "input": tc.get("input", {}),
                })
            out.append({"role": "assistant", "content": blocks})
            i += 1
            # Collect following tool messages into one user message
            tool_results = []
            while i < len(msgs) and msgs[i].get("role") == "tool":
                t = msgs[i]
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": t.get("tool_call_id", ""),
                    "content": t.get("content", ""),
                })
                i += 1
            if tool_results:
                out.append({"role": "user", "content": tool_results})
            continue

        if role == "tool":
            # Orphan tool message; wrap as user
            out.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": m.get("tool_call_id", ""), "content": m.get("content", "")}],
            })
            i += 1
            continue

        # Regular user or assistant
        out.append({"role": role, "content": content})
        i += 1
    return out


def _messages_to_openai(msgs: list[dict], system: str) -> list[dict]:
    """Convert internal format to OpenAI API format."""
    result = [{"role": "system", "content": system}]
    for m in msgs:
        role = m.get("role", "")
        content = m.get("content", "")
        if role == "system":
            continue
        if role == "assistant" and "tool_calls" in m:
            tc_list = []
            for tc in m["tool_calls"]:
                inp = tc.get("input", {})
                if not isinstance(inp, str):
                    inp = json.dumps(inp) if inp else "{}"
                tc_list.append({
                    "id": tc.get("id", ""),
                    "type": "function",
                    "function": {"name": tc.get("name", ""), "arguments": inp},
                })
            result.append({"role": "assistant", "content": content or None, "tool_calls": tc_list})
        elif role == "tool":
            result.append({
                "role": "tool",
                "tool_call_id": m.get("tool_call_id", ""),
                "content": content,
            })
        else:
            result.append({"role": role, "content": content})
    return result


def _to_anthropic_tools(tool_defs: list[dict]) -> list[dict]:
    """Convert OpenAI-style tool defs to Anthropic format."""
    tools = []
    for t in tool_defs:
        f = t.get("function", t)
        tools.append({
            "name": f.get("name", ""),
            "description": f.get("description", ""),
            "input_schema": f.get("parameters", {"type": "object", "properties": {}}),
        })
    return tools


def _to_openai_tools(tool_defs: list[dict]) -> list[dict]:
    """Pass through OpenAI format."""
    return tool_defs


def get_llm_client():
    """Return configured LLM client. Raises if provider or key missing."""
    if AI_PROVIDER == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        return AnthropicClient()
    if AI_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env")
        return OpenAIClient()
    raise ValueError(f"Unknown AI_PROVIDER: {AI_PROVIDER}. Use 'anthropic' or 'openai'.")


class AnthropicClient:
    """Claude via Anthropic SDK."""

    def __init__(self):
        import anthropic
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def chat_with_tools(self, messages: list[dict], tools: list[dict], system: str) -> dict:
        anth_tools = _to_anthropic_tools(tools)
        anth_messages = _messages_to_anthropic(messages)
        response = self._client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system,
            messages=anth_messages,
            tools=anth_tools,
            tool_choice="auto",
        )
        return self._parse_response(response)

    def _parse_response(self, response):
        content = response.content
        if len(content) == 0:
            return {"text": "", "tool_calls": []}
        text_parts = []
        tool_calls = []
        for block in content:
            if hasattr(block, "type"):
                if block.type == "text":
                    text_parts.append(block.text)
                if block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input if isinstance(block.input, dict) else {},
                    })
        return {"text": "".join(text_parts), "tool_calls": tool_calls}


class OpenAIClient:
    """GPT-4o via OpenAI SDK."""

    def __init__(self):
        from openai import OpenAI
        self._client = OpenAI(api_key=OPENAI_API_KEY)

    def chat_with_tools(self, messages: list[dict], tools: list[dict], system: str) -> dict:
        oai_messages = _messages_to_openai(messages, system)
        oai_tools = [
            {"type": "function", "function": t.get("function", t)}
            for t in tools
        ]
        response = self._client.chat.completions.create(
            model="gpt-4o",
            messages=oai_messages,
            tools=oai_tools,
            tool_choice="auto",
        )
        choice = response.choices[0]
        msg = choice.message
        if msg.tool_calls:
            tool_calls = []
            for tc in msg.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": json.loads(tc.function.arguments or "{}"),
                })
            return {"text": msg.content or "", "tool_calls": tool_calls}
        return {"text": msg.content or "", "tool_calls": []}
