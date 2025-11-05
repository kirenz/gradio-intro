"""Step 15: Marketing video studio for Veo with brand and persona controls."""

import io
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple

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

DEFAULT_MODEL = "veo-3.1-generate-preview"
MODEL_CHOICES = [
    "veo-3.1-generate-preview",
    "veo-3.1-fast-generate-preview",
]
ASPECT_CHOICES = ["16:9", "9:16"]
RESOLUTION_CHOICES = ["720p", "1080p"]
PERSON_CHOICES = ["auto", "allow_adult", "allow_all", "dont_allow"]
CAMPAIGN_GOALS = [
    "Product launch awareness",
    "Lead generation",
    "Upsell existing customers",
    "Event promotion",
    "Brand storytelling",
    "App install growth",
]
DEFAULT_NEGATIVE = "low quality, jitter, unreadable text overlays, oversaturated colors, warped faces"
MAX_POLLS = 40
POLL_SECONDS = 6


def _pil_to_part(image: Optional[Image.Image]) -> Optional[types.Image]:
    if image is None:
        return None
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return types.Image(image_bytes=buffer.getvalue(), mime_type="image/png")


def _validate_resolution(aspect: str, resolution: str) -> None:
    if resolution == "1080p" and aspect != "16:9":
        raise gr.Error("1080p is only available when the aspect ratio is 16:9.")


def _cleanup_person_value(value: str) -> Optional[str]:
    if not value or value == "auto":
        return None
    return value


def _wait_for_video(operation: types.GenerateVideosOperation) -> types.GenerateVideosOperation:
    polls = 0
    while not operation.done:
        if polls >= MAX_POLLS:
            raise gr.Error(
                "Video generation is taking longer than expected. "
                "Try a shorter prompt or switch to the fast model."
            )
        time.sleep(POLL_SECONDS)
        operation = client.operations.get(operation)
        polls += 1
    return operation


def build_prompt(
    brand_name: str,
    brand_voice: str,
    persona_title: str,
    persona_details: str,
    campaign_goal: str,
    custom_goal: str,
    product_highlights: str,
    differentiators: str,
    call_to_action: str,
    visual_style: str,
    audio_direction: str,
    extra_notes: str,
    duration_seconds: int,
) -> str:
    brand_name = brand_name.strip()
    brand_voice = brand_voice.strip()
    persona_title = persona_title.strip()
    persona_details = persona_details.strip()
    campaign_goal = campaign_goal.strip()
    custom_goal = custom_goal.strip()
    product_highlights = product_highlights.strip()
    differentiators = differentiators.strip()
    call_to_action = call_to_action.strip()
    visual_style = visual_style.strip()
    audio_direction = audio_direction.strip()
    extra_notes = extra_notes.strip()

    objective = custom_goal or campaign_goal

    parts = []
    if brand_name:
        parts.append(
            f"Produce a {duration_seconds}-second marketing video for {brand_name}."
        )
    else:
        parts.append(f"Produce a {duration_seconds}-second marketing video.")

    if objective:
        parts.append(f"Campaign objective: {objective}.")

    if persona_title or persona_details:
        persona_lines = ["Target viewer:"]
        if persona_title:
            persona_lines.append(persona_title)
        if persona_details:
            persona_lines.append(persona_details)
        parts.append(" ".join(persona_lines))

    if product_highlights:
        parts.append(f"Showcase these key messages or offers: {product_highlights}.")

    if differentiators:
        parts.append(f"Brand differentiators to reinforce: {differentiators}.")

    if brand_voice:
        parts.append(f"Maintain a brand voice that is {brand_voice}.")

    if visual_style:
        parts.append(f"Visual direction and cinematography: {visual_style}.")

    if audio_direction:
        parts.append(f"Audio direction (music, ambience, dialogue cues): {audio_direction}.")

    if call_to_action:
        parts.append(f"End with a clear call-to-action: {call_to_action}.")

    if extra_notes:
        parts.append(f"Additional guidance: {extra_notes}.")

    parts.append("Include naturalistic motion and keep logos or on-screen text sharp and legible.")
    parts.append("Deliver a cohesive narrative arc that hooks the viewer in the opening seconds.")

    return "\n".join(parts)


def craft_brief(
    brand_name: str,
    brand_voice: str,
    persona_title: str,
    persona_details: str,
    campaign_goal: str,
    custom_goal: str,
    product_highlights: str,
    differentiators: str,
    call_to_action: str,
    visual_style: str,
    audio_direction: str,
    extra_notes: str,
    negative_prompt: str,
    duration_seconds: int,
) -> Tuple[str, str]:
    prompt_text = build_prompt(
        brand_name,
        brand_voice,
        persona_title,
        persona_details,
        campaign_goal,
        custom_goal,
        product_highlights,
        differentiators,
        call_to_action,
        visual_style,
        audio_direction,
        extra_notes,
        duration_seconds,
    )

    negative_prompt = negative_prompt.strip() or DEFAULT_NEGATIVE
    return prompt_text, negative_prompt


def advanced_generate(
    model: str,
    brand_name: str,
    brand_voice: str,
    persona_title: str,
    persona_details: str,
    campaign_goal: str,
    custom_goal: str,
    product_highlights: str,
    differentiators: str,
    call_to_action: str,
    visual_style: str,
    audio_direction: str,
    extra_notes: str,
    prompt_override: str,
    reference_image: Optional[Image.Image],
    negative_prompt: str,
    aspect_ratio: str,
    resolution: str,
    duration_seconds: int,
    generate_audio: bool,
    enhance_prompt: bool,
    person_generation: str,
    seed_text: str,
) -> Tuple[str, str]:
    _validate_resolution(aspect_ratio, resolution)

    prompt_override = prompt_override.strip()
    prompt_text = prompt_override or build_prompt(
        brand_name,
        brand_voice,
        persona_title,
        persona_details,
        campaign_goal,
        custom_goal,
        product_highlights,
        differentiators,
        call_to_action,
        visual_style,
        audio_direction,
        extra_notes,
        duration_seconds,
    )

    if not prompt_text:
        raise gr.Error("Add enough campaign details to craft a prompt.")

    start_image = _pil_to_part(reference_image)
    negative_prompt = negative_prompt.strip() or None
    person_value = _cleanup_person_value(person_generation)

    if seed_text.strip():
        try:
            seed = int(seed_text.strip())
        except ValueError as exc:
            raise gr.Error("Seed must be a whole number.") from exc
    else:
        seed = None

    source = types.GenerateVideosSource(prompt=prompt_text, image=start_image) if start_image else None

    config = types.GenerateVideosConfig(
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        duration_seconds=duration_seconds,
        generate_audio=generate_audio,
        enhance_prompt=enhance_prompt or None,
        negative_prompt=negative_prompt,
        person_generation=person_value,
        seed=seed,
    )

    try:
        operation = client.models.generate_videos(
            model=model,
            prompt=None if source else prompt_text,
            source=source,
            config=config,
        )
    except errors.ClientError as err:
        raise gr.Error(
            f"Gemini video generation failed ({err.status}). "
            f"{err.message} Ensure your account has access to {model}."
        ) from err

    operation = _wait_for_video(operation)

    if operation.error:
        raise gr.Error(operation.error.get("message", "Veo returned an unknown error."))

    response = operation.response or operation.result
    videos = response.generated_videos if response else None
    if not videos:
        raise gr.Error("Gemini did not return a video. Try refining your brief or settings.")

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

    descriptors = [
        f"**Brand:** {brand_name or '—'}",
        f"**Persona:** {persona_title or '—'}",
        f"**Goal:** {(custom_goal or campaign_goal or '—')}",
        f"**Model:** `{model}`",
        f"**Aspect:** {aspect_ratio}",
        f"**Resolution:** {resolution}",
        f"**Duration:** {duration_seconds}s",
        f"**Audio:** {'On' if generate_audio else 'Off'}",
    ]
    if negative_prompt:
        descriptors.append(f"**Negative prompt:** `{negative_prompt}`")
    if person_value:
        descriptors.append(f"**Person policy:** `{person_value}`")
    if seed is not None:
        descriptors.append(f"**Seed:** {seed}")
    if start_image:
        descriptors.append("**Reference image:** provided")

    status = (
        f"Saved result from `{model}` to `{video_path.name}`.\n\n"
        + " | ".join(descriptors)
        + "\n\nDownload the MP4 below to share with your marketing squad."
    )
    return str(video_path), status


with gr.Blocks(title="Marketing Video Studio for Veo") as demo:
    gr.Markdown(
        "## Marketing Video Studio for Veo\n"
        "Capture your campaign brief, craft a polished prompt, and render a Veo marketing clip."
    )

    with gr.Tab("Campaign Brief"):
        with gr.Row():
            brand_name = gr.Textbox(label="Brand name", placeholder="Example: Nimbus Bikes")
            brand_voice = gr.Textbox(
                label="Brand voice & tone",
                placeholder="Example: Bold, data-backed, upbeat optimism",
            )
            persona_title = gr.Textbox(
                label="Persona shorthand",
                placeholder="Example: Urban commuter, 28-40, eco-conscious",
            )

        persona_details = gr.Textbox(
            label="Persona insights",
            lines=3,
            placeholder="Pain points, motivations, favorite channels...",
        )

        with gr.Row():
            campaign_goal = gr.Dropdown(
                label="Primary objective",
                choices=CAMPAIGN_GOALS,
                value=CAMPAIGN_GOALS[0],
            )
            custom_goal = gr.Textbox(
                label="Custom objective (optional)",
                placeholder="Example: Boost trial sign-ups before trade show",
            )
            call_to_action = gr.Textbox(
                label="Call to action",
                placeholder="Example: Book a free fitting today",
            )

        product_highlights = gr.Textbox(
            label="Key message pillars",
            lines=3,
            placeholder="List 2-3 talking points or offers to spotlight.",
        )
        differentiators = gr.Textbox(
            label="Brand differentiators",
            lines=2,
            placeholder="Example: Lightweight carbon frame, lifetime maintenance, community rides",
        )

        visual_style = gr.Textbox(
            label="Visual direction",
            lines=3,
            placeholder="Camera moves, color palette, mood, setting, shot types...",
        )
        audio_direction = gr.Textbox(
            label="Audio & dialogue cues",
            lines=2,
            placeholder="Voiceover, dialogue lines, SFX, music genre...",
        )
        extra_notes = gr.Textbox(
            label="Extra notes",
            placeholder="Legal disclaimers, on-screen text, platform placement, etc.",
        )

    with gr.Tab("Model Controls"):
        with gr.Row():
            model_choice = gr.Dropdown(
                label="Veo model",
                choices=MODEL_CHOICES,
                value=DEFAULT_MODEL,
            )
            aspect_choice = gr.Radio(
                choices=ASPECT_CHOICES,
                value="16:9",
                label="Aspect ratio",
            )
            resolution_choice = gr.Radio(
                choices=RESOLUTION_CHOICES,
                value="720p",
                label="Resolution",
            )
            duration_slider = gr.Slider(
                minimum=4,
                maximum=8,
                value=8,
                step=1,
                label="Clip length (seconds)",
            )

        with gr.Row():
            audio_toggle = gr.Checkbox(label="Generate audio", value=True)
            enhance_toggle = gr.Checkbox(label="Enhance prompt", value=True)
            person_dropdown = gr.Dropdown(
                choices=PERSON_CHOICES,
                value="auto",
                label="Person generation policy",
                info="Region limits may apply.",
            )
            seed_box = gr.Textbox(
                label="Seed (optional integer)",
                placeholder="Leave blank for random seed",
            )

        reference_image = gr.Image(
            type="pil",
            image_mode="RGB",
            label="Optional reference frame",
        )
        negative_prompt_box = gr.Textbox(
            label="Negative prompt",
            placeholder=DEFAULT_NEGATIVE,
        )

    craft_button = gr.Button("Craft Marketing Prompt", variant="secondary")
    prompt_preview = gr.Textbox(
        label="Assembled Veo prompt",
        lines=8,
        placeholder="Click “Craft Marketing Prompt” after filling the brief.",
        interactive=True,
    )

    generate_button = gr.Button("Render Marketing Video", variant="primary")
    reset_button = gr.Button("Start Over")

    output_video = gr.Video(label="Generated video")
    status_box = gr.Markdown(label="Status & settings")

    gr.Examples(
        examples=[
            [
                "Nimbus Bikes",
                "Energetic, witty, city-smart",
                "Young urban commuter, values time savings",
                "Works downtown, wants to ditch gridlock while looking stylish and sustainable.",
                "Product launch awareness",
                "",
                "Highlight 5x faster commute, regenerative braking, concierge maintenance.",
                "Only bike with adaptive lighting + theft recovery service.",
                "Tap to book a free downtown test ride.",
                "Dynamic sunrise shots weaving through traffic, neon accents, kinetic typography on benefits.",
                "Voiceover from excited rider, subtle city ambience, upbeat electronic score.",
                "",
            ],
            [
                "Pulse Fuel",
                "Confident, expert, high-performance coach",
                "Endurance athlete juggling family & training",
                "Needs energy that is clean, science-backed, and portable.",
                "Lead generation",
                "",
                "Clinically proven electrolyte ratio, zero sugar, designed by sports scientists.",
                "Trusted by national triathlon team, NSF certified, smoother gut profile.",
                "Claim your performance starter pack.",
                "Split-screen of training visuals + product close-ups, bold kinetic infographics, warm sunrise palette.",
                "Pulse-like synth beats, heartbeat SFX transitions, coach whispers 'power your breakthrough'.",
                "Mention limited-time coach Q&A webinar registration.",
            ],
        ],
        inputs=[
            brand_name,
            brand_voice,
            persona_title,
            persona_details,
            campaign_goal,
            custom_goal,
            product_highlights,
            differentiators,
            call_to_action,
            visual_style,
            audio_direction,
            extra_notes,
        ],
        label="Load sample briefs",
    )

    craft_button.click(
        craft_brief,
        inputs=[
            brand_name,
            brand_voice,
            persona_title,
            persona_details,
            campaign_goal,
            custom_goal,
            product_highlights,
            differentiators,
            call_to_action,
            visual_style,
            audio_direction,
            extra_notes,
            negative_prompt_box,
            duration_slider,
        ],
        outputs=[prompt_preview, negative_prompt_box],
        show_progress=False,
    )

    generate_button.click(
        advanced_generate,
        inputs=[
            model_choice,
            brand_name,
            brand_voice,
            persona_title,
            persona_details,
            campaign_goal,
            custom_goal,
            product_highlights,
            differentiators,
            call_to_action,
            visual_style,
            audio_direction,
            extra_notes,
            prompt_preview,
            reference_image,
            negative_prompt_box,
            aspect_choice,
            resolution_choice,
            duration_slider,
            audio_toggle,
            enhance_toggle,
            person_dropdown,
            seed_box,
        ],
        outputs=[output_video, status_box],
        show_progress=True,
    )

    reset_button.click(
        lambda: (
            "",
            "",
            "",
            "",
            CAMPAIGN_GOALS[0],
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            DEFAULT_MODEL,
            "16:9",
            "720p",
            8,
            True,
            True,
            "auto",
            "",
            None,
            DEFAULT_NEGATIVE,
            None,
            "",
        ),
        inputs=[],
        outputs=[
            brand_name,
            brand_voice,
            persona_title,
            persona_details,
            campaign_goal,
            custom_goal,
            product_highlights,
            differentiators,
            call_to_action,
            visual_style,
            audio_direction,
            extra_notes,
            prompt_preview,
            model_choice,
            aspect_choice,
            resolution_choice,
            duration_slider,
            audio_toggle,
            enhance_toggle,
            person_dropdown,
            seed_box,
            reference_image,
            negative_prompt_box,
            output_video,
            status_box,
        ],
        queue=False,
    )


if __name__ == "__main__":
    demo.launch()
