"""OCR provider abstraction with local preprocessing and graceful fallbacks."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import shutil

from app.models.schemas import OCRResult


@dataclass
class OCRInput:
    """Input payload for OCR providers."""

    filename: str
    content_type: str
    data: bytes


class OCRProvider:
    """Protocol-like base class for OCR providers."""

    name = "base"

    def extract_text(self, ocr_input: OCRInput) -> OCRResult:
        raise NotImplementedError


class TextPassthroughOCRProvider(OCRProvider):
    """Reads text-like uploads directly for deterministic tests and fallbacks."""

    name = "text-passthrough"

    def extract_text(self, ocr_input: OCRInput) -> OCRResult:
        warnings: list[str] = []
        try:
            text = ocr_input.data.decode("utf-8")
            if not text.strip():
                warnings.append("Uploaded file decoded as text but was empty.")
            return OCRResult(
                text=text,
                provider=self.name,
                warnings=warnings,
                preprocessing_steps=["text upload passthrough"],
            )
        except UnicodeDecodeError:
            return OCRResult(
                text="",
                provider=self.name,
                warnings=["The file could not be decoded as UTF-8 text."],
                preprocessing_steps=["text upload passthrough"],
            )


class TesseractOCRProvider(OCRProvider):
    """Optional OCR provider backed by available local image libraries."""

    name = "tesseract"

    def extract_text(self, ocr_input: OCRInput) -> OCRResult:
        try:
            import pytesseract
        except Exception as exc:  # pragma: no cover - depends on optional deps
            return OCRResult(
                text="",
                provider=self.name,
                warnings=[f"Tesseract OCR dependencies are unavailable: {exc}"],
                preprocessing_steps=[],
            )

        pillow_modules = _load_pillow_modules()
        cv2_module, numpy_module = _load_cv2_modules()

        tesseract_path = shutil.which("tesseract")
        if tesseract_path is None:
            return OCRResult(
                text="",
                provider=self.name,
                warnings=[
                    "Local OCR could not run because the Tesseract executable is not installed on this machine."
                ],
                preprocessing_steps=["attempted image OCR"],
            )

        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        preprocessing_steps: list[str] = []

        try:
            if cv2_module is not None and numpy_module is not None:
                processed = _decode_and_preprocess_with_cv2(
                    ocr_input.data,
                    preprocessing_steps,
                    cv2_module,
                    numpy_module,
                    pillow_modules,
                )
            elif pillow_modules is not None:
                Image, _, _ = pillow_modules
                image = Image.open(BytesIO(ocr_input.data)).convert("RGB")
                processed = _preprocess_image_with_pillow(image, preprocessing_steps)
                preprocessing_steps.append("opencv fallback unavailable")
            else:
                return OCRResult(
                    text="",
                    provider=self.name,
                    warnings=[
                        "Tesseract OCR dependencies are unavailable: neither Pillow nor OpenCV image decoding is available."
                    ],
                    preprocessing_steps=[],
                )
            text = pytesseract.image_to_string(processed)
            warnings = [] if text.strip() else ["OCR completed but did not detect readable text."]
            return OCRResult(
                text=text,
                provider=self.name,
                warnings=warnings,
                preprocessing_steps=preprocessing_steps,
            )
        except Exception as exc:  # pragma: no cover - depends on file contents and optional deps
            return OCRResult(
                text="",
                provider=self.name,
                warnings=[f"OCR processing failed: {exc}"],
                preprocessing_steps=preprocessing_steps,
            )


def _preprocess_image_with_cv2(image, steps: list[str], cv2_module, numpy_module):  # type: ignore[no-untyped-def]
    """Apply bounded preprocessing to improve OCR on noisy label images."""

    grayscale = cv2_module.cvtColor(image, cv2_module.COLOR_BGR2GRAY)
    steps.append("grayscale conversion")

    resized = _resize_for_ocr(grayscale, cv2_module)
    if resized.shape != grayscale.shape:
        steps.append("bounded resize")

    denoised = cv2_module.fastNlMeansDenoising(resized)
    steps.append("denoising")

    thresholded = cv2_module.adaptiveThreshold(
        denoised,
        255,
        cv2_module.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2_module.THRESH_BINARY,
        31,
        11,
    )
    steps.append("adaptive thresholding")

    deskewed = _deskew_image(thresholded, cv2_module, numpy_module)
    if deskewed is not thresholded:
        steps.append("light deskew")

    return deskewed


def _preprocess_image_with_pillow(image, steps: list[str]):  # type: ignore[no-untyped-def]
    """Fallback preprocessing when OpenCV is unavailable."""
    _, ImageFilter, ImageOps = _load_pillow_modules()
    if ImageFilter is None or ImageOps is None:
        raise RuntimeError("Pillow preprocessing modules are unavailable")

    grayscale = ImageOps.grayscale(image)
    steps.append("grayscale conversion")

    resized = _resize_pillow_for_ocr(grayscale)
    if resized.size != grayscale.size:
        steps.append("bounded resize")

    sharpened = resized.filter(ImageFilter.SHARPEN)
    steps.append("sharpen")

    thresholded = sharpened.point(lambda pixel: 255 if pixel > 170 else 0)
    steps.append("binary thresholding")
    return thresholded


def _decode_and_preprocess_with_cv2(data: bytes, steps: list[str], cv2_module, numpy_module, pillow_modules):  # type: ignore[no-untyped-def]
    """Decode image bytes with OpenCV and preprocess for OCR."""

    image_bytes = numpy_module.frombuffer(data, dtype=numpy_module.uint8)
    array = cv2_module.imdecode(image_bytes, cv2_module.IMREAD_COLOR)
    if array is None:
        raise RuntimeError("OpenCV could not decode the uploaded image bytes")

    if pillow_modules is not None:
        Image, _, _ = pillow_modules
        rgb_array = cv2_module.cvtColor(array, cv2_module.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_array)
        steps.append("opencv decode")
        return _preprocess_image_with_cv2(
            cv2_module.cvtColor(numpy_module.array(image), cv2_module.COLOR_RGB2BGR),
            steps,
            cv2_module,
            numpy_module,
        )

    steps.append("opencv decode")
    return _preprocess_image_with_cv2(array, steps, cv2_module, numpy_module)


def _load_pillow_modules():
    """Load Pillow modules when available, otherwise return None."""

    try:
        from PIL import Image, ImageFilter, ImageOps

        return Image, ImageFilter, ImageOps
    except Exception:
        return None


def _load_cv2_modules():
    """Load OpenCV and numpy when available, otherwise return a clean fallback signal."""

    try:
        import cv2 as imported_cv2
        import numpy as imported_numpy

        return imported_cv2, imported_numpy
    except Exception:
        return None, None


def _resize_for_ocr(image, cv2_module):  # type: ignore[no-untyped-def]
    height, width = image.shape[:2]
    longest_side = max(height, width)
    if longest_side >= 1800:
        return image
    scale = 1800 / longest_side
    return cv2_module.resize(image, None, fx=scale, fy=scale, interpolation=cv2_module.INTER_CUBIC)


def _resize_pillow_for_ocr(image):  # type: ignore[no-untyped-def]
    width, height = image.size
    longest_side = max(height, width)
    if longest_side >= 1800:
        return image
    scale = 1800 / longest_side
    return image.resize((int(width * scale), int(height * scale)))


def _deskew_image(image, cv2_module, numpy_module):  # type: ignore[no-untyped-def]
    coords = numpy_module.column_stack(numpy_module.where(image < 255))
    if len(coords) < 50:
        return image

    angle = cv2_module.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 1:
        return image

    (height, width) = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2_module.getRotationMatrix2D(center, angle, 1.0)
    return cv2_module.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2_module.INTER_CUBIC,
        borderMode=cv2_module.BORDER_REPLICATE,
    )


def build_ocr_provider(ocr_input: OCRInput) -> OCRProvider:
    """Choose the best available local OCR strategy for the uploaded file."""

    if ocr_input.content_type.startswith("text/") or ocr_input.filename.lower().endswith((".txt", ".json")):
        return TextPassthroughOCRProvider()
    return TesseractOCRProvider()
