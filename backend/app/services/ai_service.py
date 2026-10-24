import io
import json
import logging
import os
import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.schemas.detection import BoundingBox, DetectionResult

logger = logging.getLogger("lookdo.ai_service")

# Maximum image dimension (px) that Gemma 4 accepts without a 500 error
_GEMMA_MAX_DIM = 400


class BaseAIService(ABC):
    """
    Abstract Base Class for Multimodal UI Detection.
    Subclasses can implement Mock, Gemini, Gemma, or other multimodal providers.
    """

    async def guide_element(self, image_bytes: bytes, instruction: str) -> DetectionResult:
        # Reuse the same model, validation, retries and fallback path as Locate.
        guide_instruction = (
            f"Guide Me task: {instruction}\n"
            "Identify only the NEXT visible action on this current screenshot toward the task. "
            "Target a control visible now, not a control on a future screen. "
            "Return exactly one target using the existing JSON schema. "
            "suggested_action must be one short instruction without a step number. "
            "Do not provide multiple steps or assume any previous conversation."
        )
        result = await self.locate_element(image_bytes, guide_instruction)
        if result.source == "mock":
            # Mock keyword matching must see the task, not the guidance prompt.
            was_fallback = result.explanation.startswith("[Mock fallback:")
            result = await MockAIService().locate_element(image_bytes, instruction)
            if was_fallback:
                result.explanation = "[Mock fallback: live inference unavailable] " + result.explanation
        result.next_step = f"Step 1: {result.suggested_action}"
        return result

    @abstractmethod
    async def locate_element(self, image_bytes: bytes, instruction: str) -> DetectionResult:
        """
        Analyze the screenshot image and natural language instruction,
        and return the structured detection result.
        """
        pass


class MockAIService(BaseAIService):
    """
    Mock AI Service for testing and verifying the complete UI flow
    before connecting live models. Returns smart, context-sensitive
    normalized coordinates based on keywords in the instruction.
    """

    async def locate_element(self, image_bytes: bytes, instruction: str) -> DetectionResult:
        text = instruction.strip().lower()

        # Match common user intents to realistic coordinates
        if any(k in text for k in ["setting", "gear", "config", "preferences"]):
            return DetectionResult(
                element_label="Settings Gear Icon",
                element_type="icon_button",
                bounding_box=BoundingBox(top=0.035, left=0.88, bottom=0.085, right=0.965),
                confidence=0.96,
                explanation="Located the gear icon in the top-right navigation area, which opens interface settings.",
                suggested_action="Click the settings gear icon in the top right header",
            )

        if any(k in text for k in ["download", "install", "get", "save"]):
            return DetectionResult(
                element_label="Download Installer Button",
                element_type="button",
                bounding_box=BoundingBox(top=0.46, left=0.35, bottom=0.55, right=0.65),
                confidence=0.94,
                explanation="Found the primary call-to-action button centered on the screen for downloading the installer.",
                suggested_action="Click the 'Download' button to start your download",
            )

        if any(k in text for k in ["password", "security", "login", "auth"]):
            return DetectionResult(
                element_label="Change Password Link",
                element_type="link",
                bounding_box=BoundingBox(top=0.60, left=0.18, bottom=0.66, right=0.42),
                confidence=0.92,
                explanation="Identified the 'Change Password' security hyperlink in the account options section.",
                suggested_action="Click to navigate to the password modification form",
            )

        if any(k in text for k in ["second", "blue", "next button"]):
            return DetectionResult(
                element_label="Second Blue Action Button",
                element_type="button",
                bounding_box=BoundingBox(top=0.42, left=0.52, bottom=0.50, right=0.74),
                confidence=0.89,
                explanation="Identified the second prominent blue action button in the main content container.",
                suggested_action="Click the highlighted blue action button",
            )

        if any(k in text for k in ["right", "side", "sidebar", "panel"]):
            return DetectionResult(
                element_label="Side Option Control",
                element_type="menu_item",
                bounding_box=BoundingBox(top=0.28, left=0.72, bottom=0.36, right=0.94),
                confidence=0.88,
                explanation="Identified the requested control option located on the right side of the interface.",
                suggested_action="Click to select this side panel option",
            )

        if any(k in text for k in ["search", "find", "lookup"]):
            return DetectionResult(
                element_label="Search Input Field",
                element_type="input",
                bounding_box=BoundingBox(top=0.04, left=0.25, bottom=0.09, right=0.70),
                confidence=0.93,
                explanation="Found the search bar in the top navigation area.",
                suggested_action="Click to focus the search box and type your query",
            )

        # Fallback default mock detection
        clean_prompt = instruction.strip() or "target element"
        return DetectionResult(
            element_label=f"Target: {clean_prompt[:30]}",
            element_type="interactive_element",
            bounding_box=BoundingBox(top=0.30, left=0.28, bottom=0.42, right=0.72),
            confidence=0.86,
            explanation=f"Analyzed screenshot and identified this element as the best match for '{clean_prompt}'.",
            suggested_action="Click or interact with the highlighted element",
        )


def _downscale_image_for_gemma(image_bytes: bytes, max_dim: int = _GEMMA_MAX_DIM) -> bytes:
    """
    Downscale image to max_dim on the longest edge (JPEG) if larger.
    Gemma 4 returns HTTP 500 for large PNG payloads, but works reliably
    at 400px wide JPEG. Returns original bytes if already small enough.
    """
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if max(img.size) > max_dim:
            scale = max_dim / max(img.size)
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue()
    except Exception as e:
        logger.warning(f"Image downscale failed, using original bytes: {e}")
        return image_bytes


def _extract_json_from_text(text: str) -> dict:
    """
    Extract a JSON object from model output, stripping markdown code fences
    and other surrounding text if present.
    """
    if not text or not text.strip():
        raise ValueError("Empty response received from Gemma model.")

    # raw_decode ignores trailing prose/fences and respects braces inside strings.
    start = text.find("{")
    if start < 0:
        raise ValueError("Gemma response contains no JSON object.")
    result, _ = json.JSONDecoder().raw_decode(text[start:])
    return result



class GemmaAIService(BaseAIService):
    """
    Adapter for Google Gemma 4 Multimodal API using official `google-genai` SDK.
    Uses the configured Gemma model without switching models.
    Images are downscaled to 400px max to avoid API 500 errors on large payloads.

    Attempts the same model at most twice, then returns an explicit mock fallback.
    """

    PRIMARY_MODEL = "gemma-4-31b-it"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("LOOKDO_GEMMA_MODEL", self.PRIMARY_MODEL)
        self._client = None

        if self.api_key:
            try:
                from google import genai
                from google.genai import types
                self._client = genai.Client(
                    api_key=self.api_key,
                    http_options=types.HttpOptions(
                        timeout=20000, retry_options=types.HttpRetryOptions(attempts=1)
                    ),
                )
                logger.info(f"GemmaAIService initialised with model={self.model}")
            except Exception as e:
                logger.error("Failed to initialize Google GenAI client: %s", type(e).__name__)

    def _build_prompt(self, instruction: str) -> str:
        return (
            f"You are LookDo, an AI user interface accessibility and navigation assistant.\n"
            f"The user wants to locate this element in the interface: \"{instruction}\".\n\n"
            f"Analyze the attached screenshot and locate the exact button, link, icon, menu item, or input field.\n"
            f"Return strict JSON only matching this schema:\n"
            f"{{\n"
            f"  \"element_label\": \"<concise descriptive label of the target element>\",\n"
            f"  \"element_type\": \"<button | link | input | icon_button | menu_item | dropdown | interactive_element>\",\n"
            f"  \"bounding_box\": {{\n"
            f"    \"top\": <normalized float ymin between 0.0 and 1.0>,\n"
            f"    \"left\": <normalized float xmin between 0.0 and 1.0>,\n"
            f"    \"bottom\": <normalized float ymax between 0.0 and 1.0>,\n"
            f"    \"right\": <normalized float xmax between 0.0 and 1.0>\n"
            f"  }},\n"
            f"  \"confidence\": <float between 0.0 and 1.0>,\n"
            f"  \"explanation\": \"<concise reason explaining why this element matches the user's intent>\",\n"
            f"  \"suggested_action\": \"<specific interaction advice>\"\n"
            f"}}\n"
            f"CRITICAL RULES:\n"
            f"1. Coordinates must be normalized floats between 0.0 and 1.0.\n"
            f"2. Return only valid JSON. Do not wrap in conversational text or markdown fences."
        )

    async def locate_element(self, image_bytes: bytes, instruction: str) -> DetectionResult:
        async def fallback(reason: str) -> DetectionResult:
            result = await MockAIService().locate_element(image_bytes, instruction)
            result.explanation = f"[Mock fallback: {reason}] " + result.explanation
            return result

        if not self._client or not self.api_key:
            return await fallback("Gemma client unavailable")

        from google.genai import types
        image_part = types.Part.from_bytes(
            data=_downscale_image_for_gemma(image_bytes), mime_type="image/jpeg"
        )
        prompt = self._build_prompt(instruction)
        for attempt in range(2):
            try:
                response = await asyncio.wait_for(
                    self._client.aio.models.generate_content(
                        model=self.model, contents=[image_part, prompt]
                    ),
                    timeout=20,
                )
                result = DetectionResult.model_validate(_extract_json_from_text(response.text))
                # Set provenance here, never trust a model-provided source field.
                result.source = "gemma"
                return result
            except Exception as error:
                # Avoid logging model text, validation payloads, or API credentials.
                logger.warning("Gemma attempt %s failed (%s)", attempt + 1, type(error).__name__)
                code = getattr(error, "code", None)
                transient = (
                    isinstance(error, (ValueError, TimeoutError, ConnectionError))
                    or code in (408, 429, 500, 502, 503, 504)
                    or type(error).__name__ in ("ConnectError", "ReadTimeout", "ConnectTimeout", "RemoteProtocolError")
                )
                if attempt == 0 and transient:
                    prompt += "\nReturn valid JSON only, no markdown or explanation outside JSON."
                    continue
                return await fallback("Gemma timed out or returned an unusable response")


class GeminiAIService(BaseAIService):
    """
    Adapter for Google Gemini Multimodal API using official `google-genai` SDK.
    Supports Gemini 2.5 Flash and other Gemini endpoints with structured output.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("LOOKDO_GEMINI_MODEL", model)
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error("Failed to initialize Google GenAI client: %s", type(e).__name__)

    async def locate_element(self, image_bytes: bytes, instruction: str) -> DetectionResult:
        if not self._client or not self.api_key:
            logger.info("GEMINI_API_KEY not configured. Using MockAIService.")
            mock = MockAIService()
            return await mock.locate_element(image_bytes, instruction)

        try:
            from google.genai import types

            image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            prompt = (
                f"You are LookDo, an AI user interface accessibility and navigation assistant.\n"
                f"The user wants to locate this element in the interface: \"{instruction}\".\n\n"
                f"Analyze the attached screenshot and locate the exact button, link, icon, menu item, or input field.\n"
                f"Return a structured JSON with:\n"
                f"- element_label: concise descriptive label of the target element\n"
                f"- element_type: button, link, input, icon_button, menu_item, dropdown, or interactive_element\n"
                f"- bounding_box: normalized coordinates between 0.0 and 1.0 (top: ymin, left: xmin, bottom: ymax, right: xmax)\n"
                f"- confidence: float between 0.0 and 1.0\n"
                f"- explanation: concise reason explaining why this element matches the user's intent\n"
                f"- suggested_action: specific interaction advice (e.g. 'Click the button')\n\n"
                f"CRITICAL: Bounding box coordinates must be normalized floats strictly between 0.0 and 1.0."
            )

            response = self._client.models.generate_content(
                model=self.model,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DetectionResult,
                    temperature=0.1,
                ),
            )

            if response.text:
                result_data = json.loads(response.text)
                result = DetectionResult.model_validate(result_data)
                result.source = "gemini"
                return result
            else:
                raise ValueError("Empty response received from Gemini model.")

        except Exception as e:
            logger.warning(f"Gemini API call encountered an error: {e}. Falling back to MockAIService.")
            mock = MockAIService()
            result = await mock.locate_element(image_bytes, instruction)
            result.explanation = f"[Live Gemini fallback: {str(e)[:50]}] " + result.explanation
            return result


def get_ai_service() -> BaseAIService:
    """
    Factory method to retrieve the active AI Service provider.
    Priority order:
      LOOKDO_AI_PROVIDER=gemma  -> GemmaAIService (Gemma 4)
      LOOKDO_AI_PROVIDER=gemini -> GeminiAIService (Gemini 2.5 Flash)
      LOOKDO_AI_PROVIDER=auto   -> GemmaAIService if GEMINI_API_KEY present, else MockAIService
      LOOKDO_AI_PROVIDER=mock   -> MockAIService
    """
    provider = os.getenv("LOOKDO_AI_PROVIDER", "auto").lower()
    gemini_key = os.getenv("GEMINI_API_KEY")

    if provider == "gemma" or (provider == "auto" and gemini_key):
        return GemmaAIService()
    if provider == "gemini":
        return GeminiAIService()
    return MockAIService()
