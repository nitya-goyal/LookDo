import os
import sys
import io
import json
from dotenv import load_dotenv

load_dotenv()

from PIL import Image
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set.", flush=True)
    sys.exit(1)


def sanitize(text: str) -> str:
    """Ensure API key is never exposed in output or errors."""
    if api_key and api_key in text:
        text = text.replace(api_key, "[REDACTED_API_KEY]")
    return text


def run_test():
    client = genai.Client(api_key=api_key)
    model_id = sys.argv[1] if len(sys.argv) > 1 else os.getenv("LOOKDO_GEMMA_MODEL", "gemma-4-31b-it")

    print(f"Connecting to Gemma API with model: {model_id}...", flush=True)

    img = Image.new("RGB", (200, 200), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
    prompt = (
        "You are LookDo UI element locator. The user instruction is: \"click the button\".\n"
        "Return strict JSON only matching this schema:\n"
        "{\n"
        "  \"element_label\": \"...\",\n"
        "  \"element_type\": \"...\",\n"
        "  \"bounding_box\": {\n"
        "    \"left\": 0.0,\n"
        "    \"top\": 0.0,\n"
        "    \"right\": 1.0,\n"
        "    \"bottom\": 1.0\n"
        "  },\n"
        "  \"confidence\": 0.0,\n"
        "  \"explanation\": \"...\",\n"
        "  \"suggested_action\": \"...\"\n"
        "}\n"
        "Do not include any text outside the JSON block."
    )

    print("Sending request to model...", flush=True)
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[part, prompt],
        )
        print("Gemma API Call Succeeded!", flush=True)
        response_text = sanitize(response.text or "")
        print(f"Response: {response_text}", flush=True)
        return True, response_text
    except Exception as e:
        err_msg = sanitize(f"{type(e).__name__}: {e}")
        print(f"Gemma API Call Failed: {err_msg}", flush=True)
        return False, err_msg


if __name__ == "__main__":
    success, _ = run_test()
    if not success:
        sys.exit(1)
