# Building AI Apps with Gradio

Use this repository to learn how to build AI apps with [Gradio](https://www.gradio.app/) and Google Gemini using `uv`. Each lesson is a tiny Python file that you can run locally to see the concept in action.

> [!IMPORTANT]
> You need to have `uv` installed on your machine. If you have not set it up yet, follow the installation guide in [this repository](https://github.com/kirenz/uv-setup).

You also need a Google Gemini API key. To get one, sign up for **Google AI Studio** at [https://ai.google/studio](https://ai.google/studio) and create an API key in the settings.

## Step-by-step instructions

If you are on macOS, open the built-in **Terminal** app. On Windows, open **Git Bash**.

1. Clone the repository  

   ```bash
   git clone https://github.com/kirenz/gradio-intro.git
   ```

   Change into the repository folder

   ```bash
   cd gradio-intro
   ```

2. Sync the Python environment defined in `pyproject.toml`  

   ```bash
   uv sync
   ```

   This installs all required packages in an isolated environment managed by `uv`.

3. Create a `.env` file for your Gemini API key  

   ```bash
   cat <<'ENV' > .env
   GEMINI_API_KEY=your_api_key_here
   ENV
   ```

4. Open the project in VS Code  

   ```bash
   code .
   ```

   You can also open the folder manually from within VS Code.

   Replace `your_api_key_here` in the `.env` file with the key you generated in Google AI Studio.

---

## What You'll Learn

- Launch quick interfaces around Python functions.
- Arrange layouts with Gradio Blocks.
- Store information between interactions with `gr.State`.
- Handle files and images.
- Connect to Google Gemini for text, chat, and vision.
- Stream model outputs so users see answers immediately.
- Add friendly validation and theming.


## Step-by-Step Examples

Paste one snippet at a time into your terminal. When the app starts, open the local URL (usually `http://127.0.0.1:7860`) in your browser. Stop the app with `Ctrl+C` when you are done.

### Step 1 – Hello, Gradio
Turns a simple function into an app that says hello.
```bash
uv run python step01_hello_gradio.py
```

### Step 2 – Components Playground
Combines text, dropdown, slider, and multiple outputs.
```bash
uv run python step02_components.py
```

### Step 3 – Blocks Layout
Shows how to arrange components with rows and columns.
```bash
uv run python step03_blocks_layout.py
```

### Step 4 – State & Events
Stores a list of items in session memory and keeps the UI updated.
```bash
uv run python step04_state_events.py
```

### Step 5 – Files & Images
Reads an uploaded image, reports its size, and shows a preview.
```bash
uv run python step05_file_image.py
```

### Step 6 – Gemini Text Generation
Connects your app to Gemini and shows the full response.
```bash
uv run python step06_gemini_text.py
```

### Step 7 – Gemini Streaming
Streams Gemini’s answer chunk by chunk for a responsive UX.
```bash
uv run python step07_gemini_stream.py
```

### Step 8 – Gemini Chatbot
Keeps conversation history and streams replies.
```bash
uv run python step08_gemini_chat.py
```

### Step 9 – Gemini Vision Q&A
Uploads an image and sends it with a question to Gemini.
```bash
uv run python step09_gemini_vision.py
```

### Step 10 – Friendly Error Handling
Uses `gr.Error` for a clear message when something goes wrong.
```bash
uv run python step10_error_handling.py
```

### Step 11 – Styling & Themes
Switches the Gradio theme for an instant visual upgrade.
```bash
uv run python step11_styling.py
```

### Step 12 – Handy LLM Helpers
Utility functions for prompt templates and bullet formatting.
```bash
uv run python step12_llm_patterns.py
```

### Bonus – Streaming Gemini Starter App
A one-file app that streams Gemini output for any prompt.
```bash
uv run python app.py
```

---

## Tips for Using Gemini

- Keep your `.env` file private so your API key never leaks.
- `"gemini-1.5-flash"` is fast and inexpensive; `"gemini-1.5-pro"` is better for complex reasoning and images.
- Streaming (steps 7, 8, and the bonus app) makes long answers feel responsive.
- If a request fails, check that inputs are not empty and that you have not exceeded rate limits.

---

## Troubleshooting Checklist
- “Invalid API key”? Confirm `.env` is in this folder and you called `load_dotenv()` before `genai.configure(...)`.
- App not loading? Verify the terminal shows `Running on ...` and that your virtual environment is active.
- Image upload slow or failing? Resize the image to something smaller first.
- Repeated model errors? Wait a bit and try again; you may have hit temporary limits.

---

## Practice Ideas
- **Beginner:** Add a language dropdown to Step 1 and return greetings in that language; ensure the name field is not empty.
- **Intermediate:** Add a reset button to the chatbot (Step 8); add a textbox for a custom “system role.”
- **Advanced:** Build a summariser that streams results (Step 7 style) and stores previous prompts so repeated requests return cached answers.

---

## Going Further
To deploy on Google Cloud with Vertex AI instead of the public Gemini API, install `google-cloud-aiplatform` (or `vertexai`) and authenticate with `gcloud`. The Gradio UI code stays the same—you only swap out the Gemini client.

---

Happy building! Keep experimenting, remix the snippets, and share your favourite tweaks with friends or classmates. Paste, run, and learn. 🚀
