from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import base64

async def encrypt_data_for_abha(data_to_encrypt: str, certificate_pem: str) -> str:
    """
    Encrypts data using RSA-OAEP with SHA-1 using a public key.
    The key can be a full PEM string or just the base64-encoded content.
    """
    key_content = certificate_pem.strip()
    if not key_content.startswith("-----BEGIN"):
        # Based on the JS code, it's a public key (SPKI).
        key_content = (
            "-----BEGIN PUBLIC KEY-----\n"
            f"{key_content}\n"
            "-----END PUBLIC KEY-----"
        )

    # Load public key from the PEM string
    public_key = serialization.load_pem_public_key(
        key_content.encode("utf-8"), backend=default_backend()
    )

    # Encrypt data
    encrypted_bytes = public_key.encrypt(
        data_to_encrypt.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

    # Base64 encode the encrypted bytes
    return base64.b64encode(encrypted_bytes).decode("utf-8")
