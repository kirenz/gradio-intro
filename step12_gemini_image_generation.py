"""Step 12: Generate brand-new images from a text prompt with Gemini."""

import io
import os
from typing import Tuple

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from PIL import Image


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set GEMINI_API_KEY in your environment or .env file.")
client = genai.Client(api_key=api_key)

IMAGE_MODEL = "imagen-4.0-generate-001"
DEFAULT_ASPECT = "1:1"


def generate_image(prompt: str, aspect_ratio: str) -> Tuple[Image.Image, str]:
    """Create a single Gemini image and return it with a short status string."""
    prompt = prompt.strip()
    if not prompt:
        raise gr.Error("Add a short description of what you want to see.")

    try:
        response = client.models.generate_images(
            model=IMAGE_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio or None,
            ),
        )
    except errors.ClientError as err:
        raise gr.Error(
            f"Gemini image generation failed ({err.status}). "
            f"{err.message} Ensure your account has access to {IMAGE_MODEL}."
        ) from err

    images = response.generated_images or []
    if not images:
        raise gr.Error("Gemini did not return an image. Try another prompt.")

    generated = images[0]
    if generated.rai_filtered_reason:
        raise gr.Error(
            f"Gemini blocked this request: {generated.rai_filtered_reason}. "
            "Try rephrasing your prompt."
        )

    if not generated.image or not generated.image.image_bytes:
        raise gr.Error("Gemini returned empty image bytes. Please try again.")

    image = Image.open(io.BytesIO(generated.image.image_bytes)).convert("RGB")
    used_prompt = generated.enhanced_prompt or prompt
    return image, f"Prompt sent to the model: `{used_prompt}`"


with gr.Blocks(title="Gemini Image Generator") as demo:
    gr.Markdown(
        "## Gemini Image Generator\n"
        "Describe the scene you want and Gemini will paint it for you."
    )

    with gr.Row():
        prompt_box = gr.Textbox(
            label="Image prompt",
            placeholder="Example: A watercolor illustration of a cozy reading nook",
            lines=3,
        )
        aspect_choice = gr.Radio(
            choices=["1:1", "4:3", "3:4", "16:9", "9:16"],
            value=DEFAULT_ASPECT,
            label="Aspect ratio",
        )

    with gr.Row():
        submit = gr.Button("Generate Image", variant="primary")
        reset = gr.Button("Start Over")

    with gr.Row():
        output_image = gr.Image(label="Generated image")
        prompt_details = gr.Markdown(label="Model settings")

    gr.Examples(
        examples=[
            ["A friendly robot chef cooking ramen in a neon-lit kitchen", DEFAULT_ASPECT],
            ["An aerial photo of futuristic floating islands at sunrise", "16:9"],
            ["A stained glass window depicting a peaceful forest temple", "3:4"],
        ],
        inputs=[prompt_box, aspect_choice],
        label="Need ideas?",
    )

    submit.click(
        generate_image,
        inputs=[prompt_box, aspect_choice],
        outputs=[output_image, prompt_details],
    )

    reset.click(
        lambda: ("", DEFAULT_ASPECT, None, ""),
        inputs=[],
        outputs=[prompt_box, aspect_choice, output_image, prompt_details],
    )

if __name__ == "__main__":
    demo.launch()
