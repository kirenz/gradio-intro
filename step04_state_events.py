"""Step 4: Remember data with state and events."""

from typing import List, Optional, Tuple

import gradio as gr


def add_item(new_item: str, items: Optional[List[str]]):
    """Store each item in the session state and update the list display."""
    items = list(items or [])
    text = (new_item or "").strip()
    if not text:
        highlighted: List[Tuple[str, Optional[str]]] = [(value, None) for value in items]
        return items, "", highlighted, "Please type something before adding."

    items.append(text)
    highlighted = [(value, None) for value in items]
    return items, "", highlighted, ""


with gr.Blocks(title="State & Events") as demo:
    gr.Markdown("### Add items and keep them in session memory.")

    items_state = gr.State([])

    with gr.Row():
        new_item = gr.Textbox(label="New item", placeholder="Type something…")
        add_btn = gr.Button("Add", variant="primary")

    listbox = gr.HighlightedText(label="Saved items", combine_adjacent=True)
    status = gr.Markdown("")

    add_btn.click(add_item, [new_item, items_state], [items_state, new_item, listbox, status])
    new_item.submit(add_item, [new_item, items_state], [items_state, new_item, listbox, status])


if __name__ == "__main__":
    demo.launch()
