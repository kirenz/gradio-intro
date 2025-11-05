"""Step 13: Generate short videos from text prompts using Gemini."""

import os
import tempfile
import time
from pathlib import Path
from typing import Tuple

import gradio as gr
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set GEMINI_API_KEY in your environment or .env file.")
client = genai.Client(api_key=api_key)

VIDEO_MODEL = "veo-3.1-generate-preview"
POLL_SECONDS = 6
MAX_POLLS = 30


def _wait_for_video(operation: types.GenerateVideosOperation) -> types.GenerateVideosOperation:
    """Poll the long-running operation until the video is ready or fails."""
    polls = 0
    while not operation.done:
        if polls >= MAX_POLLS:
            raise gr.Error(
                "Video generation is taking longer than expected. "
                "Please try again in a moment."
            )
        time.sleep(POLL_SECONDS)
        operation = client.operations.get(operation)
        polls += 1
    return operation


def generate_video(prompt: str) -> Tuple[str, str]:
    """Generate a video and return the local file path plus status details."""
    prompt = prompt.strip()
    if not prompt:
        raise gr.Error("Describe the video you want Gemini to create.")

    try:
        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            prompt=prompt,
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
        raise gr.Error("Gemini did not return a video. Try another prompt.")

    generated = videos[0]
    if generated.video is None:
        raise gr.Error("Gemini returned an empty video. Please try again.")

    try:
        video_bytes = client.files.download(file=generated.video)
    except errors.ClientError as err:
        raise gr.Error(
            f"Gemini finished but downloading the video failed ({err.status}). "
            "Please retry."
        ) from err

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(video_bytes)
    temp_file.flush()
    temp_file.close()

    video_path = Path(temp_file.name)
    return str(video_path), f"Saved result from `{VIDEO_MODEL}` to `{video_path.name}`."


with gr.Blocks(title="Gemini Video Generator") as demo:
    gr.Markdown(
        "## Gemini Video Generator\n"
        "Prompt Gemini to direct a short clip. One request can take a minute."
    )

    prompt_box = gr.Textbox(
        label="Video prompt",
        lines=4,
        placeholder=(
            "Example: Drone shot following a classic red convertible along a coastal road at sunset."
        ),
    )
    generate_button = gr.Button("Generate Video", variant="primary")
    reset_button = gr.Button("Start Over")

    output_video = gr.Video(label="Generated video")
    status_box = gr.Markdown(label="Status")

    gr.Examples(
        examples=[
            [
                "A timelapse of wildflowers blooming across a foggy valley at dawn, cinematic lighting.",
            ],
            [
                "A cyberpunk street scene with neon reflections on wet pavement, steady cam dolly shot.",
            ],
            [
                "An aerial shot soaring over snow-capped mountains toward a rising sun.",
            ],
        ],
        inputs=[prompt_box],
        label="Need ideas?",
    )

    generate_button.click(
        generate_video,
        inputs=prompt_box,
        outputs=[output_video, status_box],
        show_progress=True,
    )

    reset_button.click(
        lambda: ("", None, ""),
        inputs=[],
        outputs=[prompt_box, output_video, status_box],
    )


if __name__ == "__main__":
    demo.launch()
