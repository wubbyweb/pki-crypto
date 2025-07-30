# PKI Token Network - How-To Guide

## Overview

This guide explains how to use the PKI Token Network system for secure token creation, distribution, and validation. The system implements a hierarchical Public Key Infrastructure (PKI) with cryptographic signatures for distributed authentication.

## Table of Contents

1. [System Setup](#system-setup)
2. [Creating Master Authority](#creating-master-authority)
3. [Issuing Tokens](#issuing-tokens)
4. [Creating Secure Distribution Packages](#creating-secure-distribution-packages)
5. [Node Token Generation and Distribution](#node-token-generation-and-distribution)
6. [Token Validation Methods](#token-validation-methods)
7. [Advanced Verification](#advanced-verification)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## System Setup

### Prerequisites

```bash
# Install required cryptography library
pip3 install cryptography

# Or if using homebrew on macOS
brew install python-cryptography
```

### Directory Structure

The system creates the following structure:
```
project/
├── pki_token.py          # Core system
├── cli.py                # Command line interface
├── secure_distribution.py # Secure package creation
└── token_storage/        # Storage directory
    ├── tokens/           # Token files
    └── keys/             # Cryptographic keys
```

---

## Creating Master Authority

### Step 1: Create Master Token

The master token serves as the root certificate authority for your PKI network.

```bash
# Create master token
python3 cli.py create-master corporate-root

# Expected output:
# Master token created for node: corporate-root
# Token hash: a1b2c3d4e5f6...
```

**What happens:**
- Creates master token with self-signed certificate
- Generates RSA 2048-bit key pair for master
- Stores master private key securely
- Master can now issue tokens to other nodes

### Step 2: Verify Master Token

```bash
# Verify master token using different methods
python3 cli.py verify corporate-root --mode chain
python3 cli.py verify corporate-root --mode master
python3 cli.py verify corporate-root --mode hybrid
```

---

## Issuing Tokens

### Basic Token Issuance

```bash
# Issue token to regional office
python3 cli.py issue corporate-root us-office --data "US Regional Office"

# Issue token to department
python3 cli.py issue us-office engineering-dept --data "Engineering Department"

# Issue token to team
python3 cli.py issue engineering-dept backend-team --data "Backend Development Team"

# Issue token to individual
python3 cli.py issue backend-team john-doe --data "Senior Backend Developer"
```

### View Token Information

```bash
# Show detailed token information
python3 cli.py show john-doe

# List all tokens in network
python3 cli.py list
```

**Example Output:**
```json
{
  "node_id": "john-doe",
  "issuer_id": "backend-team",
  "master_id": "corporate-root",
  "hierarchy_level": 4,
  "master_signature": "iMpays8ItAzxxh+gkX29WS...",
  "issuer_signature": "bfRD5Pi2lHXNOxiHETyFG...",
  "verification_paths": ["chain", "master-direct", "issuer-direct"]
}
```

---

## Creating Secure Distribution Packages

### Step 1: Generate Secure Package

**⚠️ SECURITY CRITICAL**: Never distribute private keys!

```bash
# Create secure distribution package
python3 -c "
from secure_distribution import create_secure_token_package
from pki_token import PKITokenNetwork

network = PKITokenNetwork('token_storage')
create_secure_token_package(network, 'john-doe', 'john_doe_package')
print('Secure package created in john_doe_package/')
"
```

### Step 2: Package Contents

The secure package contains:
```
john_doe_package/
├── john-doe_certificate.json    # Token with embedded signatures
├── master_public_key.pem         # Master's public key for verification
├── backend-team_public_key.pem   # Issuer's public key for verification
└── README.json                   # Security instructions
```

### Step 3: Distribute Package

```bash
# Copy package to target system (example)
scp -r john_doe_package/ user@target-system:/opt/pki/

# Or create archive for distribution
tar -czf john_doe_certificate.tar.gz john_doe_package/
```

**What to distribute:**
- ✅ Certificate file (contains token data and signatures)
- ✅ Public keys (for signature verification)
- ✅ Instructions (security guidelines)
- ❌ **NEVER** distribute private keys

---

## Node Token Generation and Distribution

### Step 1: Node Receives Package

On the target node system:

```bash
# Extract received package
tar -xzf john_doe_certificate.tar.gz
cd john_doe_package/

# Read security instructions
cat README.json
```

### Step 2: Node Generates Own Keys

Each node must generate its own key pair:

```bash
# Generate RSA key pair (node does this locally)
python3 -c "
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Save private key (keep secure!)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

with open('node_private_key.pem', 'wb') as f:
    f.write(private_pem)

# Save public key (can be shared)
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open('node_public_key.pem', 'wb') as f:
    f.write(public_pem)

print('✅ Key pair generated successfully')
print('🔒 Keep node_private_key.pem secure and never share it')
print('📢 node_public_key.pem can be shared for verification')
"
```

### Step 3: Node Issues Tokens to Others

If the node needs to issue tokens to subordinates:

```bash
# Set up local PKI environment
mkdir node_pki_storage
export PKI_STORAGE_DIR="node_pki_storage"

# Import node's certificate and keys into local system
python3 -c "
import os
import json
import shutil
from pki_token import PKITokenNetwork, SecureToken

# Create local PKI network
network = PKITokenNetwork('node_pki_storage')

# Load received certificate
with open('john-doe_certificate.json', 'r') as f:
    cert_data = json.load(f)

# Import certificate as token
token = SecureToken.from_dict(cert_data)
network.tokens[token.node_id] = token

# Copy keys to local storage
os.makedirs('node_pki_storage/keys', exist_ok=True)
shutil.copy('node_private_key.pem', 'node_pki_storage/keys/john-doe_private.pem')
shutil.copy('node_public_key.pem', 'node_pki_storage/keys/john-doe_public.pem')

# Load master keys for verification
shutil.copy('master_public_key.pem', 'node_pki_storage/keys/master_public.pem')

print('✅ Local PKI environment configured')
"

# Now issue tokens to subordinates
python3 cli.py --storage-dir node_pki_storage issue john-doe junior-dev --data "Junior Developer"
```

### Step 4: Create Distribution Package for Subordinate

```bash
# Create secure package for junior developer
python3 -c "
from secure_distribution import create_secure_token_package
from pki_token import PKITokenNetwork

network = PKITokenNetwork('node_pki_storage')
create_secure_token_package(network, 'junior-dev', 'junior_dev_package')
print('Package created for junior-dev')
"

# Distribute to junior developer
tar -czf junior_dev_certificate.tar.gz junior_dev_package/
```

---

## Token Validation Methods

### Method 1: Chain Verification (Traditional)

Validates token by traversing the complete chain to master:

```bash
# Chain verification (requires all intermediate tokens)
python3 cli.py verify john-doe --mode chain

# Example output:
# Token verification for node: john-doe
# Verification mode: chain
# Status: VALID
# 
# Verification chain:
#   1. john-doe -> cc5c61d7a7a9c487...
#   2. backend-team -> 3ae615c238d25366...
#   3. engineering-dept -> 0c05cb03d59f8967...
#   4. us-office -> b6e3109be2d16ee9...
#   5. corporate-root -> 08cd0be32e6a81d0...
```

### Method 2: Master Direct Verification (Key Innovation)

Master can verify any token directly without intermediate tokens:

```bash
# Master direct verification (no intermediates needed)
python3 cli.py verify john-doe --mode master

# Example output:
# Token verification for node: john-doe
# Verification mode: master
# Status: VALID
# 
# Master direct verification:
#   1. Master signature verified for john-doe
```

### Method 3: Issuer Verification

Verify that a token was issued by a specific node:

```bash
# Direct issuer verification
python3 cli.py verify-as-issuer backend-team john-doe

# Indirect issuer verification
python3 cli.py verify-as-issuer us-office john-doe

# Example output:
# Issuer verification: backend-team → john-doe
# Status: VALID
# 
# Verification path:
#   1. Direct issuer signature verified: backend-team → john-doe
```

### Method 4: Hybrid Verification (All Methods)

Uses all available verification methods for maximum confidence:

```bash
# Hybrid verification
python3 cli.py verify john-doe --mode hybrid

# Example output:
# Token verification for node: john-doe
# Verification mode: hybrid
# Overall Status: VALID
# 
# Verification Results by Method:
#   chain: VALID
#     - john-doe -> cc5c61d7a7a9c487...
#     - backend-team -> 3ae615c238d25366...
#     [...]
#   master-direct: VALID
#     - Master signature verified for john-doe
#   issuer-direct: VALID
#     - Direct issuer signature verified: backend-team → john-doe
```

---

## Advanced Verification

### Offline Verification

Verify tokens without network connectivity:

```bash
# Create minimal verification environment
mkdir offline_verification
cd offline_verification

# Copy only necessary files
cp ../john_doe_package/john-doe_certificate.json .
cp ../john_doe_package/master_public_key.pem .

# Verify using only certificate and master public key
python3 -c "
import json
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from pki_token import SecureToken

# Load certificate
with open('john-doe_certificate.json', 'r') as f:
    cert_data = json.load(f)

token = SecureToken.from_dict(cert_data)

# Load master public key
with open('master_public_key.pem', 'rb') as f:
    master_public_key = load_pem_public_key(f.read())

# Verify master signature
is_valid = token.verify_master_signature(master_public_key)
print(f'Token validation: {\"VALID\" if is_valid else \"INVALID\"}')
print(f'Node: {token.node_id}')
print(f'Hierarchy Level: {token.hierarchy_level}')
print(f'Master: {token.master_id}')
"
```

### Distributed Verification

Verify tokens across different systems without full token chain:

```bash
# System A: Master authority
python3 cli.py --storage-dir master_storage verify any-token --mode master

# System B: Regional office
python3 cli.py --storage-dir regional_storage verify-as-issuer regional-office any-descendant

# System C: Individual node (offline)
# Uses certificate file and public keys only (see offline verification above)
```

### Batch Verification

Verify multiple tokens efficiently:

```bash
# Verify all tokens in network
python3 -c "
from pki_token import PKITokenNetwork

network = PKITokenNetwork('token_storage')
tokens = network.list_all_tokens()

print(f'Verifying {len(tokens)} tokens...')
for token_data in tokens:
    node_id = token_data['node_id']
    is_valid, _ = network.verify_token_hybrid(node_id)
    status = 'VALID' if is_valid else 'INVALID'
    print(f'{node_id}: {status}')
"
```

---

## Security Best Practices

### 1. Private Key Security

```bash
# ✅ GOOD: Generate keys locally
python3 -c "from cryptography.hazmat.primitives.asymmetric import rsa; ..."

# ❌ BAD: Never share private keys
# Don't do: scp node_private_key.pem other-system:/

# ✅ GOOD: Secure storage with encryption
gpg --symmetric --armor --output node_private_key.pem.gpg node_private_key.pem
rm node_private_key.pem  # Remove unencrypted version
```

### 2. Certificate Distribution

```bash
# ✅ GOOD: Distribute secure packages
tar -czf secure_certificate_package.tar.gz certificate_package/

# ✅ GOOD: Verify package integrity
sha256sum secure_certificate_package.tar.gz > package.sha256
# Verify: sha256sum -c package.sha256

# ❌ BAD: Don't distribute raw private keys
```

### 3. Verification Security

```bash
# ✅ GOOD: Use multiple verification methods
python3 cli.py verify token --mode hybrid

# ✅ GOOD: Verify master signature for high-security operations
python3 cli.py verify token --mode master

# ✅ GOOD: Check hierarchy levels for authorization
python3 cli.py show token | grep hierarchy_level
```

### 4. Network Security

```bash
# ✅ GOOD: Use secure channels for distribution
scp certificate_package.tar.gz user@system:/secure/location/

# ✅ GOOD: Validate certificates after receiving
python3 cli.py verify received-token --mode hybrid

# ✅ GOOD: Regular key rotation (advanced)
# Periodically regenerate keys and reissue certificates
```

---

## Troubleshooting

### Common Issues

#### 1. "Cryptography module not found"

```bash
# Solution: Install cryptography library
pip3 install cryptography
# Or: brew install python-cryptography
```

#### 2. "Master token already exists"

```bash
# Solution: Use existing master or clean storage
rm -rf token_storage/  # WARNING: Removes all tokens
python3 cli.py create-master new-master
```

#### 3. "Token verification failed"

```bash
# Debug: Check verification methods available
python3 cli.py show problematic-token | grep verification_paths

# Try different verification modes
python3 cli.py verify problematic-token --mode chain
python3 cli.py verify problematic-token --mode master
python3 cli.py verify problematic-token --mode hybrid
```

#### 4. "Issuer not found"

```bash
# Solution: Ensure all intermediate tokens are present
python3 cli.py list  # Check available tokens

# Or use master direct verification
python3 cli.py verify token --mode master
```

#### 5. "Private key permission denied"

```bash
# Solution: Fix file permissions
chmod 600 node_private_key.pem
chmod 644 node_public_key.pem
```

### Debugging Commands

```bash
# Check token information
python3 cli.py show token-id

# List all tokens
python3 cli.py list

# Verify with detailed output
python3 cli.py verify token-id --mode hybrid

# Check storage directory
ls -la token_storage/
ls -la token_storage/keys/

# Test key loading
python3 -c "
from pki_token import PKITokenNetwork
network = PKITokenNetwork('token_storage')
print(f'Master key loaded: {network.master_private_key is not None}')
print(f'Node keys: {list(network.node_keys.keys())}')
"
```

### Performance Optimization

```bash
# For large networks, use master direct verification
python3 cli.py verify token --mode master  # Faster than chain

# Batch operations for multiple tokens
python3 -c "
from pki_token import PKITokenNetwork
network = PKITokenNetwork('token_storage')

# Verify multiple tokens efficiently
tokens = ['token1', 'token2', 'token3']
for token in tokens:
    is_valid, _ = network.verify_token_direct_master(token)
    print(f'{token}: {\"VALID\" if is_valid else \"INVALID\"}')
"
```

---

## Summary

This PKI Token Network system provides:

- ✅ **Secure Token Distribution**: Certificates without private keys
- ✅ **Hierarchical Trust**: Multi-level organizational structure  
- ✅ **Multiple Verification**: Chain, master-direct, issuer-direct, hybrid
- ✅ **Offline Capability**: Verify tokens without network connectivity
- ✅ **Cryptographic Security**: RSA signatures and SHA256 hashing
- ✅ **Scalable Architecture**: Handles deep hierarchies efficiently

**Key Security Principle**: Private keys never leave their originating system. Only certificates and public keys are distributed for verification.

For additional support or advanced configurations, refer to the source code documentation in `pki_token.py` and `cli.py`.