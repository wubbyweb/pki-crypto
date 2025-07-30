#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
import json
from pki_network import SecureToken, PKITokenNetwork

class TestPersistence(unittest.TestCase):
    """Test data persistence and storage functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_token_file_creation(self):
        """Test that token files are created correctly"""
        network = PKITokenNetwork(self.test_dir)
        master = network.create_master_token("master-node")
        
        # Check that file was created
        expected_file = os.path.join(self.test_dir, "master-node_token.json")
        self.assertTrue(os.path.exists(expected_file))
        
        # Verify file contents
        with open(expected_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['node_id'], "master-node")
        self.assertEqual(data['token_hash'], master.token_hash)
        self.assertIsNone(data['issuer_token_hash'])
    
    def test_token_file_loading(self):
        """Test that token files are loaded correctly on startup"""
        # Create network and tokens
        network1 = PKITokenNetwork(self.test_dir)
        master = network1.create_master_token("master")
        child = network1.issue_token("master", "child", "child data")
        
        # Create new network instance to test loading
        network2 = PKITokenNetwork(self.test_dir)
        
        # Verify tokens were loaded
        self.assertEqual(len(network2.tokens), 2)
        self.assertIn("master", network2.tokens)
        self.assertIn("child", network2.tokens)
        self.assertIsNotNone(network2.master_token)
        self.assertEqual(network2.master_token.node_id, "master")
        
        # Verify token data integrity
        loaded_child = network2.tokens["child"]
        self.assertEqual(loaded_child.token_data, "child data")
        self.assertEqual(loaded_child.issuer_id, "master")
        self.assertEqual(loaded_child.issuer_token_hash, master.token_hash)
    
    def test_persistence_across_sessions(self):
        """Test token persistence across multiple sessions"""
        # Session 1: Create hierarchy
        network1 = PKITokenNetwork(self.test_dir)
        network1.create_master_token("root")
        network1.issue_token("root", "branch1")
        network1.issue_token("root", "branch2")
        network1.issue_token("branch1", "leaf1")
        
        # Session 2: Load and extend hierarchy
        network2 = PKITokenNetwork(self.test_dir)
        network2.issue_token("branch2", "leaf2")
        network2.issue_token("leaf1", "leaf1-child")
        
        # Session 3: Verify complete hierarchy
        network3 = PKITokenNetwork(self.test_dir)
        
        expected_nodes = ["root", "branch1", "branch2", "leaf1", "leaf2", "leaf1-child"]
        for node in expected_nodes:
            self.assertIn(node, network3.tokens)
            is_valid, _ = network3.verify_token(node)
            self.assertTrue(is_valid, f"Node {node} should be valid")
    
    def test_corrupted_token_file_handling(self):
        """Test handling of corrupted token files"""
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        
        # Corrupt a token file
        token_file = os.path.join(self.test_dir, "master_token.json")
        with open(token_file, 'w') as f:
            f.write("invalid json content")
        
        # Create new network instance - should handle corruption gracefully
        network2 = PKITokenNetwork(self.test_dir)
        
        # Network should start empty due to corruption
        self.assertEqual(len(network2.tokens), 0)
        self.assertIsNone(network2.master_token)
    
    def test_missing_token_file_fields(self):
        """Test handling of token files with missing fields"""
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        
        # Modify token file to remove required field
        token_file = os.path.join(self.test_dir, "master_token.json")
        with open(token_file, 'r') as f:
            data = json.load(f)
        
        # Remove required field
        del data['token_hash']
        
        with open(token_file, 'w') as f:
            json.dump(data, f)
        
        # Should handle missing fields gracefully
        network2 = PKITokenNetwork(self.test_dir)
        self.assertEqual(len(network2.tokens), 0)
    
    def test_empty_storage_directory(self):
        """Test behavior with empty storage directory"""
        # Remove the directory
        shutil.rmtree(self.test_dir)
        
        # Network should create directory and start empty
        network = PKITokenNetwork(self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertEqual(len(network.tokens), 0)
        self.assertIsNone(network.master_token)
    
    def test_non_token_files_in_directory(self):
        """Test that non-token files are ignored"""
        # Create some non-token files
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "readme.txt"), 'w') as f:
            f.write("This is not a token file")
        
        with open(os.path.join(self.test_dir, "config.json"), 'w') as f:
            json.dump({"config": "value"}, f)
        
        # Create network - should ignore non-token files
        network = PKITokenNetwork(self.test_dir)
        self.assertEqual(len(network.tokens), 0)
        
        # Add actual token
        network.create_master_token("master")
        self.assertEqual(len(network.tokens), 1)
    
    def test_concurrent_access_simulation(self):
        """Test simulation of concurrent access to storage"""
        # Create initial network
        network1 = PKITokenNetwork(self.test_dir)
        network1.create_master_token("master")
        
        # Simulate second process accessing same storage
        network2 = PKITokenNetwork(self.test_dir)
        
        # Both should see the master token
        self.assertIn("master", network1.tokens)
        self.assertIn("master", network2.tokens)
        
        # Add token via network1
        network1.issue_token("master", "child1")
        
        # network2 won't see it until reload (expected behavior)
        self.assertNotIn("child1", network2.tokens)
        
        # Create new instance to simulate reload
        network3 = PKITokenNetwork(self.test_dir)
        self.assertIn("child1", network3.tokens)
    
    def test_large_token_network_persistence(self):
        """Test persistence with large number of tokens"""
        network1 = PKITokenNetwork(self.test_dir)
        network1.create_master_token("master")
        
        # Create 100 tokens in a chain
        parent = "master"
        for i in range(100):
            child_id = f"node{i:03d}"
            network1.issue_token(parent, child_id)
            parent = child_id
        
        # Verify file count
        token_files = [f for f in os.listdir(self.test_dir) if f.endswith('_token.json')]
        self.assertEqual(len(token_files), 101)  # 100 + 1 master
        
        # Load in new network instance
        network2 = PKITokenNetwork(self.test_dir)
        self.assertEqual(len(network2.tokens), 101)
        
        # Verify the end of the chain
        is_valid, chain = network2.verify_token("node099")
        self.assertTrue(is_valid)
        self.assertEqual(len(chain), 101)  # Full chain
    
    def test_token_file_format_validation(self):
        """Test validation of token file format"""
        # Create a properly formatted token file manually
        token_data = {
            "node_id": "manual-token",
            "issuer_token_hash": None,
            "issuer_id": None,
            "timestamp": "2023-01-01T00:00:00+00:00",
            "token_id": "manual-uuid-12345",
            "token_data": "manual token data",
            "token_hash": "manual-hash-abcdef123456"
        }
        
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "manual-token_token.json"), 'w') as f:
            json.dump(token_data, f)
        
        # Load network
        network = PKITokenNetwork(self.test_dir)
        
        # Should load the manually created token
        self.assertIn("manual-token", network.tokens)
        loaded_token = network.tokens["manual-token"]
        self.assertEqual(loaded_token.token_data, "manual token data")
        self.assertEqual(loaded_token.token_hash, "manual-hash-abcdef123456")

if __name__ == '__main__':
    unittest.main()