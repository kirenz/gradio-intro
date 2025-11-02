"""Step 8: Build a simple Gemini-powered chatbot."""

import os
from typing import Iterator, List

import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.0-flash"
SYSTEM_PROMPT = (
    "You are a helpful, concise assistant for business students. "
    "Answer clearly and add short examples when useful."
)


ChatHistory = List[List[str]]


def add_user_message(user_message: str, history: ChatHistory | None):
    """Append the user's message to the chat history and clear the input box."""
    text = user_message.strip()
    if not text:
        raise gr.Error("Please enter a message.")

    history = list(history or [])
    history.append([text, ""])
    return "", history, history


def _format_history_for_gemini(history: ChatHistory) -> list[dict[str, object]]:
    """Convert Gradio-style history into Gemini's expected structure."""
    gemini_history = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
    for user_text, bot_text in history:
        gemini_history.append({"role": "user", "parts": [user_text]})
        if bot_text:
            gemini_history.append({"role": "model", "parts": [bot_text]})
    return gemini_history


def chatbot_reply(history: ChatHistory) -> Iterator[tuple[ChatHistory, ChatHistory]]:
    """Stream the assistant's reply and update both the UI and the stored history."""
    if not history:
        return

    user_message = history[-1][0]
    previous_turns = history[:-1]

    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat(history=_format_history_for_gemini(previous_turns))

    answer = ""
    for chunk in chat.send_message(user_message, stream=True):
        if chunk.text:
            answer += chunk.text
            updated_history = previous_turns + [[user_message, answer]]
            yield updated_history, updated_history


with gr.Blocks(title="Gemini Chatbot") as demo:
    gr.Markdown("### Chat with Gemini and keep the conversation history.")

    chatbot = gr.Chatbot(label="Chat")
    state = gr.State([])

    with gr.Row():
        message = gr.Textbox(
            placeholder="Ask me anything about business, marketing, finance…",
            label="Your message",
            scale=8,
        )
        send = gr.Button("Send", scale=1, variant="primary")

    send.click(add_user_message, [message, state], [message, chatbot, state]).then(
        chatbot_reply, inputs=state, outputs=[chatbot, state]
    )

    message.submit(add_user_message, [message, state], [message, chatbot, state]).then(
        chatbot_reply, inputs=state, outputs=[chatbot, state]
    )


if __name__ == "__main__":
    demo.launch()
