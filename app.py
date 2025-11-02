"""Run the full Gemini starter app with streaming output.

Usage:
    python app.py
"""

import os
from typing import Iterator, List

import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"


def generate(prompt: str) -> Iterator[str]:
    """Stream the Gemini response chunk by chunk."""
    if not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    model = genai.GenerativeModel(MODEL_NAME)
    chunks: List[str] = []
    for chunk in model.generate_content(prompt, stream=True):
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
