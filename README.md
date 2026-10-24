# LookDo

An accessibility-focused multimodal AI assistant that highlights the interface element you want to use.

## Problem
Users may know what they want to do but struggle to identify the right button, icon, or link in an unfamiliar interface.

## Solution
Upload or paste a screenshot and describe your intent. LookDo locates the target, draws a bounding-box highlight, and explains the suggested action. Two built-in sample interfaces make it easy to try.

## Why Gemma 4
Gemma 4 performs **visual-semantic grounding**: connecting visible screenshot content with the user's intent and locating the matching element. It does more than generate text: its coordinates drive the highlight. LookDo uses the open-weight Gemma family through Google's hosted API, defaulting to `gemma-4-31b-it`; this demo does not run model weights locally.

## Architecture
```text
Screenshot + user intent
  → React frontend
  → FastAPI backend
  → Gemma 4 multimodal reasoning
  → structured JSON: label / type / bounding box / confidence / action
  → React bounding-box overlay
```

`POST /api/locate` accepts multipart `image` and `instruction` fields. Its response contains `element_label`, `element_type`, `bounding_box`, `confidence`, `explanation`, `suggested_action`, and `source`. Coordinates are normalized between 0 and 1; the source distinguishes live inference from mock results.

## Tech stack
- React, Vite, CSS, Lucide icons
- Python, FastAPI, Pydantic, Pillow
- Google Gen AI SDK and Gemma 4

## How it works
1. Select a sample, upload an image, or paste a screenshot with Ctrl+V.
2. Enter a natural-language instruction.
3. The backend resizes the screenshot to a maximum 400-pixel edge and sends image and text together to Gemma 4.
4. It parses and validates JSON, including coordinates.
5. React draws the highlight and displays the explanation, action, and result source.

Each Gemma attempt has a 20-second timeout. Transient API, timeout, or JSON errors receive at most one retry on the **same model**; SDK retries are disabled. Failed live inference returns clearly labeled mock coordinates. The UI stops waiting after 50 seconds with a retry message if the backend cannot be reached.

## Demo instructions
Prerequisites: Python 3.10+ and Node.js 18+. Store the key only in ignored `backend/.env`, never in frontend code or Git.

Backend, from the repository root:
```powershell
cd backend
python -m pip install -r requirements.txt
# In backend/.env: GEMINI_API_KEY=<your key>
# Optional: LOOKDO_AI_PROVIDER=gemma
python -m uvicorn app.main:app --port 8000
```

Frontend, in a second terminal from the repository root:
```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Install dependencies only on first setup or when they change.

1. Select **Software Portal**. The recommended command is **Open settings**.
2. Click **Locate Element**; show the Settings highlight and the result source.
3. Enter **Where do I download this?**; show the download button highlight.
4. **Settings Console** remains available with its password-change example.

For an explicit offline demo, set `LOOKDO_AI_PROVIDER=mock` before starting the backend. The header reports the configured provider; the result card identifies each actual result as live or mock/fallback.

## Current limitations
- Hosted inference needs internet, model access, and quota; availability and latency vary.
- Small text and icons lose detail during downscaling. Coordinates may be inaccurate; confidence is not calibrated.
- Mock fallback uses keyword-based predefined demo coordinates and cannot locate elements in arbitrary screenshots.
- LookDo highlights static screenshots and suggests actions; it does not click or control the computer.
- Screenshots are sent to the hosted model provider. Avoid sensitive content.
- Accessibility benefits need broader usability validation.

## Future roadmap
Planned concepts only, not implemented in this MVP:
- **Guide Me** step-by-step mode
- Voice input
- MediaPipe rough gaze/head direction
- Combining gaze with **“look at it and say open that”**
