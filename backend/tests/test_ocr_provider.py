from pathlib import Path

from app.services.ocr import OCRInput, TesseractOCRProvider


def test_tesseract_provider_falls_back_when_cv2_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("app.services.ocr._load_cv2_modules", lambda: (None, None))

    provider = TesseractOCRProvider()
    fixture_bytes = Path("backend/tests/fixtures/labels/clean-readable-label.png").read_bytes()
    result = provider.extract_text(
        OCRInput(
            filename="clean-readable-label.png",
            content_type="image/png",
            data=fixture_bytes,
        )
    )

    assert result.provider == "tesseract"
    assert "Tesseract OCR dependencies are unavailable" not in " ".join(result.warnings)
    assert result.preprocessing_steps


def test_tesseract_provider_falls_back_when_pillow_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("app.services.ocr._load_pillow_modules", lambda: None)

    provider = TesseractOCRProvider()
    fixture_bytes = Path("backend/tests/fixtures/labels/clean-readable-label.png").read_bytes()
    result = provider.extract_text(
        OCRInput(
            filename="clean-readable-label.png",
            content_type="image/png",
            data=fixture_bytes,
        )
    )

    assert result.provider == "tesseract"
    assert "Tesseract OCR dependencies are unavailable" not in " ".join(result.warnings)
    assert result.preprocessing_steps
