#!/usr/bin/env python3

import os
import json
import tempfile
from pki_token import PKITokenNetwork
from cryptography.hazmat.primitives import serialization

def create_secure_token_package(network: PKITokenNetwork, node_id: str, output_dir: str):
    """Create a secure token package for distribution to a node"""
    
    if node_id not in network.tokens:
        raise ValueError(f"Token for {node_id} not found")
    
    token = network.tokens[node_id]
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Token/Certificate file (contains all verification data)
    token_file = os.path.join(output_dir, f"{node_id}_certificate.json")
    with open(token_file, 'w') as f:
        json.dump(token.to_dict(), f, indent=2)
    
    # 2. Master public key (for master signature verification)
    if network.master_public_key:
        master_pub_pem = network.master_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        master_pub_file = os.path.join(output_dir, "master_public_key.pem")
        with open(master_pub_file, 'wb') as f:
            f.write(master_pub_pem)
    
    # 3. Issuer public key (for issuer signature verification)
    if token.issuer_id and token.issuer_id in network.node_keys:
        _, issuer_public_key = network.node_keys[token.issuer_id]
        issuer_pub_pem = issuer_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        issuer_pub_file = os.path.join(output_dir, f"{token.issuer_id}_public_key.pem")
        with open(issuer_pub_file, 'wb') as f:
            f.write(issuer_pub_pem)
    
    # 4. Verification instructions
    instructions = {
        "node_id": node_id,
        "certificate_file": f"{node_id}_certificate.json",
        "master_public_key": "master_public_key.pem",
        "issuer_public_key": f"{token.issuer_id}_public_key.pem" if token.issuer_id else None,
        "verification_methods": list(token.verification_paths),
        "instructions": [
            "1. Generate your own RSA key pair locally (never share private key)",
            "2. Use the certificate file for identity verification",
            "3. Use public keys to verify signatures in the certificate",
            "4. The private key corresponding to this certificate is NOT included for security",
            "5. To issue tokens to others, use your locally generated private key"
        ],
        "security_notes": [
            "⚠️  Private keys are never distributed",
            "✅ Generate your own key pair on your secure system",
            "✅ Verify certificate signatures using provided public keys",
            "✅ Store your private key securely (encrypted storage recommended)"
        ]
    }
    
    instructions_file = os.path.join(output_dir, "README.json")
    with open(instructions_file, 'w') as f:
        json.dump(instructions, f, indent=2)

def demonstrate_secure_distribution():
    """Demonstrate secure token distribution vs current insecure method"""
    
    print("=" * 80)
    print("SECURE TOKEN DISTRIBUTION DEMONSTRATION")
    print("=" * 80)
    
    # Setup
    demo_dir = "demo_secure_dist"
    if os.path.exists(demo_dir):
        import shutil
        shutil.rmtree(demo_dir)
    
    network = PKITokenNetwork(demo_dir)
    
    # Create tokens
    master = network.create_master_token("pki-authority")
    client = network.issue_token("pki-authority", "client-system", "Production Client")
    
    print("🏢 Created PKI Authority and issued token to client-system")
    
    # Current insecure method
    print("\n❌ CURRENT INSECURE DISTRIBUTION:")
    print("Files created for client-system:")
    client_files = [f for f in os.listdir(demo_dir) if "client-system" in f]
    for file in client_files:
        print(f"  📄 {file}")
    
    # Check for private key
    keys_dir = os.path.join(demo_dir, "keys")
    if os.path.exists(keys_dir):
        key_files = [f for f in os.listdir(keys_dir) if "client-system" in f]
        for file in key_files:
            if "private" in file:
                print(f"  🚨 {file} (SECURITY RISK - private key distributed!)")
            else:
                print(f"  📄 keys/{file}")
    
    # Secure distribution
    print("\n✅ SECURE DISTRIBUTION METHOD:")
    secure_package_dir = "client_secure_package"
    create_secure_token_package(network, "client-system", secure_package_dir)
    
    print("Secure package contents:")
    for file in os.listdir(secure_package_dir):
        print(f"  📦 {file}")
    
    # Show package contents
    print("\n📋 SECURITY INSTRUCTIONS FOR CLIENT:")
    with open(os.path.join(secure_package_dir, "README.json"), 'r') as f:
        instructions = json.load(f)
    
    for instruction in instructions["instructions"]:
        print(f"  {instruction}")
    
    print("\n🔒 SECURITY NOTES:")
    for note in instructions["security_notes"]:
        print(f"  {note}")
    
    print("\n🔍 CERTIFICATE VERIFICATION:")
    print("Client can verify certificate using:")
    print(f"  - Master signature via: {instructions['master_public_key']}")
    if instructions["issuer_public_key"]:
        print(f"  - Issuer signature via: {instructions['issuer_public_key']}")
    print(f"  - Available methods: {', '.join(instructions['verification_methods'])}")
    
    # Demonstrate verification with only public keys
    print("\n✅ VERIFICATION TEST (using only distributed public keys):")
    
    # Load public keys from secure package
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    
    with open(os.path.join(secure_package_dir, "master_public_key.pem"), 'rb') as f:
        master_pub_key = load_pem_public_key(f.read())
    
    # Verify master signature
    client_token = network.tokens["client-system"]
    can_verify_master = client_token.verify_master_signature(master_pub_key)
    print(f"  Master signature verification: {'✅ VALID' if can_verify_master else '❌ INVALID'}")
    
    # Cleanup
    import shutil
    shutil.rmtree(demo_dir)
    shutil.rmtree(secure_package_dir)
    
    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS:")
    print("=" * 80)
    print("❌ NEVER distribute private keys to nodes")
    print("✅ Distribute: certificate + public keys + instructions")
    print("✅ Nodes generate their own key pairs locally")
    print("✅ Verification works with only public keys")
    print("✅ Private keys remain secure on each system")

if __name__ == "__main__":
    demonstrate_secure_distribution()