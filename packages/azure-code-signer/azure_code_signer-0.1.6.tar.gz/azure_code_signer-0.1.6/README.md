# Azure Code Signer

Azure Code Signer is a command line tool that allows you to code sign files using a code signing certificate stored in Azure Key Vault. This tool is designed to work across multiple platforms, including Linux, macOS, and Windows.

## Features

- Authenticate with Azure Key Vault to retrieve code signing certificates
- Sign files using certificates from Azure Key Vault
- Generate detached signature files (.sig)
- Verify file signatures
- Cross-platform compatibility (Windows, macOS, Linux)
- Support for various certificate formats (PEM, DER, PKCS#12)

## Prerequisites

- Python 3.7 or higher
- An Azure account with access to Azure Key Vault
- A code signing certificate stored in Azure Key Vault

## Installation

### Using pip (recommended)

```bash
pip install azure-code-signer
```

### From source

```bash
git clone https://github.com/yourusername/azure-code-signer.git
cd azure-code-signer
pip install -e .
```

## Authentication with Azure

The tool uses Azure's DefaultAzureCredential for authentication, which tries multiple authentication methods in the following order:

1. Environment variables
2. Managed Identity
3. Visual Studio Code credentials
4. Azure CLI credentials
5. Interactive browser authentication

### Authentication via Environment Variables

To authenticate using environment variables, set the following:

```bash
# Required for service principal authentication
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Optional - to specify which subscription to use
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

#### Setting Up a Service Principal

1. **Create a service principal in Azure**:
   ```bash
   az ad sp create-for-rbac --name "AzureCodeSigner" --skip-assignment
   ```
   This will output JSON containing your `appId` (client ID), `password` (client secret), and `tenant`.

2. **Grant Key Vault access to your service principal**:
   ```bash
   az keyvault set-policy --name your-keyvault-name \
     --object-id <service-principal-object-id> \
     --certificate-permissions get list \
     --secret-permissions get list
   ```

#### Setting Environment Variables

**Linux/macOS**:
```bash
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
```

**Windows (Command Prompt)**:
```cmd
set AZURE_TENANT_ID=your-tenant-id
set AZURE_CLIENT_ID=your-client-id
set AZURE_CLIENT_SECRET=your-client-secret
```

**Windows (PowerShell)**:
```powershell
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_CLIENT_ID = "your-client-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
```

### Authentication via Azure CLI

If you prefer interactive authentication, you can use Azure CLI:

```bash
# Login with Azure CLI
az login

# Set your subscription (if necessary)
az account set --subscription <subscription-id>
```

## Usage

### Basic usage

```bash
azure-code-signer --vault-url https://your-vault.vault.azure.net/ --cert-name your-cert-name --file path/to/file
```

### Command line arguments

| Argument | Description |
|----------|-------------|
| `--vault-url` | URL of your Azure Key Vault (required) |
| `--cert-name` | Name of the certificate in Key Vault (required) |
| `--file` | Path to the file to sign or verify (required) |
| `--output` | Path where to save the signature (default: file.sig) |
| `--verify` | Verify an existing signature instead of signing |
| `--verbose` | Enable verbose logging |
| `--pkcs12-password` | Password for PKCS#12 certificate if required |

### Signing a file

```bash
azure-code-signer --vault-url https://your-vault.vault.azure.net/ --cert-name your-cert-name --file path/to/file
```

This will create a detached signature file at `path/to/file.sig`.

### Verifying a signature

```bash
azure-code-signer --vault-url https://your-vault.vault.azure.net/ --cert-name your-cert-name --file path/to/file --verify
```

### Specifying a signature output path

```bash
azure-code-signer --vault-url https://your-vault.vault.azure.net/ --cert-name your-cert-name --file path/to/file --output path/to/custom-signature.sig
```

### Working with password-protected certificates

If your certificate in Azure Key Vault is password-protected:

```bash
azure-code-signer --vault-url https://your-vault.vault.azure.net/ --cert-name your-cert-name --file path/to/file --pkcs12-password your-password
```

## Certificate Formats

Azure Code Signer automatically handles various certificate formats:

- Certificates in Azure Key Vault (native format)
- PKCS#12 (PFX) format with or without password protection
- PEM format certificates and keys
- Base64-encoded certificates
- Raw certificate data with missing headers

The tool will attempt to detect and convert between formats as needed.

## Troubleshooting

### Enable verbose logging

For detailed debugging information:

```bash
azure-code-signer --vault-url https://your-vault.vault.azure.net/ --cert-name your-cert-name --file path/to/file --verbose
```

### Permission errors

Ensure your Azure account has the following permissions on the Key Vault:
- `get` permission for certificates
- `get` permission for secrets

### Certificate format issues

If you encounter errors like "Failed to load certificate and/or private key", check:
- Is the certificate in the expected format?
- Does it require a password? (Use `--pkcs12-password`)
- Does the service principal have access to both certificate and secret?

### Authentication errors

If authentication fails:
- Check that environment variables are correctly set and spelled
- Verify the service principal has appropriate permissions
- Try using Azure CLI authentication with `az login`
- Ensure your client secret hasn't expired

### Error: bytearray object cannot be converted to PyBytes

This error is typically resolved by newer versions of the tool. Update to the latest version:

```bash
pip install --upgrade azure-code-signer
```

## Security Considerations

- Never commit environment variables with secrets to source control
- Consider using a secure secrets manager to store service principal credentials
- For CI/CD pipelines, use the pipeline's built-in secrets management
- Limit the permissions of your service principal to only what's needed
- Rotate your client secrets regularly

## Azure Key Vault Setup

1. Create a Key Vault in Azure Portal
2. Import or generate a code signing certificate
3. Add a secret with the same name as your certificate
4. Grant your user or service principal access to the Key Vault

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.