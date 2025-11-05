"""Step 8: Chat with Gemini and remember previous messages."""

from collections.abc import Iterable
from typing import Any, List

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
client = genai.Client()

MODEL_NAME = "gemini-2.0-flash"
SYSTEM_PROMPT = (
    "You are a helpful, concise assistant for business students. "
    "Answer clearly and add short examples when useful."
)


def _to_text(content: Any) -> str:
    """Normalize Gradio message content into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, Iterable):
        parts: List[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("text"):
                parts.append(part["text"])
        if parts:
            return "\n".join(parts)
    return ""


def respond(message: str, history: list[dict[str, str]]) -> str:
    """Send the full conversation to Gemini and return its reply."""
    conversation = history + [{"role": "user", "content": message}]
    contents = []
    for entry in conversation:
        text = _to_text(entry.get("content", ""))
        if not text:
            continue
        role = entry.get("role", "user")
        if role == "assistant":
            role = "model"
        if role not in {"user", "model"}:
            role = "user"
        contents.append(
            {
                "role": role,
                "parts": [{"text": text}],
            }
        )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )
    return response.text or "Sorry, I did not catch that."


demo = gr.ChatInterface(
    fn=respond,
    title="Gemini Chatbot",
    description="Ask anything about business, marketing, or finance. Gemini remembers the conversation.",
    type="messages",
)


if __name__ == "__main__":
    demo.launch()
