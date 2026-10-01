import io
import re
import ipaddress
import urllib.parse
import httpx
from typing import Tuple, Dict, Any
import PyPDF2
from docx import Document
from providers.ocr_provider import get_ocr_provider
from providers.stt_provider import get_stt_provider

def is_safe_url(url: str) -> Tuple[bool, str]:
    """Validates URL to protect against SSRF and local network access."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False, "Only HTTP and HTTPS protocols are permitted."
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid hostname."
        
        # Block localhost and private addresses
        if hostname.lower() in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            return False, "Access to localhost/loopback is prohibited."
            
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False, "Access to private/internal networks is prohibited."
        except ValueError:
            # Hostname is a domain name, not an IP literal
            pass
            
        return True, ""
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

async def fetch_url_content(url: str) -> Tuple[str, Dict[str, Any]]:
    """Safely fetches and extracts text from a public web page."""
    is_safe, error_msg = is_safe_url(url)
    if not is_safe:
        raise ValueError(error_msg)
        
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "NTRO-ContentTransformer/1.0"})
        if response.status_code != 200:
            raise ValueError(f"HTTP error {response.status_code} fetching URL.")
            
        html = response.text
        # Clean HTML tags
        clean_text = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r'<style.*?</style>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        metadata = {
            "source_url": url,
            "status_code": response.status_code,
            "words_count": len(clean_text.split()),
            "content_type": response.headers.get("content-type", "text/html")
        }
        return clean_text, metadata

def extract_pdf_content(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        text += f"\n--- Page {idx+1} ---\n" + page_text
        
    metadata = {
        "pages_count": len(reader.pages),
        "words_count": len(text.split()),
        "format": "PDF"
    }
    return text.strip(), metadata

def extract_docx_content(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    # Also extract tables
    table_texts = []
    for table in doc.tables:
        for row in table.rows:
            row_vals = [cell.text.strip() for cell in row.cells]
            table_texts.append(" | ".join(row_vals))
            
    all_text = "\n".join(paragraphs)
    if table_texts:
        all_text += "\n\n[Extracted Tables]:\n" + "\n".join(table_texts)
        
    metadata = {
        "paragraphs_count": len(paragraphs),
        "tables_count": len(doc.tables),
        "words_count": len(all_text.split()),
        "format": "DOCX"
    }
    return all_text.strip(), metadata

def extract_image_content(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    ocr_provider = get_ocr_provider()
    text = ocr_provider.extract_text(file_bytes)
    metadata = {
        "filename": filename,
        "format": "IMAGE_OCR",
        "words_count": len(text.split())
    }
    return text, metadata

def extract_video_content(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    stt_provider = get_stt_provider()
    result = stt_provider.transcribe(file_bytes, filename=filename)
    text = result.get("transcript", "")
    metadata = {
        "filename": filename,
        "format": "VIDEO_ASR",
        "duration_seconds": result.get("duration_seconds", 0),
        "language": result.get("language", "en"),
        "confidence": result.get("confidence", 1.0),
        "timestamps": result.get("timestamps", [])
    }
    return text, metadata
