"""Step 7: Stream Gemini responses as they arrive."""

import os
from typing import Iterator

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


def stream_text(prompt: str) -> Iterator[str]:
    """Yield partial Gemini responses so the UI updates live."""
    if not prompt.strip():
        yield "Please enter a prompt to begin."
        return

    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7),
    )
    collected: list[str] = []
    for chunk in stream:
        if chunk.text:
            collected.append(chunk.text)
            yield "".join(collected)


with gr.Blocks(title="Gemini Streaming") as demo:
    gr.Markdown("### Watch the response build word by word.")

    prompt_box = gr.Textbox(label="Prompt", lines=4)
    run_button = gr.Button("Stream response", variant="primary")
    output_box = gr.Markdown(label="Response")

    run_button.click(stream_text, inputs=prompt_box, outputs=output_box)


if __name__ == "__main__":
    demo.launch()
