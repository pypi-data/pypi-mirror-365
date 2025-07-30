import logging
import os
from typing import Any, Dict
import json
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
from jose import jwe, jwk
from jose.constants import ALGORITHMS
load_dotenv()

class AiUtilities:
    """
    A utility class for AI service specific operations like encryption/decryption.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def load_public_key_from_x509_certificate(self, certificate_pem: str) -> dict:
        """
        Loads an RSA public key from a PEM-encoded X.509 certificate and returns it as a JWK.
        """
        try:
            cert = x509.load_pem_x509_certificate(
                certificate_pem.encode("utf-8"), default_backend()
            )
            public_key = cert.public_key()

            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("The certificate does not contain an RSA public key.")

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            jwk_object = jwk.construct(
                public_pem.decode("utf-8"),  # public_pem is bytes, decode to string
                algorithm=ALGORITHMS.RSA_OAEP_256,  # Specify the algorithm context
            )
            jwk_dict = jwk_object.to_dict()
            return jwk_dict
        except Exception as e:
            self.logger.error(
                f"Error loading public key from certificate: {e}", exc_info=True
            )
            raise RuntimeError(
                f"Failed to load public key from certificate: {e}"
            ) from e

    async def encryption(self, payload: Dict[str, Any]) -> str:
        """
        Encrypts a payload dictionary using JWE with an RSA public key.
        """
        try:

            # Load the public key as a JWK from the certificate
            certificate_pem = os.getenv("ENCRYPTION_PUBLIC_KEY")
            public_jwk = await self.load_public_key_from_x509_certificate(
                certificate_pem
            )

            payload_bytes = json.dumps(payload).encode("utf-8")

            encrypted_payload = jwe.encrypt(
                plaintext=payload_bytes,
                key=public_jwk,  # Use the JWK dictionary
                algorithm=ALGORITHMS.RSA_OAEP_256,
                encryption=ALGORITHMS.A256GCM,
                # 'zip', 'cty', 'kid' could be passed here if needed and supported
            )
            self.logger.debug("Encryption successful.")
            return encrypted_payload.decode("utf-8")

        except Exception as error:
            self.logger.error(f"Failed to encrypt data: {error}", exc_info=True)
            raise RuntimeError(f"Failed to encrypt data: {error}") from error
