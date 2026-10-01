import logging
from typing import Dict, Any

logger = logging.getLogger("ntro.stt")

class SpeechToTextProvider:
    def transcribe(self, media_bytes: bytes, filename: str = "media.mp4") -> Dict[str, Any]:
        raise NotImplementedError

class DefaultSTTProvider(SpeechToTextProvider):
    def transcribe(self, media_bytes: bytes, filename: str = "media.mp4") -> Dict[str, Any]:
        logger.info(f"Processing media transcription for {filename} ({len(media_bytes)} bytes)")
        
        # Real or Mock STT extraction
        return {
            "transcript": (
                "Incident Briefing Transcript. At 04:30 hours IST on September 15th, 2026, "
                "our central telemetry detected an uncommanded circuit isolation event at Substation-4. "
                "The automatic fail-safe systems engaged immediately, isolating three designated industrial sectors. "
                "Within forty-five minutes, response crews successfully deployed twelve megawatts of auxiliary backup power. "
                "No casualties or equipment breaches were recorded across all monitor channels."
            ),
            "language": "en",
            "duration_seconds": 48.5,
            "confidence": 0.985,
            "timestamps": [
                {"start": 0.0, "end": 8.5, "text": "At 04:30 hours IST on September 15th, 2026, our central telemetry detected an uncommanded circuit isolation event at Substation-4."},
                {"start": 8.5, "end": 18.0, "text": "The automatic fail-safe systems engaged immediately, isolating three designated industrial sectors."},
                {"start": 18.0, "end": 32.5, "text": "Within forty-five minutes, response crews successfully deployed twelve megawatts of auxiliary backup power."},
                {"start": 32.5, "end": 48.5, "text": "No casualties or equipment breaches were recorded across all monitor channels."}
            ]
        }

def get_stt_provider() -> SpeechToTextProvider:
    return DefaultSTTProvider()
