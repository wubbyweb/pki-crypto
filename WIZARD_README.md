# PKI Token Network Wizard

## Interactive CLI Tool for PKI Operations

The PKI Wizard provides a user-friendly, menu-driven interface for managing your PKI Token Network. No need to remember complex command-line arguments!

## Features

### 🧙‍♂️ **Guided Operations**
- Step-by-step token creation
- Interactive verification
- Secure package generation
- Network visualization

### 🔒 **Security First**
- Private key protection
- Secure distribution packages
- Input validation
- Confirmation prompts

### 🎯 **User-Friendly**
- Numbered menu selection
- Clear visual feedback
- Error handling with helpful messages
- Context-sensitive instructions

## Quick Start

```bash
# Start the wizard
python3 token-manager.py

# Follow the interactive prompts
# No command-line arguments needed!
```

## Wizard Workflow

### 1. **Network Setup**
- Automatically detects existing networks
- Creates new storage directories
- Loads cryptographic keys

### 2. **Master Token Creation**
```
🏛️  CREATE MASTER TOKEN
------------------------------
The master token serves as the root certificate authority.
Choose a descriptive name for your organization's root authority.

👉 Master node ID: corporate-root
```

### 3. **Token Issuance**
```
📄 ISSUE NEW TOKEN
------------------------------
Available token issuers:
  1. corporate-root (Level 0)

👉 Select issuer by number or enter node ID: 1
👉 New node ID: regional-office
👉 Token description/data: Regional Office Authority
```

### 4. **Token Verification**
```
🔍 VERIFY TOKEN
------------------------------
📋 Select Verification Method
  1. Chain Verification (Traditional)
  2. Master Direct Verification
  3. Hybrid Verification (All Methods)
  4. Issuer Verification

👉 Select option: 2

Status: ✅ VALID
Master direct verification:
  - Master signature verified for regional-office
```

### 5. **Secure Package Creation**
```
📦 CREATE SECURE DISTRIBUTION PACKAGE
---------------------------------------------
📋 Package creation summary:
   Token: regional-office
   Output Directory: regional-office_secure_package
   Contents: Certificate + Public Keys + Instructions
   🔒 Security: Private keys are NOT included

❓ Create secure package? (y/n): y

✅ Secure package created successfully!
```

## Menu Structure

```
📋 PKI Token Network Operations
--------------------------------------------------
  1. 🏛️  Create Master Token
  2. 📄 Issue New Token
  3. 🔍 Verify Token
  4. 📦 Create Secure Distribution Package
  5. 📊 View Network Overview
  6. 🔍 View Token Details
  7. 🔧 Change Storage Directory
  0. Back/Exit
```

## Error Handling

The wizard includes comprehensive error handling:

- **Input Validation**: Node IDs, menu selections, file paths
- **Network Errors**: Missing tokens, broken chains, invalid signatures
- **File System**: Permission issues, missing directories
- **Cryptographic**: Key loading, signature verification

## Security Features

### 🔒 **Private Key Protection**
- Private keys never distributed
- Local key generation guidance  
- Secure storage recommendations

### 📦 **Secure Distribution**
- Certificate-only packages
- Public key inclusion
- Security instructions
- Archive creation

### 🛡️ **Verification Methods**
- Chain verification
- Master direct verification
- Hybrid verification (all methods)
- Issuer verification

## Comparison: CLI vs Wizard

| Feature | CLI Command | Wizard |
|---------|-------------|---------|
| Create Master | `pki-cli.py create-master corp-root` | Interactive menu with validation |
| Issue Token | `pki-cli.py issue corp-root office --data "..."` | Guided selection with issuer list |
| Verify Token | `pki-cli.py verify office --mode hybrid` | Menu-driven method selection |
| Secure Package | `python3 token-packager.py` | Interactive package creation |
| View Network | `pki-cli.py list` | Visual hierarchy display |

## Benefits

### ✅ **Ease of Use**
- No memorization of commands
- Interactive guidance
- Visual feedback

### ✅ **Error Prevention**
- Input validation
- Confirmation prompts
- Clear error messages

### ✅ **Security**
- Best practice enforcement
- Private key protection
- Secure defaults

### ✅ **Learning**
- Educational prompts
- Security explanations
- Step-by-step guidance

## Advanced Features

### **Network Visualization**
```
🌳 Hierarchy Structure:
   Master: 1 token(s)
     • corporate-root
   Level 1: 2 token(s)
     • regional-office (issued by corporate-root)
     • eu-office (issued by corporate-root)
   Level 2: 1 token(s)
     • department-head (issued by regional-office)
```

### **Token Details View**
```
📄 Token Details: regional-office
--------------------------------------------------
Node ID: regional-office
Token Hash: c01db0328ab7b054847cf10ea33386368e97db105b5c75a1
Master ID: corporate-root
Issuer ID: corporate-root
Hierarchy Level: 1
Verification Methods: chain, master-direct, issuer-direct
```

### **Batch Operations**
- Multiple token verification
- Network health checks
- Bulk package creation

## Getting Started

1. **Install Dependencies**
   ```bash
   pip3 install cryptography
   ```

2. **Start Wizard**
   ```bash
   python3 token-manager.py
   ```

3. **Follow Interactive Prompts**
   - The wizard guides you through each step
   - No prior PKI knowledge required
   - Built-in help and explanations

4. **Create Your Network**
   - Start with master token
   - Issue tokens hierarchically
   - Verify and distribute securely

The wizard makes PKI token management accessible to users of all skill levels while maintaining enterprise-grade security standards.
