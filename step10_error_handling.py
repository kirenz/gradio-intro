"""Step 10: Handle errors and guide the user."""

import gradio as gr


def safe_divide(a: float, b: float) -> float:
    """Divide two numbers with a friendly error message for b = 0."""
    if b == 0:
        raise gr.Error("Division by zero is not allowed.")
    return a / b


demo = gr.Interface(
    fn=safe_divide,
    inputs=[gr.Number(label="Numerator"), gr.Number(label="Denominator")],
    outputs=gr.Number(label="Result"),
    title="Safe Divider",
    description="Enter two numbers. If the denominator is zero, a helpful error appears.",
)


if __name__ == "__main__":
    demo.launch()
