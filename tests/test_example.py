#!/usr/bin/env python3

import os
import shutil
from pki_network import PKITokenNetwork

def test_pki_network():
    test_dir = "test_tokens"
    
    # Clean up any existing test directory
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    print("=== PKI Token Network Test ===\n")
    
    # Initialize network
    network = PKITokenNetwork(test_dir)
    
    # Test 1: Create master token
    print("1. Creating master token...")
    try:
        master = network.create_master_token("master-node")
        print(f"   ✓ Master token created: {master.token_hash[:16]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Test 2: Issue child tokens
    print("\n2. Issuing child tokens...")
    try:
        node_a = network.issue_token("master-node", "node-a", "Node A data")
        node_b = network.issue_token("master-node", "node-b", "Node B data")
        print(f"   ✓ Token issued to node-a: {node_a.token_hash[:16]}...")
        print(f"   ✓ Token issued to node-b: {node_b.token_hash[:16]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Test 3: Issue grandchild tokens
    print("\n3. Issuing grandchild tokens...")
    try:
        node_a1 = network.issue_token("node-a", "node-a1", "Subnode A1")
        node_a2 = network.issue_token("node-a", "node-a2", "Subnode A2")
        node_b1 = network.issue_token("node-b", "node-b1", "Subnode B1")
        print(f"   ✓ Token issued to node-a1: {node_a1.token_hash[:16]}...")
        print(f"   ✓ Token issued to node-a2: {node_a2.token_hash[:16]}...")
        print(f"   ✓ Token issued to node-b1: {node_b1.token_hash[:16]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Test 4: Verify tokens
    print("\n4. Verifying tokens...")
    test_nodes = ["master-node", "node-a", "node-b", "node-a1", "node-a2", "node-b1"]
    
    for node in test_nodes:
        is_valid, chain = network.verify_token(node)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"   {status}: {node} (chain length: {len(chain)})")
        if not is_valid:
            print(f"     Reason: {chain[-1] if chain else 'Unknown'}")
    
    # Test 5: Show network structure
    print("\n5. Network structure:")
    tokens = network.list_all_tokens()
    for token in tokens:
        token_type = "MASTER" if token['issuer_token_hash'] is None else "NODE"
        issuer_info = f" (issued by {token['issuer_id']})" if token['issuer_id'] else ""
        print(f"   {token['node_id']}: {token_type}{issuer_info}")
    
    # Test 6: Error handling
    print("\n6. Testing error handling...")
    
    # Try to create duplicate master
    try:
        network.create_master_token("master-node-2")
        print("   ✗ Should have failed: duplicate master")
    except ValueError as e:
        print(f"   ✓ Correctly rejected duplicate master: {e}")
    
    # Try to issue to existing node
    try:
        network.issue_token("master-node", "node-a", "Duplicate")
        print("   ✗ Should have failed: duplicate node")
    except ValueError as e:
        print(f"   ✓ Correctly rejected duplicate node: {e}")
    
    # Try to issue from non-existent node
    try:
        network.issue_token("non-existent", "new-node", "Invalid")
        print("   ✗ Should have failed: non-existent issuer")
    except ValueError as e:
        print(f"   ✓ Correctly rejected non-existent issuer: {e}")
    
    # Test 7: Simulate hash chain break
    print("\n7. Testing hash chain integrity...")
    
    # Create a new network instance to test persistence
    network2 = PKITokenNetwork(test_dir)
    is_valid, chain = network2.verify_token("node-a1")
    print(f"   ✓ Persistent verification: {'VALID' if is_valid else 'INVALID'}")
    
    # Manually corrupt a token file to test integrity
    token_file = f"{test_dir}/node-a_token.json"
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            content = f.read()
        
        # Corrupt the token hash
        corrupted = content.replace(node_a.token_hash, "corrupted_hash_12345")
        with open(token_file, 'w') as f:
            f.write(corrupted)
        
        # Test with corrupted chain
        network3 = PKITokenNetwork(test_dir)
        is_valid, chain = network3.verify_token("node-a1")
        print(f"   ✓ Corrupted chain detection: {'INVALID' if not is_valid else 'FAILED TO DETECT'}")
    
    print("\n=== Test completed ===")
    
    # Clean up
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    print("Test directory cleaned up.")

if __name__ == "__main__":
    test_pki_network()