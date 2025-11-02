"""Step 12: Helpful utility functions for LLM apps."""


def build_prompt(task: str, style: str, text: str) -> str:
    """Create a reusable prompt template."""
    return (
        "You are a helpful assistant.\n"
        f"Task: {task}\n"
        f"Style: {style}\n\n"
        "Text:\n"
        f"{text}\n"
    )


def to_bullets(text: str) -> str:
    """Convert plain text into a bulleted list."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullets = [f"- {line}" for line in lines]
    return "\n".join(bullets)


if __name__ == "__main__":
    example_prompt = build_prompt(
        task="Explain this marketing concept",
        style="Friendly and short",
        text="Customer lifetime value tells us how much a client will spend with us.",
    )
    print("Prompt template example:\n")
    print(example_prompt)

    print("Bullet conversion example:\n")
    print(to_bullets("Line one\nLine two\nLine three"))
