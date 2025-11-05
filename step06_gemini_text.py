"""Step 6: Connect a Gradio app to Gemini for text generation."""

import os

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


def generate_text(prompt: str) -> str:
    """Send the prompt to Gemini and return the full response."""
    if not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7),
    )
    if response.text:
        return response.text
    raise gr.Error("The model did not return any text. Please try another prompt.")


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
