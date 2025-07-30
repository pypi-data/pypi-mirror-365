from setuptools import setup, find_packages

setup(
    name="azure-code-signer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "azure-identity>=1.10.0",
        "azure-keyvault-certificates>=4.5.0",
        "azure-keyvault-secrets>=4.5.0",
        "cryptography>=38.0.0",
    ],
    entry_points={
        "console_scripts": [
            "azure-code-signer=src.main:main",
        ],
    },
)
