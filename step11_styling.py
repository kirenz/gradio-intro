"""Step 11: Try different Gradio themes."""

import gradio as gr


theme = gr.themes.Soft()

with gr.Blocks(title="Themed App", theme=theme) as demo:
    gr.Markdown("## Nice theme ✨")
    user_text = gr.Textbox(label="Say something")
    output = gr.Markdown()
    user_text.change(lambda text: f"**You wrote:** {text}", inputs=user_text, outputs=output)


if __name__ == "__main__":
    demo.launch()
