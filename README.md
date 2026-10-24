# LookDo 🔍✨
> Helping users navigate confusing computer interfaces with Multimodal AI.

LookDo is an accessibility-focused tool that takes a screenshot of any user interface along with a natural-language instruction (such as *"open settings"*, *"where do I download this?"*, or *"click the second blue button"*), uses multimodal AI to locate the requested element, and renders an interactive, highlighted bounding box over the interface with a clear explanation and suggested action.

---

## 🚀 Architecture

```
lookdo/
  backend/
    app/
      main.py               # FastAPI entrypoint with CORS
      routes/
        locate.py           # /api/locate endpoint accepting multipart form
      schemas/
        detection.py        # Pydantic schemas (DetectionResult, BoundingBox)
      services/
        ai_service.py       # Abstract BaseAIService + MockAIService + Gemini adapter ready
    requirements.txt
  frontend/
    src/                    # React + Vite application
      components/           # UI elements (ScreenshotViewer, BoundingBoxOverlay, ExplanationCard)
      index.css             # Premium custom styling & accessible design tokens
    package.json
    vite.config.js
  README.md
  .gitignore
```

---

## ⚡ Quick Start

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend API docs will be available at: `http://localhost:8000/docs`

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Frontend will be running at: `http://localhost:5173`

---

## 🎯 Features in this MVP
- **Screenshot Upload & Drag-and-Drop / Clipboard Paste**: Easily upload your own screenshot, paste directly from clipboard, or pick a sample UI screenshot.
- **Natural Language Intent Input**: Type what you are trying to find or click.
- **Normalized Coordinate System**: Uses 0.0 to 1.0 coordinates (`top`, `left`, `bottom`, `right`, `width`, `height`) so responsive resizing never displaces overlays.
- **Visually Rich Overlay**: Glowing highlight box with animated beacon, badge indicator, and clear element details.
- **Detailed Explanation**: Structured card showing element label, element type, confidence score, suggested action, and natural-language explanation.
- **Provider Abstraction**: Easily switch from Mock AI to Gemini / Gemma API.
