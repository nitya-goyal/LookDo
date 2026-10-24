# LookDo 👁️

### Multimodal UI Navigation & Element Locator

LookDo uses Gemma 4 to understand a user interface screenshot together with natural-language intent, identify the UI element the user means, and visually highlight it.

**Tell LookDo what you want to do. It finds where to do it.**

## Problem

Modern interfaces can be visually dense and difficult to navigate, especially for users who do not know where an action is located or find precise navigation difficult.

## Solution

The user provides:

- A screenshot
- Natural-language intent

For example:

- “Open settings”
- “Where do I download this?”
- “How do I change my password?”

LookDo uses multimodal AI to ground that intent to a visible interface element and highlights the result, with a reason and suggested action.

## Architecture

```mermaid
flowchart TD
    U["User: Screenshot + Intent"] --> F["React + Vite Frontend"]
    F --> P["POST /api/locate"]
    P --> B["FastAPI Backend"]
    B --> G["Gemma 4: Visual-Semantic Grounding"]
    G --> J["Validated Structured JSON: label / type / bounding box / confidence / reason / action"]
    J --> O["React Bounding Box Overlay"]
    G -->|"Transient API / JSON error or timeout"| R["20-second attempt timeout; at most one same-model retry"]
    R -->|"Retry succeeds"| J
    R -->|"Inference still unavailable"| S{"Built-in sample?"}
    S -->|"Yes"| M["Explicitly labeled mock fallback"]
    M --> O
    S -->|"No: uploaded screenshot"| E["Live Gemma inference unavailable — please retry; no mock box"]
```

The backend sends image and instruction together, validates the returned structure, and normalizes the result for rendering. The UI has a 50-second loading deadline. Retries never switch models. Non-retryable API failures go directly to the same sample-only fallback/error decision.

## Why Gemma 4?

Gemma is not used merely to generate text. It receives:

- The screenshot
- The user's natural-language intent

Its role is **visual-semantic grounding**: understanding which visible UI element best matches what the user means and locating it within the screenshot. The frontend only renders the structured result returned by the backend.

The judging/demo model configuration is **`gemma-4-26b-a4b-it`**, selected with `LOOKDO_GEMMA_MODEL` in the launch instructions below. The repository's unchanged code default is `gemma-4-31b-it` if no override is set. LookDo uses Google's hosted API for the open-weight Gemma family; it does not run the model weights locally.

## Structured output

Conceptual result example:

```json
{
  "label": "Settings",
  "element_type": "button",
  "bounding_box": {
    "left": 0.88,
    "top": 0.03,
    "right": 0.96,
    "bottom": 0.08
  },
  "confidence": 0.94,
  "reason": "The Settings button matches the requested action.",
  "suggested_action": "Open Settings"
}
```

Coordinates are normalized from 0 to 1 so overlays remain aligned when screenshots are resized. The existing API uses `element_label` for `label` and `explanation` for `reason`, adds computed box `width`/`height`, and includes a `source` field (`gemma`, `mock`, or the legacy optional `gemini` provider). The result card explicitly identifies live Gemma versus mock/fallback coordinates. Confidence is a model estimate, not a calibrated probability.

## Tech stack

| Area | Technologies / safeguards |
| --- | --- |
| Frontend | React, Vite |
| Backend | Python, FastAPI, Pydantic, Pillow |
| AI | Gemma 4, Google GenAI SDK |
| Reliability | Request timeout, bounded retry, validated structured output, transparent fallback for built-in samples |

## How it works

1. **See** — upload/paste an interface screenshot.
2. **Ask** — describe what you want to do.
3. **Understand** — Gemma 4 combines visual and language context.
4. **Locate** — LookDo highlights the intended element.

## Demo

**Primary demo:** select **Software Portal**, use **“Open settings”**, and click **Locate Element**. Show the highlight and the result-source label.

**Secondary demo:** on the same sample, ask **“Where do I download this?”**.

The second built-in sample, **Settings Console**, remains available with its password-change example. Uploaded real-world screenshots are also supported through upload, drag-and-drop, or Ctrl+V paste. If live inference fails for an upload, LookDo shows a retry message and draws no predefined mock box. Built-in samples alone can use labeled mock fallback.

### Run locally

Prerequisites: Python 3.10+ and Node.js 18+. From the repository root, start the backend in PowerShell:

```powershell
cd backend
python -m pip install -r requirements.txt
# First-time setup only: copy .env.example to .env if .env does not exist.
# Put your own GEMINI_API_KEY in backend/.env. Never commit the key.
$env:LOOKDO_AI_PROVIDER="gemma"
$env:LOOKDO_GEMMA_MODEL="gemma-4-26b-a4b-it"
python -m uvicorn app.main:app --port 8000
```

In a second terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open [LookDo](http://localhost:5173). Dependencies only need installing on first setup or when they change. API documentation is available at [FastAPI docs](http://localhost:8000/docs).

For an intentional offline demonstration of the built-in samples, set `LOOKDO_AI_PROVIDER=mock` before starting the backend. The header shows the configured provider; the result card reports the actual result source.

### Offline validation

These commands do not send Gemma API requests:

```powershell
# From the repository root:
python -m compileall -q backend/app
cd backend
python -m unittest test_demo_reliability
cd ../frontend
npm run build
```

`test_demo_reliability.py` covers both demo commands, same-model retry limits, timeout enforcement, and sample-only mock responses. The other retained tests are manual/live integration checks; do not run them as part of offline validation.

## Current limitations

- Dense interfaces and very small controls can reduce grounding accuracy, especially after the backend resizes images to a maximum 400-pixel edge.
- Model latency and availability can vary; hosted inference requires internet access and quota.
- The MVP identifies and highlights targets but does not automatically click them.
- Mock fallback is explicitly labeled and intended only for built-in demos; its predefined coordinates do not analyze the screenshot.
- Accessibility benefits need broader usability validation.

## Roadmap — FUTURE WORK

These are planned concepts, **not implemented features**:

- **Guide Me** — step-by-step interface navigation
- Voice commands
- MediaPipe rough gaze/head-direction input
- Combine gaze + speech: look toward something and say “open that”
- DOM/OCR-assisted grounding for higher coordinate precision
- Optional browser extension / direct interaction

## Open source

LookDo is released under the [MIT License](LICENSE). The application license does not relicense Gemma model weights or the hosted API; their respective terms apply.

## Security

- `.env` files are ignored by Git. `.env.example` is a configuration template without credentials.
- Keep API keys in the backend environment; never place them in frontend code, test fixtures, or documentation.
- Screenshots are sent to the hosted model provider. Avoid uploading sensitive content.
