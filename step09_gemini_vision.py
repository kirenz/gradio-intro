"""Step 9: Ask Gemini questions about an uploaded image."""

import io
import os

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set GEMINI_API_KEY in your environment or .env file.")
client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.0-flash"


def describe_image(question: str, img: Image.Image) -> str:
    """Send both the text question and the image to Gemini Vision."""
    if img is None:
        raise gr.Error("Please upload an image.")

    prompt = question.strip() or "Describe this image briefly."

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    contents = types.UserContent(
        parts=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        ]
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[contents],
        config=types.GenerateContentConfig(temperature=0.4),
    )
    if response.text:
        return response.text
    raise gr.Error("Gemini did not return an answer. Please try another image.")


with gr.Blocks(title="Gemini Vision Q&A") as demo:
    gr.Markdown("### Upload an image and ask a question about it.")

    with gr.Row():
        image_input = gr.Image(type="pil", label="Upload image")
        question_box = gr.Textbox(
            label="Question",
            placeholder="Example: What is happening in this picture?",
        )

    answer_box = gr.Markdown(label="Answer")
    with gr.Row():
        ask_button = gr.Button("Ask Gemini", variant="primary")
        reset_button = gr.Button("Start Over")

    ask_button.click(
        describe_image,
        inputs=[question_box, image_input],
        outputs=answer_box,
    )
    reset_button.click(
        lambda: (None, "", ""),
        inputs=[],
        outputs=[image_input, question_box, answer_box],
    )


if __name__ == "__main__":
    demo.launch()
