"""Step 7: Stream Gemini responses as they arrive."""

import os
from typing import Iterator

import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.0-flash"


def stream_text(prompt: str) -> Iterator[str]:
    """Yield partial Gemini responses so the UI updates live."""
    if not prompt.strip():
        yield "Please enter a prompt to begin."
        return

    model = genai.GenerativeModel(MODEL_NAME)
    for chunk in model.generate_content(prompt, stream=True):
        if chunk.text:
            yield chunk.text


with gr.Blocks(title="Gemini Streaming") as demo:
    gr.Markdown("### Watch the response build word by word.")

    prompt_box = gr.Textbox(label="Prompt", lines=4)
    run_button = gr.Button("Stream response", variant="primary")
    output_box = gr.Markdown(label="Response")

    run_button.click(stream_text, inputs=prompt_box, outputs=output_box)


if __name__ == "__main__":
    demo.launch()
