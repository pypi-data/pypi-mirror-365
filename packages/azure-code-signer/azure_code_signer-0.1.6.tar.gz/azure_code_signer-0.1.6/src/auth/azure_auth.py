from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient
from azure.keyvault.secrets import SecretClient
import logging


class AzureAuth:
    def __init__(self, key_vault_url, certificate_name=None, credential=None):
        """
        Initialize authentication to Azure Key Vault

        Args:
            key_vault_url (str): URL of the Azure Key Vault
            certificate_name (str, optional): Name of certificate in Key Vault
            credential: Azure credential object (if None, DefaultAzureCredential is used)
        """
        self.key_vault_url = key_vault_url
        self.certificate_name = certificate_name
        self.credential = credential or DefaultAzureCredential()
        self.certificate_client = None
        self.secret_client = None
        self.logger = logging.getLogger(__name__)

    def authenticate(self):
        """
        Authenticate with Azure Key Vault and create clients

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Create clients for KeyVault certificates and secrets - reduced logging
            self.certificate_client = CertificateClient(
                vault_url=self.key_vault_url, credential=self.credential
            )

            self.secret_client = SecretClient(
                vault_url=self.key_vault_url, credential=self.credential
            )

            # Test connection by listing certificates
            next(
                self.certificate_client.list_properties_of_certificates(
                    max_page_size=1
                ),
                None,
            )

            # Reduced logging - moved to DEBUG level
            self.logger.debug(f"Successfully authenticated to Azure Key Vault")
            return True

        except Exception as e:
            self.logger.error(f"Failed to authenticate to Azure Key Vault: {str(e)}")
            return False

    def get_certificate(self, certificate_name=None):
        """
        Retrieve a certificate and its private key from Azure Key Vault

        Args:
            certificate_name (str, optional): Name of certificate to retrieve
                                             (uses self.certificate_name if not provided)

        Returns:
            tuple: (certificate, private_key) or None if retrieval fails
        """
        cert_name = certificate_name or self.certificate_name

        if not cert_name:
            self.logger.error("Certificate name not provided")
            return None

        if not self.certificate_client:
            if not self.authenticate():
                return None

        try:
            # Get certificate - reduced logging
            certificate = self.certificate_client.get_certificate(cert_name)

            # Get private key from the secret with the same name
            secret = self.secret_client.get_secret(cert_name)

            self.logger.debug(f"Retrieved certificate: {cert_name}")
            return (certificate, secret.value)

        except Exception as e:
            self.logger.error(f"Failed to retrieve certificate {cert_name}: {str(e)}")
            return None
