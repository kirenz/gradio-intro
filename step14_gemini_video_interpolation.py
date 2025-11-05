"""Step 14: Morph between two images with Gemini Veo."""

import io
import os
import tempfile
import time
from pathlib import Path
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

VIDEO_MODEL = "veo-3.1-generate-preview"
POLL_SECONDS = 6
MAX_POLLS = 30


def _pil_to_part(image: Image.Image) -> types.Image:
    """Convert a PIL image to a Gemini Image message."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return types.Image(image_bytes=buffer.getvalue(), mime_type="image/png")


def _wait_for_video(operation: types.GenerateVideosOperation) -> types.GenerateVideosOperation:
    """Poll the long-running operation until the video is ready or times out."""
    polls = 0
    while not operation.done:
        if polls >= MAX_POLLS:
            raise gr.Error(
                "Video generation is taking longer than expected. Please try again shortly."
            )
        time.sleep(POLL_SECONDS)
        operation = client.operations.get(operation)
        polls += 1
    return operation


def generate_transition(prompt: str, first_frame: Image.Image, last_frame: Image.Image) -> Tuple[str, str]:
    """Blend between two uploaded frames and return the generated clip."""
    prompt = prompt.strip()
    if not prompt:
        raise gr.Error("Describe the story you want Gemini to tell.")
    if first_frame is None or last_frame is None:
        raise gr.Error("Upload both a starting image and an ending image.")

    start_image = _pil_to_part(first_frame)
    end_image = _pil_to_part(last_frame)

    try:
        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            source=types.GenerateVideosSource(
                prompt=prompt,
                image=start_image,
            ),
            config=types.GenerateVideosConfig(
                last_frame=end_image,
            ),
        )
    except errors.ClientError as err:
        raise gr.Error(
            f"Gemini video generation failed ({err.status}). "
            f"{err.message} Ensure your account has access to {VIDEO_MODEL}."
        ) from err

    operation = _wait_for_video(operation)

    if operation.error:
        raise gr.Error(
            f"Gemini reported an error: {operation.error.get('message', 'Unknown error')}"
        )

    response = operation.response or operation.result
    videos = response.generated_videos if response else None
    if not videos:
        raise gr.Error("Gemini did not return a video. Try a different prompt or images.")

    generated = videos[0]
    if generated.video is None:
        raise gr.Error("Gemini returned an empty video. Please try again.")

    try:
        video_bytes = client.files.download(file=generated.video)
    except errors.ClientError as err:
        raise gr.Error(
            f"Gemini finished but downloading the video failed ({err.status}). Please retry."
        ) from err

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(video_bytes)
    temp_file.flush()
    temp_file.close()

    video_path = Path(temp_file.name)
    status = (
        f"Saved morph from `{VIDEO_MODEL}` to `{video_path.name}`. "
        "Download the MP4 to keep the result."
    )
    return str(video_path), status


with gr.Blocks(title="Gemini Image-to-Video Transition") as demo:
    gr.Markdown(
        "## Gemini Image-to-Video Transition\n"
        "Upload a starting frame, an ending frame, and describe the scene. "
        "Gemini Veo will create a clip that bridges the two images."
    )

    prompt_box = gr.Textbox(
        label="Video prompt",
        lines=4,
        placeholder="Example: A ghostly figure fades from the swing as mist thickens in the moonlight.",
    )

    with gr.Row():
        first_image = gr.Image(
            type="pil",
            label="Starting image",
            image_mode="RGB",
        )
        last_image = gr.Image(
            type="pil",
            label="Ending image",
            image_mode="RGB",
        )

    generate_button = gr.Button("Generate Transition", variant="primary")
    reset_button = gr.Button("Start Over")

    output_video = gr.Video(label="Generated transition")
    status_box = gr.Markdown(label="Status")

    gr.Examples(
        examples=[
            [
                "A cinematic, haunting transition where a spirit dissolves into mist beneath an ancient tree.",
            ],
        ],
        inputs=[prompt_box],
        label="Need a prompt?",
    )

    generate_button.click(
        generate_transition,
        inputs=[prompt_box, first_image, last_image],
        outputs=[output_video, status_box],
        show_progress=True,
    )

    reset_button.click(
        lambda: ("", None, None, None, ""),
        inputs=[],
        outputs=[prompt_box, first_image, last_image, output_video, status_box],
        queue=False,
    )


if __name__ == "__main__":
    demo.launch()
