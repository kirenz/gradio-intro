"""Step 1: Say hello with Gradio."""

import gradio as gr


def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}! 👋"


demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Your name"),
    outputs=gr.Textbox(label="Greeting"),
    title="Hello Gradio",
    description="Type a name to see a friendly message.",
)


if __name__ == "__main__":
    demo.launch()
