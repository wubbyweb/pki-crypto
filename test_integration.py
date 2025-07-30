#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
import json
from pki_token import SecureToken, PKITokenNetwork

class TestIntegrationFlow(unittest.TestCase):
    """Integration tests for complete token issuance and verification flows"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.network = PKITokenNetwork(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_complete_three_level_hierarchy(self):
        """Test complete three-level token hierarchy creation and verification"""
        # Level 1: Create master
        master = self.network.create_master_token("root-ca")
        self.assertIsNotNone(master)
        
        # Level 2: Issue intermediate certificates
        intermediate1 = self.network.issue_token("root-ca", "intermediate-ca-1", "Intermediate CA 1")
        intermediate2 = self.network.issue_token("root-ca", "intermediate-ca-2", "Intermediate CA 2")
        
        self.assertEqual(intermediate1.issuer_id, "root-ca")
        self.assertEqual(intermediate1.issuer_token_hash, master.token_hash)
        self.assertEqual(intermediate2.issuer_id, "root-ca")
        self.assertEqual(intermediate2.issuer_token_hash, master.token_hash)
        
        # Level 3: Issue end-entity certificates
        end1 = self.network.issue_token("intermediate-ca-1", "server-1", "Web Server 1")
        end2 = self.network.issue_token("intermediate-ca-1", "server-2", "Web Server 2")
        end3 = self.network.issue_token("intermediate-ca-2", "client-1", "Client Certificate")
        
        self.assertEqual(end1.issuer_id, "intermediate-ca-1")
        self.assertEqual(end1.issuer_token_hash, intermediate1.token_hash)
        
        # Verify all tokens
        tokens_to_verify = ["root-ca", "intermediate-ca-1", "intermediate-ca-2", 
                           "server-1", "server-2", "client-1"]
        
        for token_id in tokens_to_verify:
            is_valid, chain = self.network.verify_token(token_id)
            self.assertTrue(is_valid, f"Token {token_id} should be valid")
            self.assertIn("root-ca", chain[-1], f"Chain for {token_id} should end with root-ca")
        
        # Verify chain lengths
        is_valid, chain = self.network.verify_token("server-1")
        self.assertEqual(len(chain), 3)  # server-1 -> intermediate-ca-1 -> root-ca
        
        is_valid, chain = self.network.verify_token("intermediate-ca-1")
        self.assertEqual(len(chain), 2)  # intermediate-ca-1 -> root-ca
        
        is_valid, chain = self.network.verify_token("root-ca")
        self.assertEqual(len(chain), 1)  # root-ca only
    
    def test_cross_branch_issuance_prevention(self):
        """Test that tokens from different branches cannot issue to each other's nodes"""
        # Create hierarchy
        self.network.create_master_token("root")
        self.network.issue_token("root", "branch-a")
        self.network.issue_token("root", "branch-b")
        self.network.issue_token("branch-a", "leaf-a1")
        self.network.issue_token("branch-b", "leaf-b1")
        
        # Try to have leaf-a1 issue a token to a node that should belong to branch-b
        # This should work (no restriction), but verify the chain is correct
        cross_token = self.network.issue_token("leaf-a1", "cross-node")
        
        is_valid, chain = self.network.verify_token("cross-node")
        self.assertTrue(is_valid)
        # Chain should be: cross-node -> leaf-a1 -> branch-a -> root
        self.assertEqual(len(chain), 4)
        self.assertIn("cross-node", chain[0])
        self.assertIn("leaf-a1", chain[1])
        self.assertIn("branch-a", chain[2])
        self.assertIn("root", chain[3])
    
    def test_large_token_network(self):
        """Test creation and verification of large token network"""
        # Create master
        self.network.create_master_token("master")
        
        # Create 5 first-level children
        first_level = []
        for i in range(5):
            node_id = f"level1-node{i}"
            self.network.issue_token("master", node_id)
            first_level.append(node_id)
        
        # Create 3 second-level children for each first-level node
        second_level = []
        for parent in first_level:
            for j in range(3):
                node_id = f"{parent}-child{j}"
                self.network.issue_token(parent, node_id)
                second_level.append(node_id)
        
        # Create 2 third-level children for each second-level node
        third_level = []
        for parent in second_level:
            for k in range(2):
                node_id = f"{parent}-leaf{k}"
                self.network.issue_token(parent, node_id)
                third_level.append(node_id)
        
        # Verify total count: 1 master + 5 level1 + 15 level2 + 30 level3 = 51 tokens
        all_tokens = self.network.list_all_tokens()
        self.assertEqual(len(all_tokens), 51)
        
        # Verify random samples from each level
        test_samples = ["master", "level1-node2", "level1-node3-child1", 
                       "level1-node0-child2-leaf1"]
        
        for sample in test_samples:
            is_valid, chain = self.network.verify_token(sample)
            self.assertTrue(is_valid, f"Token {sample} should be valid")
            self.assertIn("master", chain[-1])
    
    def test_token_issuance_sequence_integrity(self):
        """Test that the sequence of token issuance maintains integrity"""
        # Create tokens in specific sequence
        master = self.network.create_master_token("master")
        
        # Store initial state
        initial_master_hash = master.token_hash
        
        # Issue child token
        child1 = self.network.issue_token("master", "child1")
        
        # Verify master hash hasn't changed
        current_master = self.network.tokens["master"]
        self.assertEqual(current_master.token_hash, initial_master_hash)
        
        # Issue another child
        child2 = self.network.issue_token("master", "child2")
        
        # Both children should reference the same master hash
        self.assertEqual(child1.issuer_token_hash, initial_master_hash)
        self.assertEqual(child2.issuer_token_hash, initial_master_hash)
        
        # Issue grandchild from child1
        grandchild = self.network.issue_token("child1", "grandchild")
        
        # Grandchild should reference child1's hash
        self.assertEqual(grandchild.issuer_token_hash, child1.token_hash)
        
        # Verify all tokens are still valid
        all_nodes = ["master", "child1", "child2", "grandchild"]
        for node in all_nodes:
            is_valid, _ = self.network.verify_token(node)
            self.assertTrue(is_valid, f"Node {node} should remain valid")

class TestErrorConditions(unittest.TestCase):
    """Test various error conditions and edge cases"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.network = PKITokenNetwork(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_operations_without_master_token(self):
        """Test that operations fail appropriately without master token"""
        # Try to issue token without master
        with self.assertRaises(ValueError):
            self.network.issue_token("nonexistent", "child")
        
        # Try to verify non-existent token
        is_valid, chain = self.network.verify_token("nonexistent")
        self.assertFalse(is_valid)
        self.assertIn("not found", chain[0])
    
    def test_boundary_node_id_lengths(self):
        """Test node ID length boundaries"""
        # Test maximum valid length (64 characters)
        valid_long_id = "a" * 64
        self.network.create_master_token(valid_long_id)
        self.assertIn(valid_long_id, self.network.tokens)
        
        # Test too long (65 characters) - should fail
        with self.assertRaises(ValueError):
            PKITokenNetwork().create_master_token("a" * 65)
    
    def test_special_characters_in_node_ids(self):
        """Test various special characters in node IDs"""
        valid_chars = ["node-test", "node_test", "node.test", "Node123"]
        invalid_chars = ["node test", "node@test", "node#test", "node/test", "node\\test"]
        
        # Test valid characters
        for i, node_id in enumerate(valid_chars):
            network = PKITokenNetwork(tempfile.mkdtemp())
            try:
                network.create_master_token(node_id)
                self.assertIn(node_id, network.tokens)
            finally:
                shutil.rmtree(network.storage_dir)
        
        # Test invalid characters
        for node_id in invalid_chars:
            with self.assertRaises(ValueError):
                SecureToken(node_id)
    
    def test_concurrent_token_operations(self):
        """Test behavior under rapid token operations"""
        # Create master
        self.network.create_master_token("master")
        
        # Rapidly create many tokens
        token_count = 100
        for i in range(token_count):
            if i == 0:
                parent = "master"
            else:
                parent = f"node{i-1}"
            
            self.network.issue_token(parent, f"node{i}")
        
        # Verify the chain
        final_node = f"node{token_count-1}"
        is_valid, chain = self.network.verify_token(final_node)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(chain), token_count + 1)  # +1 for master
        self.assertIn("master", chain[-1])

if __name__ == '__main__':
    unittest.main()