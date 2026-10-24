from pydantic import BaseModel, Field, model_validator
from typing import Optional


class BoundingBox(BaseModel):
    """
    Normalized coordinates between 0.0 and 1.0.
    top: normalized y-min (0.0 = top edge, 1.0 = bottom edge)
    left: normalized x-min (0.0 = left edge, 1.0 = right edge)
    bottom: normalized y-max
    right: normalized x-max
    width: normalized width (right - left)
    height: normalized height (bottom - top)
    """
    top: float = Field(..., ge=0.0, le=1.0, description="Normalized Y minimum coordinate [0, 1]")
    left: float = Field(..., ge=0.0, le=1.0, description="Normalized X minimum coordinate [0, 1]")
    bottom: float = Field(..., ge=0.0, le=1.0, description="Normalized Y maximum coordinate [0, 1]")
    right: float = Field(..., ge=0.0, le=1.0, description="Normalized X maximum coordinate [0, 1]")
    width: Optional[float] = Field(None, ge=0.0, le=1.0, description="Normalized width")
    height: Optional[float] = Field(None, ge=0.0, le=1.0, description="Normalized height")

    @model_validator(mode="after")
    def compute_dimensions(self):
        # Automatically calculate width and height if not explicitly provided
        if self.width is None:
            self.width = round(max(0.0, self.right - self.left), 4)
        if self.height is None:
            self.height = round(max(0.0, self.bottom - self.top), 4)
        return self


class DetectionResult(BaseModel):
    """
    Structured outcome returned by LookDo AI service.
    """
    element_label: str = Field(..., description="Human-readable label of the identified element")
    element_type: str = Field(..., description="Type of the UI element (e.g. button, input, link, icon, menu)")
    bounding_box: BoundingBox = Field(..., description="Normalized coordinates of the bounding box")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    explanation: str = Field(..., description="Short, clear explanation of why this element was selected")
    suggested_action: str = Field(..., description="Recommended user action (e.g., Click, Type text, Hover)")
