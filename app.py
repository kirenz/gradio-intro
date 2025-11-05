"""Run the full Gemini starter app with streaming output.

Usage:
    uv run python app.py
"""

import os
from typing import Iterator, List

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set GEMINI_API_KEY in your environment or .env file.")
client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.0-flash"


def generate(prompt: str) -> Iterator[str]:
    """Stream the Gemini response chunk by chunk."""
    if not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    chunks: List[str] = []
    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7),
    )
    for chunk in stream:
        if chunk.text:
            chunks.append(chunk.text)
            yield "".join(chunks)


with gr.Blocks(title="Gemini Starter") as demo:
    gr.Markdown("# Gemini Starter\nEnter a prompt and stream the result.")
    prompt_box = gr.Textbox(
        placeholder="Write a haiku about data science...",
        lines=4,
        label="Prompt",
    )
    go_button = gr.Button("Generate", variant="primary")
    output = gr.Markdown()

    go_button.click(generate, inputs=prompt_box, outputs=output)


if __name__ == "__main__":
    demo.launch()
