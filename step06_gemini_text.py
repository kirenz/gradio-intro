"""Step 6: Connect a Gradio app to Gemini for text generation."""

import os

import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"


def generate_text(prompt: str) -> str:
    """Send the prompt to Gemini and return the full response."""
    if not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text


with gr.Blocks(title="Gemini Text Generator") as demo:
    gr.Markdown("### Ask Gemini to write or explain anything.")

    prompt_box = gr.Textbox(
        label="Prompt",
        lines=5,
        placeholder="Example: Summarize the main ideas from this topic…",
    )
    run_button = gr.Button("Generate", variant="primary")
    output_box = gr.Markdown(label="Response")

    run_button.click(generate_text, inputs=prompt_box, outputs=output_box)


if __name__ == "__main__":
    demo.launch()
