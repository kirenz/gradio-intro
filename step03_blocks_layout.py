"""Step 3: Arrange components with Gradio Blocks."""

import gradio as gr


def to_upper(text: str) -> str:
    """Convert text to upper case."""
    return text.upper()


with gr.Blocks(title="Blocks Basics") as demo:
    gr.Markdown("### Blocks Layout\nUse rows and columns to place components.")

    with gr.Row():
        with gr.Column(scale=2):
            inp = gr.Textbox(label="Enter text")
            btn = gr.Button("Uppercase")
        with gr.Column(scale=1):
            out = gr.Textbox(label="Result")

    btn.click(fn=to_upper, inputs=inp, outputs=out)


if __name__ == "__main__":
    demo.launch()
