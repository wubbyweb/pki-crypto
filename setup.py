#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="pki-token-network",
    version="1.0.0",
    author="Rajesh G",
    author_email="agentic.engineer@gmail.com",
    description="A secure blockchain-inspired PKI token system with hierarchical verification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wubbyweb/pki-crypto.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
        ],
    },
    entry_points={
        'console_scripts': [
            'pki-cli=pki_token_network.scripts:pki_cli_main',
            'token-manager=pki_token_network.scripts:token_manager_main',
            'token-packager=pki_token_network.scripts:token_packager_main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.json'],
    },
    project_urls={
        "Bug Reports": "https://github.com/wubbyweb/pki-crypto/issues",
        "Source": "https://github.com/wubbyweb/pki-crypto",
        "Documentation": "https://github.com/wubbyweb/pki-crypto/blob/main/README.md",
    },
    keywords="pki, cryptography, blockchain, token, verification, security, certificates",
    zip_safe=False,
)