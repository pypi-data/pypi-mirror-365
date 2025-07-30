import argparse
import logging
import sys
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from src.auth.azure_auth import AzureAuth
from src.signing.file_signer import FileSigner


def setup_logging(verbose=False):
    """Configure logging"""
    # Set default level to WARNING to reduce noise
    log_level = logging.DEBUG if verbose else logging.WARNING

    # Create a formatter that doesn't include the timestamp for console output
    formatter = logging.Formatter("%(levelname)s - %(message)s")

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add a console handler with the simpler formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def extract_pkcs12_key(pfx_data, password=None):
    """
    Extract private key from PKCS#12 (PFX) formatted data

    Args:
        pfx_data (bytes): The PKCS#12 data
        password (bytes, optional): Password for the PKCS#12 data

    Returns:
        tuple: (certificate_pem, private_key_pem)
    """
    # Try to decode if it's base64 encoded
    try:
        if isinstance(pfx_data, str):
            pfx_bytes = base64.b64decode(pfx_data)
        else:
            pfx_bytes = pfx_data
    except:
        # If not base64, use as is
        pfx_bytes = (
            pfx_data if isinstance(pfx_data, bytes) else pfx_data.encode("utf-8")
        )

    # Load the PKCS#12 data
    if password:
        if isinstance(password, str):
            password = password.encode("utf-8")
        p12 = pkcs12.load_key_and_certificates(pfx_bytes, password, default_backend())
    else:
        # Try with None password first, then with empty string
        try:
            p12 = pkcs12.load_key_and_certificates(pfx_bytes, None, default_backend())
        except Exception:
            p12 = pkcs12.load_key_and_certificates(pfx_bytes, b"", default_backend())

    # Extract the components
    private_key, certificate, ca_certs = p12

    # Convert to PEM
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

    return cert_pem, private_key_pem


def main():
    parser = argparse.ArgumentParser(
        description="Code sign a file using a certificate from Azure Key Vault."
    )
    parser.add_argument("--vault-url", required=True, help="Azure Key Vault URL")
    parser.add_argument(
        "--cert-name", required=True, help="Certificate name in Azure Key Vault"
    )
    parser.add_argument("--file", required=True, help="Path to the file to be signed")
    parser.add_argument(
        "--output", help="Path where to save the signature (default: file.sig)"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify an existing signature"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--pkcs12-password", help="Password for PKCS#12 if required")
    parser.add_argument(
        "--embedded", 
        action="store_true", 
        help="Embed signature directly in the file (required for AppSource)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Initialize authentication to Azure Key Vault - reduced logging
        if args.verbose:
            logger.debug(f"Authenticating to Azure Key Vault: {args.vault_url}")
        azure_auth = AzureAuth(args.vault_url, args.cert_name)

        # Retrieve certificate and private key
        cert_key_pair = azure_auth.get_certificate()
        if not cert_key_pair:
            logger.error("Failed to retrieve certificate from Azure Key Vault")
            sys.exit(1)

        certificate, private_key = cert_key_pair

        # Debug info only if verbose is enabled
        if args.verbose:
            logger.debug(f"Certificate type: {type(certificate)}")
            logger.debug(f"Private key type: {type(private_key)}")

        # Force conversion to bytes if we have a bytearray
        if isinstance(certificate, bytearray):
            certificate = bytes(certificate)
        if isinstance(private_key, bytearray):
            private_key = bytes(private_key)

        # Try to extract PEM-formatted certificate and key if it's in PKCS#12 format
        try:
            if args.verbose:
                logger.debug(
                    "Attempting to extract certificate and key from PKCS#12 format"
                )
            cert_pem, key_pem = extract_pkcs12_key(private_key, args.pkcs12_password)
            certificate = cert_pem
            private_key = key_pem
            if args.verbose:
                logger.debug(
                    "Successfully extracted certificate and key from PKCS#12 format"
                )
        except Exception as e:
            if args.verbose:
                logger.debug(f"PKCS#12 extraction failed: {str(e)}")

            # If the key appears to be base64 encoded, try to decode it - reduced logging
            if isinstance(private_key, (str, bytes)) and not private_key.startswith(
                b"-----BEGIN"
            ):
                try:
                    if args.verbose:
                        logger.debug("Attempting to base64 decode the private key")
                    if isinstance(private_key, str):
                        decoded_key = base64.b64decode(private_key)
                    else:
                        decoded_key = base64.b64decode(private_key)
                    private_key = decoded_key
                except Exception:
                    pass

        # Initialize the file signer with certificate and private key
        if args.verbose:
            logger.debug("Initializing file signer")
        try:
            file_signer = FileSigner(certificate, private_key)
        except Exception as e:
            logger.error(f"Failed to initialize file signer: {str(e)}")
            # Check if key is in PEM format but missing headers
            if isinstance(private_key, bytes) and not private_key.startswith(
                b"-----BEGIN"
            ):
                if args.verbose:
                    logger.debug("Attempting to add PEM headers to private key")
                private_key = (
                    b"-----BEGIN PRIVATE KEY-----\n"
                    + private_key
                    + b"\n-----END PRIVATE KEY-----"
                )
                try:
                    file_signer = FileSigner(certificate, private_key)
                except Exception as e:
                    logger.error(f"Still failed after adding PEM headers: {str(e)}")
                    raise
            else:
                raise

        if args.verify:
            # Verify the file signature - keep user-facing messages
            print(f"Verifying signature for: {args.file}")
            if args.embedded:
                # Verify embedded signature
                if file_signer.verify_embedded_signature(args.file):
                    print(f"✅ Embedded signature verified for {args.file}")
                    sys.exit(0)
                else:
                    print(f"❌ Invalid embedded signature for {args.file}")
                    sys.exit(1)
            else:
                # Verify detached signature
                if file_signer.verify_signature(args.file, args.output):
                    print(f"✅ Signature verified for {args.file}")
                    sys.exit(0)
                else:
                    print(f"❌ Invalid signature for {args.file}")
                    sys.exit(1)
        else:
            # Sign the file - keep user-facing messages
            if args.embedded:
                print(f"Signing file with embedded signature: {args.file}")
                signature_path = file_signer.sign_file_embedded(args.file, args.output)
                if signature_path:
                    print(f"✅ Successfully signed {args.file} with embedded signature")
                    print(f"📄 Signed file saved to {signature_path}")
                    sys.exit(0)
                else:
                    print(f"❌ Failed to sign {args.file} with embedded signature")
                    sys.exit(1)
            else:
                print(f"Signing file: {args.file}")
                signature_path = file_signer.sign_file(args.file, args.output)

                if signature_path:
                    print(f"✅ Successfully signed {args.file}")
                    print(f"📄 Signature saved to {signature_path}")
                    sys.exit(0)
                else:
                    print(f"❌ Failed to sign {args.file}")
                    sys.exit(1)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
