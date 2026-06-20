"""OCR provider abstraction with a local-first fallback.

The prototype prefers local processing. If optional OCR dependencies are
available, image files can be processed with Tesseract. When those
dependencies are absent, text-based fixtures still work so the rest of
the application remains testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from app.models.schemas import OCRResult


@dataclass
class OCRInput:
    filename: str
    content_type: str
    data: bytes


class OCRProvider:
    """Protocol-like base class for OCR providers."""

    name = "base"

    def extract_text(self, ocr_input: OCRInput) -> OCRResult:
        raise NotImplementedError


class TextPassthroughOCRProvider(OCRProvider):
    """Reads text-like uploads directly.

    This supports deterministic tests and gives the prototype a graceful
    fallback when image OCR tooling is not installed yet.
    """

    name = "text-passthrough"

    def extract_text(self, ocr_input: OCRInput) -> OCRResult:
        warnings: list[str] = []
        try:
            text = ocr_input.data.decode("utf-8")
            if not text.strip():
                warnings.append("Uploaded file decoded as text but was empty.")
            return OCRResult(text=text, provider=self.name, warnings=warnings)
        except UnicodeDecodeError:
            return OCRResult(
                text="",
                provider=self.name,
                warnings=["The file could not be decoded as UTF-8 text."],
            )


class TesseractOCRProvider(OCRProvider):
    """Optional OCR provider backed by Pillow and pytesseract."""

    name = "tesseract"

    def extract_text(self, ocr_input: OCRInput) -> OCRResult:
        try:
            from PIL import Image, ImageOps
            import pytesseract
        except Exception as exc:  # pragma: no cover - depends on optional deps
            return OCRResult(
                text="",
                provider=self.name,
                warnings=[f"Tesseract OCR dependencies are unavailable: {exc}"],
            )

        try:
            image = Image.open(BytesIO(ocr_input.data))
            grayscale = ImageOps.grayscale(image)
            text = pytesseract.image_to_string(grayscale)
            warnings = [] if text.strip() else ["OCR completed but did not detect readable text."]
            return OCRResult(text=text, provider=self.name, warnings=warnings)
        except Exception as exc:  # pragma: no cover - depends on file contents and optional deps
            return OCRResult(text="", provider=self.name, warnings=[f"OCR processing failed: {exc}"])


def build_ocr_provider(ocr_input: OCRInput) -> OCRProvider:
    """Choose the best available local OCR strategy for the uploaded file."""
    if ocr_input.content_type.startswith("text/") or ocr_input.filename.lower().endswith((".txt", ".json")):
        return TextPassthroughOCRProvider()
    return TesseractOCRProvider()
