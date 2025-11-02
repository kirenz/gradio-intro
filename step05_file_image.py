"""Step 5: Work with file uploads and images."""

from typing import Tuple

import gradio as gr
from PIL import Image


def image_info(img: Image.Image) -> Tuple[str, Image.Image]:
    """Return the image size and echo the image back to the UI."""
    if img is None:
        raise gr.Error("Please upload an image to continue.")

    width, height = img.size
    info = f"Image size: {width} × {height} pixels"
    return info, img


with gr.Blocks(title="Files & Images") as demo:
    gr.Markdown("### Upload an image to see its size and a preview.")

    with gr.Row():
        img_in = gr.Image(label="Upload image", type="pil")
        details = gr.Textbox(label="Details")
        img_out = gr.Image(label="Preview")

    img_in.change(image_info, inputs=img_in, outputs=[details, img_out])


if __name__ == "__main__":
    demo.launch()
