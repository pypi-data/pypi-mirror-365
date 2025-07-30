import os
import logging
import struct
import time
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


class FileSigner:
    def __init__(self, certificate, private_key):
        """
        Initialize a file signer with certificate and private key

        Args:
            certificate: Certificate object from Azure Key Vault
            private_key: Private key for signing (PEM format)
        """
        self.certificate = certificate
        self.private_key = private_key
        self.logger = logging.getLogger(__name__)

        # Load certificate and private key into usable objects
        self._load_certificate_and_key()

    def _load_certificate_and_key(self):
        """Load certificate and private key into cryptography objects"""
        try:
            # Convert certificate to usable format
            if hasattr(self.certificate, "cer"):
                # If it's an Azure certificate object
                cert_bytes = self.certificate.cer
                # Ensure cert_bytes is bytes, not bytearray
                if isinstance(cert_bytes, bytearray):
                    cert_bytes = bytes(cert_bytes)
                self.cert_obj = x509.load_der_x509_certificate(
                    cert_bytes, default_backend()
                )
                self.cert_pem = self.cert_obj.public_bytes(
                    encoding=serialization.Encoding.PEM
                )
            else:
                # If it's already a PEM string or bytes
                if isinstance(self.certificate, str):
                    self.cert_pem = self.certificate.encode("utf-8")
                elif isinstance(self.certificate, bytearray):
                    self.cert_pem = bytes(self.certificate)
                else:
                    self.cert_pem = self.certificate
                self.cert_obj = x509.load_pem_x509_certificate(
                    self.cert_pem, default_backend()
                )

            # Convert private key to usable format
            if isinstance(self.private_key, str):
                private_key_bytes = self.private_key.encode("utf-8")
            elif isinstance(self.private_key, bytearray):
                private_key_bytes = bytes(self.private_key)
            else:
                private_key_bytes = self.private_key

            self.key_obj = serialization.load_pem_private_key(
                private_key_bytes, password=None, backend=default_backend()
            )

            self.logger.debug("Successfully loaded certificate and private key")
        except Exception as e:
            self.logger.error(
                f"Failed to load certificate and/or private key: {str(e)}"
            )
            raise

    def sign_file(self, file_path, output_path=None):
        """
        Sign a file using the certificate and private key

        Args:
            file_path (str): Path to the file to sign
            output_path (str, optional): Path where to save the signature
                                         If None, creates a .sig file next to the original

        Returns:
            str: Path to the signature file or None if signing failed
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        try:
            # Determine output path for signature
            if not output_path:
                output_path = f"{file_path}.sig"

            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()

            # Create hash of the file
            file_hash = hashes.Hash(hashes.SHA256(), default_backend())
            file_hash.update(file_content)
            digest = file_hash.finalize()

            # Sign the hash
            signature = self.key_obj.sign(digest, padding.PKCS1v15(), hashes.SHA256())

            # Save signature to file
            with open(output_path, "wb") as f:
                f.write(signature)

            self.logger.debug(f"Successfully signed file: {file_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"Failed to sign file {file_path}: {str(e)}")
            return None

    def sign_file_embedded(self, file_path, output_path=None):
        """
        Sign a file by embedding the signature directly into the file
        This is required for AppSource submissions

        Args:
            file_path (str): Path to the file to sign
            output_path (str, optional): Path where to save the signed file
                                         If None, overwrites the original file

        Returns:
            str: Path to the signed file or None if signing failed
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        try:
            # Determine output path
            if not output_path:
                output_path = file_path

            # Read original file content
            with open(file_path, "rb") as f:
                original_content = f.read()

            # Create signature data structure
            signature_data = self._create_embedded_signature(original_content)

            # Write the signed file
            with open(output_path, "wb") as f:
                f.write(original_content)
                f.write(signature_data)

            self.logger.debug(f"Successfully embedded signature in file: {file_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to embed signature in file {file_path}: {str(e)}")
            return None

    def _create_embedded_signature(self, file_content):
        """
        Create an embedded signature data structure
        This creates a simplified signature block that can be embedded in the file
        """
        # Create hash of the original file content
        file_hash = hashes.Hash(hashes.SHA256(), default_backend())
        file_hash.update(file_content)
        digest = file_hash.finalize()

        # Sign the hash
        signature = self.key_obj.sign(digest, padding.PKCS1v15(), hashes.SHA256())

        # Get certificate in DER format
        cert_der = self.cert_obj.public_bytes(serialization.Encoding.DER)

        # Create signature block structure
        # This is a simplified structure - for full Authenticode, you'd need more complex ASN.1
        signature_block = b"SIGNATURE_BLOCK_START\n"
        signature_block += b"CERTIFICATE_LENGTH: " + str(len(cert_der)).encode() + b"\n"
        signature_block += cert_der
        signature_block += b"\nSIGNATURE_LENGTH: " + str(len(signature)).encode() + b"\n"
        signature_block += signature
        signature_block += b"\nTIMESTAMP: " + str(int(time.time())).encode() + b"\n"
        signature_block += b"SIGNATURE_BLOCK_END\n"

        return signature_block

    def verify_embedded_signature(self, file_path):
        """
        Verify an embedded signature in a file

        Args:
            file_path (str): Path to the file to verify

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # Find signature block
            start_marker = b"SIGNATURE_BLOCK_START\n"
            end_marker = b"SIGNATURE_BLOCK_END\n"
            
            start_pos = content.find(start_marker)
            end_pos = content.find(end_marker)
            
            if start_pos == -1 or end_pos == -1:
                self.logger.debug("No embedded signature found")
                return False

            # Extract original content (before signature block)
            original_content = content[:start_pos]
            
            # Extract signature block
            signature_block = content[start_pos:end_pos + len(end_marker)]
            
            # Parse signature block
            cert_data, signature_data = self._parse_embedded_signature(signature_block)
            
            if not cert_data or not signature_data:
                self.logger.debug("Failed to parse embedded signature")
                return False

            # Verify the signature
            return self._verify_signature_data(original_content, cert_data, signature_data)

        except Exception as e:
            self.logger.debug(f"Embedded signature verification failed: {str(e)}")
            return False

    def _parse_embedded_signature(self, signature_block):
        """Parse the embedded signature block to extract certificate and signature"""
        try:
            # Find the certificate and signature lengths from text parts
            cert_length_marker = b"CERTIFICATE_LENGTH: "
            sig_length_marker = b"SIGNATURE_LENGTH: "
            
            cert_length_start = signature_block.find(cert_length_marker)
            if cert_length_start == -1:
                return None, None
            
            cert_length_start += len(cert_length_marker)
            cert_length_end = signature_block.find(b"\n", cert_length_start)
            cert_length = int(signature_block[cert_length_start:cert_length_end])
            
            sig_length_start = signature_block.find(sig_length_marker)
            if sig_length_start == -1:
                return None, None
            
            sig_length_start += len(sig_length_marker)
            sig_length_end = signature_block.find(b"\n", sig_length_start)
            signature_length = int(signature_block[sig_length_start:sig_length_end])
            
            # Extract certificate data (starts right after the certificate length line)
            cert_data_start = cert_length_end + 1  # +1 to skip the newline
            cert_data = signature_block[cert_data_start:cert_data_start + cert_length]
            
            # Extract signature data (starts right after the signature length line)
            sig_data_start = sig_length_end + 1  # +1 to skip the newline
            signature_data = signature_block[sig_data_start:sig_data_start + signature_length]
            
            return cert_data, signature_data
            
        except Exception as e:
            self.logger.debug(f"Failed to parse signature block: {str(e)}")
            return None, None

    def _verify_signature_data(self, content, cert_data, signature_data):
        """Verify signature data against content"""
        try:
            # Load certificate from DER data
            cert = x509.load_der_x509_certificate(cert_data, default_backend())
            
            # Create hash of content
            file_hash = hashes.Hash(hashes.SHA256(), default_backend())
            file_hash.update(content)
            digest = file_hash.finalize()
            
            # Get public key and verify
            public_key = cert.public_key()
            public_key.verify(signature_data, digest, padding.PKCS1v15(), hashes.SHA256())
            
            self.logger.debug("Embedded signature verification successful")
            return True
            
        except Exception as e:
            self.logger.debug(f"Signature verification failed: {str(e)}")
            return False

    def verify_signature(self, file_path, signature_path=None):
        """
        Verify file signature using the certificate

        Args:
            file_path (str): Path to the file to verify
            signature_path (str, optional): Path to the signature file
                                            If None, assumes file_path + '.sig'

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False

        # Determine signature path
        if not signature_path:
            signature_path = f"{file_path}.sig"

        if not os.path.exists(signature_path):
            self.logger.error(f"Signature file not found: {signature_path}")
            return False

        try:
            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()

            # Create hash of the file
            file_hash = hashes.Hash(hashes.SHA256(), default_backend())
            file_hash.update(file_content)
            digest = file_hash.finalize()

            # Read signature
            with open(signature_path, "rb") as f:
                signature = f.read()

            # Get public key from certificate
            public_key = self.cert_obj.public_key()

            # Verify signature
            public_key.verify(signature, digest, padding.PKCS1v15(), hashes.SHA256())

            self.logger.debug(f"Signature is valid for file: {file_path}")
            return True

        except Exception as e:
            self.logger.debug(f"Signature verification failed: {str(e)}")
            return False
