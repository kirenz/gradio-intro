"""Step 9: Ask Gemini questions about an uploaded image."""

import io
import os

import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.0-flash"


def describe_image(question: str, img: Image.Image) -> str:
    """Send both the text question and the image to Gemini Vision."""
    if img is None:
        raise gr.Error("Please upload an image.")

    prompt = question.strip() or "Describe this image briefly."

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(
        [
            {"text": prompt},
            {"mime_type": "image/png", "data": image_bytes},
        ]
    )
    return response.text


with gr.Blocks(title="Gemini Vision Q&A") as demo:
    gr.Markdown("### Upload an image and ask a question about it.")

    with gr.Row():
        image_input = gr.Image(type="pil", label="Upload image")
        question_box = gr.Textbox(
            label="Question",
            placeholder="Example: What is happening in this picture?",
        )

    answer_box = gr.Markdown(label="Answer")
    ask_button = gr.Button("Ask Gemini", variant="primary")

    ask_button.click(
        describe_image,
        inputs=[question_box, image_input],
        outputs=answer_box,
    )


if __name__ == "__main__":
    demo.launch()
