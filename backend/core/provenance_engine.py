import hashlib
import json
import uuid
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Tuple
import io
import qrcode
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger("ntro.provenance")

# In-memory / persistent server-side Ed25519 private key
_PRIVATE_KEY = ed25519.Ed25519PrivateKey.generate()
_PUBLIC_KEY = _PRIVATE_KEY.public_key()

class ProvenanceEngine:
    @staticmethod
    def compute_sha256(data: bytes | str) -> str:
        """Computes deterministic SHA-256 hex digest."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def generate_provenance_id() -> str:
        """Generates canonical NTRO Provenance ID: NTRO-26154-OUT-YYYYMMDD-XXXXXX"""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        rand_str = uuid.uuid4().hex[:6].upper()
        return f"NTRO-26154-OUT-{date_str}-{rand_str}"

    @staticmethod
    def get_public_key_hex() -> str:
        """Returns the public key as hex for client-side / recipient verification."""
        raw_bytes = _PUBLIC_KEY.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return raw_bytes.hex()

    @staticmethod
    def sign_data(data: bytes | str) -> str:
        """Signs data using server-side Ed25519 private key. Returns base64 signature."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        sig_bytes = _PRIVATE_KEY.sign(data)
        return base64.b64encode(sig_bytes).decode("utf-8")

    @staticmethod
    def verify_signature(data: bytes | str, signature_b64: str, public_key_hex: str = None) -> bool:
        """Verifies Ed25519 digital signature."""
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")
            sig_bytes = base64.b64decode(signature_b64)
            
            if public_key_hex:
                pub_bytes = bytes.fromhex(public_key_hex)
                pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            else:
                pub_key = _PUBLIC_KEY

            pub_key.verify(sig_bytes, data)
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False

    @staticmethod
    def build_and_sign_manifest(
        provenance_id: str,
        transformation_id: int,
        output_id: int,
        version: int,
        output_type: str,
        source_hash: str,
        fact_registry_hash: str,
        semantic_model_hash: str,
        artifact_hash: str,
        approval_status: str = "DRAFT",
        model_name: str = "gemini-2.5-flash"
    ) -> Tuple[Dict[str, Any], str]:
        """Creates canonical manifest and computes asymmetric digital signature."""
        manifest = {
            "provenance_id": provenance_id,
            "transformation_id": transformation_id,
            "output_id": output_id,
            "version": version,
            "output_type": output_type,
            "hashes": {
                "source_hash": f"sha256:{source_hash}",
                "fact_registry_hash": f"sha256:{fact_registry_hash}",
                "semantic_model_hash": f"sha256:{semantic_model_hash}",
                "artifact_hash": f"sha256:{artifact_hash}"
            },
            "signing_authority": {
                "issuer": "National Technical Research Organisation (NTRO)",
                "key_id": "NTRO-ED25519-MASTER-01",
                "algorithm": "Ed25519"
            },
            "model_metadata": {
                "provider": "Google / NTRO AI Hub",
                "model_name": model_name
            },
            "approval_status": approval_status,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # Canonical JSON string for signature
        canonical_str = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
        signature = ProvenanceEngine.sign_data(canonical_str)
        manifest["signature"] = signature
        manifest["public_key"] = ProvenanceEngine.get_public_key_hex()
        return manifest, signature

    @staticmethod
    def generate_qr_code(provenance_id: str, base_url: str = "http://localhost:3000") -> io.BytesIO:
        """Generates a QR code linking to the verification portal."""
        verify_url = f"{base_url}/provenance?id={provenance_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
