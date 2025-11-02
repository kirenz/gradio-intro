"""Step 2: Mix and match Gradio components."""

import gradio as gr


def compute(name: str, mood: str, intensity: int):
    """Build a short message and a score from the user inputs."""
    message = f"{name} feels {mood}"
    score = len(name) * intensity
    return message, score


demo = gr.Interface(
    fn=compute,
    inputs=[
        gr.Textbox(label="Name"),
        gr.Dropdown(["happy", "curious", "tired"], label="Mood", value="curious"),
        gr.Slider(1, 10, value=3, step=1, label="Intensity"),
    ],
    outputs=[
        gr.Textbox(label="Message"),
        gr.Number(label="Score"),
    ],
    title="Components Demo",
    description="Try text, dropdown, and slider inputs with two outputs.",
)


if __name__ == "__main__":
    demo.launch()
