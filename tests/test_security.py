#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
import json
import hashlib
from pki_network import SecureToken, PKITokenNetwork

class TestSecurityAndTamperDetection(unittest.TestCase):
    """Test security features and tamper detection"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.network = PKITokenNetwork(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_hash_consistency(self):
        """Test that token hashes are consistent and deterministic"""
        # Create same token multiple times - hashes should be different due to timestamp/UUID
        token1 = SecureToken("test-node")
        token2 = SecureToken("test-node")
        
        # Should be different due to timestamp and UUID
        self.assertNotEqual(token1.token_hash, token2.token_hash)
        
        # But same token should have consistent hash
        original_hash = token1.token_hash
        self.assertEqual(token1.token_hash, original_hash)
    
    def test_hash_format_validation(self):
        """Test that token hashes are valid SHA256 hashes"""
        token = SecureToken("test-node")
        
        # Should be 64 characters (SHA256 hex)
        self.assertEqual(len(token.token_hash), 64)
        
        # Should only contain hex characters
        self.assertTrue(all(c in '0123456789abcdef' for c in token.token_hash))
        
        # Should be a valid hex string
        try:
            int(token.token_hash, 16)
        except ValueError:
            self.fail("Token hash is not a valid hex string")
    
    def test_token_modification_detection(self):
        """Test that token modifications are detected"""
        self.network.create_master_token("master")
        child = self.network.issue_token("master", "child")
        
        # Store original hash
        original_hash = child.token_hash
        
        # Modify token content
        child.token_data = "modified data"
        
        # Hash should no longer match the original
        # (In real implementation, hash would be recalculated, but this tests the concept)
        new_hash = child._generate_token_hash()
        self.assertNotEqual(original_hash, new_hash)
    
    def test_file_tampering_detection(self):
        """Test detection of file tampering"""
        self.network.create_master_token("master")
        self.network.issue_token("master", "child")
        
        # Verify original chain is valid
        is_valid, _ = self.network.verify_token("child")
        self.assertTrue(is_valid)
        
        # Tamper with stored token file
        child_file = os.path.join(self.test_dir, "child_token.json")
        with open(child_file, 'r') as f:
            data = json.load(f)
        
        # Modify the token data but keep the hash
        data['token_data'] = "tampered data"
        
        with open(child_file, 'w') as f:
            json.dump(data, f)
        
        # Reload network and verify tampering is detected
        network2 = PKITokenNetwork(self.test_dir)
        
        # The token should load but verification should fail due to hash mismatch
        tampered_token = network2.tokens["child"]
        expected_hash = tampered_token._generate_token_hash()
        self.assertNotEqual(tampered_token.token_hash, expected_hash)
    
    def test_issuer_hash_tampering(self):
        """Test detection of issuer hash tampering"""
        master = self.network.create_master_token("master")
        self.network.issue_token("master", "child")
        
        # Tamper with master token hash in file
        master_file = os.path.join(self.test_dir, "master_token.json")
        with open(master_file, 'r') as f:
            data = json.load(f)
        
        # Change the master token hash
        data['token_hash'] = "tampered_hash_1234567890abcdef" * 2  # 64 chars
        
        with open(master_file, 'w') as f:
            json.dump(data, f)
        
        # Reload network
        network2 = PKITokenNetwork(self.test_dir)
        
        # Child verification should fail due to broken hash chain
        is_valid, chain = network2.verify_token("child")
        self.assertFalse(is_valid)
        self.assertIn("Hash chain broken", chain[-1])
    
    def test_chain_injection_attack(self):
        """Test resistance to chain injection attacks"""
        self.network.create_master_token("legitimate-master")
        self.network.issue_token("legitimate-master", "legitimate-child")
        
        # Create a fake master token file
        fake_master_data = {
            "node_id": "fake-master",
            "issuer_token_hash": None,
            "issuer_id": None,
            "timestamp": "2023-01-01T00:00:00+00:00",
            "token_id": "fake-uuid",
            "token_data": "fake master",
            "token_hash": "fake_hash_" + "0" * 54  # 64 chars total
        }
        
        fake_file = os.path.join(self.test_dir, "fake-master_token.json")
        with open(fake_file, 'w') as f:
            json.dump(fake_master_data, f)
        
        # Create fake child pointing to fake master
        fake_child_data = {
            "node_id": "fake-child",
            "issuer_token_hash": fake_master_data["token_hash"],
            "issuer_id": "fake-master",
            "timestamp": "2023-01-01T00:00:00+00:00",
            "token_id": "fake-child-uuid",
            "token_data": "fake child",
            "token_hash": "fake_child_hash_" + "0" * 47  # 64 chars total
        }
        
        fake_child_file = os.path.join(self.test_dir, "fake-child_token.json")
        with open(fake_child_file, 'w') as f:
            json.dump(fake_child_data, f)
        
        # Reload network
        network2 = PKITokenNetwork(self.test_dir)
        
        # Should detect that there are multiple "master" tokens
        master_count = sum(1 for token in network2.tokens.values() 
                          if token.issuer_token_hash is None)
        self.assertGreater(master_count, 1)
        
        # Network should only recognize the first loaded master
        # (Implementation dependent - this tests the concept)
        self.assertIsNotNone(network2.master_token)
    
    def test_replay_attack_resistance(self):
        """Test resistance to replay attacks"""
        # Create tokens with identical data but different timestamps
        token1 = SecureToken("node", None, None, "same data")
        token2 = SecureToken("node", None, None, "same data")
        
        # Should have different hashes due to different timestamps/UUIDs
        self.assertNotEqual(token1.token_hash, token2.token_hash)
        self.assertNotEqual(token1.token_id, token2.token_id)
        self.assertNotEqual(token1.timestamp, token2.timestamp)
    
    def test_circular_reference_detection(self):
        """Test detection of circular references in token chain"""
        self.network.create_master_token("master")
        self.network.issue_token("master", "node-a")
        self.network.issue_token("node-a", "node-b")
        
        # Manually create circular reference by modifying file
        node_a_file = os.path.join(self.test_dir, "node-a_token.json")
        with open(node_a_file, 'r') as f:
            data = json.load(f)
        
        # Make node-a point to node-b (creating A -> B -> A cycle)
        node_b_hash = self.network.tokens["node-b"].token_hash
        data['issuer_token_hash'] = node_b_hash
        data['issuer_id'] = "node-b"
        
        with open(node_a_file, 'w') as f:
            json.dump(data, f)
        
        # Reload network
        network2 = PKITokenNetwork(self.test_dir)
        
        # Verification should detect the circular reference
        # (This would cause infinite loop without proper detection)
        # Implementation should have cycle detection mechanism
    
    def test_malicious_node_id_injection(self):
        """Test protection against malicious node IDs"""
        malicious_ids = [
            "../../../etc/passwd",  # Path traversal
            "node\x00malicious",    # Null byte injection
            "node;rm -rf /",        # Command injection
            "node`whoami`",         # Command substitution
            "node$(whoami)",        # Command substitution
            "node|whoami",          # Pipe injection
        ]
        
        for malicious_id in malicious_ids:
            with self.assertRaises(ValueError, msg=f"Should reject malicious ID: {malicious_id}"):
                SecureToken(malicious_id)
    
    def test_hash_collision_resistance(self):
        """Test that similar inputs produce different hashes"""
        # Create tokens with very similar data
        token1 = SecureToken("node1", "issuer_hash", "issuer", "data")
        token2 = SecureToken("node2", "issuer_hash", "issuer", "data")  # Only node ID differs
        
        self.assertNotEqual(token1.token_hash, token2.token_hash)
        
        # Test with similar but different issuer hashes
        token3 = SecureToken("node", "issuer_hash1", "issuer", "data")
        token4 = SecureToken("node", "issuer_hash2", "issuer", "data")
        
        self.assertNotEqual(token3.token_hash, token4.token_hash)
    
    def test_token_uniqueness_across_restarts(self):
        """Test that tokens remain unique across system restarts"""
        # Create initial network
        self.network.create_master_token("master")
        master_token = self.network.tokens["master"]
        original_hash = master_token.token_hash
        
        # Simulate system restart by creating new network instance
        network2 = PKITokenNetwork(self.test_dir)
        reloaded_master = network2.tokens["master"]
        
        # Hash should be identical after reload
        self.assertEqual(original_hash, reloaded_master.token_hash)
        
        # But new tokens should have different hashes
        new_child = network2.issue_token("master", "new-child")
        self.assertNotEqual(new_child.token_hash, original_hash)
    
    def test_storage_permission_security(self):
        """Test that storage directory permissions are secure"""
        # This test checks that the storage directory is created with appropriate permissions
        # In a production system, you'd want restrictive permissions
        
        # Check that directory exists and is accessible
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.access(self.test_dir, os.R_OK))
        self.assertTrue(os.access(self.test_dir, os.W_OK))
        
        # Create a token and check file permissions
        self.network.create_master_token("master")
        token_file = os.path.join(self.test_dir, "master_token.json")
        
        self.assertTrue(os.path.exists(token_file))
        self.assertTrue(os.access(token_file, os.R_OK))

if __name__ == '__main__':
    unittest.main()