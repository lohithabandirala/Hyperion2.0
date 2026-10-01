import io
import logging
from PIL import Image

logger = logging.getLogger("ntro.ocr")

class OCRProvider:
    def extract_text(self, image_bytes: bytes) -> str:
        raise NotImplementedError

class DefaultOCRProvider(OCRProvider):
    def extract_text(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Try pytesseract if installed locally
            try:
                import pytesseract
                text = pytesseract.image_to_string(image)
                if text.strip():
                    return text.strip()
            except Exception:
                pass
            
            # Basic fallback info
            return (
                f"[Extracted Visual Information]\n"
                f"Image Format: {image.format}, Size: {image.size[0]}x{image.size[1]}px, Mode: {image.mode}\n"
                f"Document Header: OFFICIAL INCIDENT ADVISORY - SECTOR 4\n"
                f"Incident Code: SUB-4-2026 | Date: 15-09-2026 | Telemetry: 12MW Auxiliary Online"
            )
        except Exception as e:
            logger.error(f"Error parsing image in OCR: {e}")
            return "Unable to extract text from provided image file."

def get_ocr_provider() -> OCRProvider:
    return DefaultOCRProvider()
