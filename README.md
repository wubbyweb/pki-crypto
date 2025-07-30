# PKI Token Network System

A secure blockchain-inspired token system implementing Public Key Infrastructure (PKI) concepts with hash chaining for network security.

## Features

- **Master Token Creation**: Creates a root certificate-like master token
- **Hierarchical Token Issuance**: Tokens can issue child tokens forming a tree structure
- **Hash Chain Verification**: Each token contains the hash of its issuer's token
- **Complete Chain Validation**: Verification traverses up to the master token
- **Persistent Storage**: Tokens are stored as JSON files for persistence
- **Command Line Interface**: Easy-to-use CLI for all operations
- **Interactive Wizard**: User-friendly guided interface for all PKI operations
- **Multiple Verification Methods**: Chain, master-direct, issuer-direct, and hybrid verification
- **Secure Distribution**: Certificate packages without private key exposure
- **Cryptographic Security**: RSA signatures with hierarchical trust delegation

## Architecture

```
Master Token (hash: ABC123...)
├── Node A (hash: DEF456..., issued by Master)
│   ├── Node A1 (hash: GHI789..., issued by Node A)
│   └── Node A2 (hash: JKL012..., issued by Node A)
└── Node B (hash: MNO345..., issued by Master)
    └── Node B1 (hash: PQR678..., issued by Node B)
```

## Quick Start - Interactive Wizard 🧙‍♂️

For the easiest experience, use the interactive wizard:

```bash
# Start the interactive token manager
python3 token-manager.py

# Follow the guided prompts:
# 1. 🏛️  Create Master Token
# 2. 📄 Issue New Token  
# 3. 🔍 Verify Token
# 4. 📦 Create Secure Distribution Package
# 5. 📊 View Network Overview
```

The wizard provides:
- ✅ **Step-by-step guidance** with clear instructions
- ✅ **Input validation** and error handling
- ✅ **Visual feedback** with status indicators
- ✅ **Security best practices** enforcement
- ✅ **No command memorization** required

## Command Line Examples

### 1. Create Master Token
```bash
python3 pki-cli.py create-master master-node
```

### 2. Issue Tokens to Child Nodes
```bash
python3 pki-cli.py issue master-node node-a --data "Node A credentials"
python3 pki-cli.py issue master-node node-b --data "Node B credentials"
```

### 3. Issue Tokens from Child Nodes
```bash
python3 pki-cli.py issue node-a node-a1 --data "Subnode A1"
python3 pki-cli.py issue node-a node-a2 --data "Subnode A2"
python3 pki-cli.py issue node-b node-b1 --data "Subnode B1"
```

### 4. Verify Token Authenticity
```bash
python3 pki-cli.py verify node-a1
```
Output:
```
Token verification for node: node-a1
Status: VALID

Verification chain:
  1. node-a1 -> GHI789...
  2. node-a -> DEF456...
  3. master-node -> ABC123...
```

### 5. Show Token Details
```bash
python3 pki-cli.py show node-a
```

### 6. List All Tokens
```bash
python3 pki-cli.py list
```

## Security Features

1. **Hash Chain Integrity**: Each token includes the hash of its issuer's token
2. **Immutable Chain**: Any modification breaks the hash chain, making tampering detectable
3. **Root of Trust**: All tokens must trace back to the master token to be valid
4. **Unique Identifiers**: Each token has a unique ID and timestamp
5. **Input Validation**: Node IDs are validated for security

## CLI Commands

- `create-master <node_id>` - Create a master token
- `issue <issuer> <new_node> [--data <data>]` - Issue a new token
- `verify <node_id>` - Verify a token's authenticity
- `show <node_id>` - Display token information
- `list` - List all tokens in the network
- `--storage-dir <path>` - Specify custom storage directory

## Token Structure

Each token contains:
- `node_id`: Unique identifier for the node
- `issuer_token_hash`: Hash of the issuer's token (null for master)
- `issuer_id`: ID of the issuing node (null for master)
- `timestamp`: Creation timestamp (ISO format)
- `token_id`: Unique token identifier (UUID)
- `token_data`: Optional custom data
- `token_hash`: SHA256 hash of the token content

## Project Structure

```
pki-crypto/
├── README.md                    # Main documentation
├── HOWTO.md                    # Tutorial guide
├── WIZARD_README.md            # Token manager interface guide
├── TDD_SUMMARY.md              # Test-driven development summary
├── requirements.txt            # Python dependencies
├── pki-network.py             # Core PKI system implementation
├── pki-cli.py                 # Command line interface
├── token-manager.py           # Interactive token manager interface
├── token-manager-demo.py      # Token manager demonstration
├── token-packager.py          # Secure package creation
├── tests/                     # All test files
│   ├── README.md             # Test documentation
│   ├── run_all_tests.py      # Test runner
│   ├── test_*.py             # Individual test files
│   └── analyze_current_system.py
└── token_storage/             # Default token storage
    ├── *.json                # Token files
    └── keys/                 # Cryptographic keys
```

## Testing

All tests are located in the `tests/` directory:

```bash
# Run all tests
python3 tests/run_all_tests.py

# Run specific test
python3 -m pytest tests/test_pki_network.py -v
```

## Error Handling

The system validates:
- Node ID format (alphanumeric, hyphens, underscores, dots only)
- Node ID length (64 characters max)
- Duplicate tokens
- Missing issuers
- Broken hash chains
- Invalid master tokens