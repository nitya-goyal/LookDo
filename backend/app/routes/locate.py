from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from typing import Literal
from app.schemas.detection import DetectionResult
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/api", tags=["LookDo Locate"])


@router.post("/locate", response_model=DetectionResult)
async def locate_element(
    instruction: str = Form(..., description="Natural language intent/instruction from the user"),
    image: UploadFile = File(..., description="Screenshot image file"),
    sample_id: str = Form("", description="Built-in sample identifier; empty for uploads"),
    mode: Literal["locate", "guide"] = Form("locate"),
):
    """
    Locates the most likely UI element described by the user's instruction in the provided screenshot.
    Returns normalized bounding box, element type, label, confidence, explanation, and suggested action.
    """
    if not instruction.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instruction text cannot be empty.",
        )

    # Read image bytes
    try:
        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image file is empty.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read image file: {str(e)}",
        )

    # Invoke AI Service
    ai_service = get_ai_service()
    try:
        if mode == "guide":
            result = await ai_service.guide_element(image_bytes=image_bytes, instruction=instruction)
        else:
            result = await ai_service.locate_element(image_bytes=image_bytes, instruction=instruction)
        if result.source == "mock" and sample_id not in ("software-portal", "account-settings"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Live Gemma inference unavailable — please retry",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing interface element: {str(e)}",
        )
