#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
import json
from pki_token import SecureToken, PKITokenNetwork

class TestPKITokenNetwork(unittest.TestCase):
    """Unit tests for PKITokenNetwork class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.network = PKITokenNetwork(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_network_initialization(self):
        """Test PKITokenNetwork initialization"""
        self.assertEqual(self.network.storage_dir, self.test_dir)
        self.assertEqual(len(self.network.tokens), 0)
        self.assertIsNone(self.network.master_token)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_create_master_token_success(self):
        """Test successful master token creation"""
        master = self.network.create_master_token("master-node")
        
        self.assertIsNotNone(master)
        self.assertEqual(master.node_id, "master-node")
        self.assertIsNone(master.issuer_token_hash)
        self.assertIsNone(master.issuer_id)
        self.assertEqual(self.network.master_token, master)
        self.assertIn("master-node", self.network.tokens)
    
    def test_create_master_token_duplicate(self):
        """Test that creating duplicate master token fails"""
        self.network.create_master_token("master1")
        
        with self.assertRaises(ValueError) as context:
            self.network.create_master_token("master2")
        self.assertIn("Master token already exists", str(context.exception))
    
    def test_create_master_token_invalid_node_id(self):
        """Test master token creation with invalid node ID"""
        with self.assertRaises(ValueError):
            self.network.create_master_token("invalid@node")
    
    def test_issue_token_success(self):
        """Test successful token issuance"""
        master = self.network.create_master_token("master")
        child = self.network.issue_token("master", "child-node", "child data")
        
        self.assertIsNotNone(child)
        self.assertEqual(child.node_id, "child-node")
        self.assertEqual(child.issuer_id, "master")
        self.assertEqual(child.issuer_token_hash, master.token_hash)
        self.assertEqual(child.token_data, "child data")
        self.assertIn("child-node", self.network.tokens)
    
    def test_issue_token_no_master(self):
        """Test token issuance without master token"""
        with self.assertRaises(ValueError) as context:
            self.network.issue_token("nonexistent", "new-node")
        self.assertIn("No master token exists", str(context.exception))
    
    def test_issue_token_invalid_issuer(self):
        """Test token issuance with invalid issuer"""
        self.network.create_master_token("master")
        
        with self.assertRaises(ValueError) as context:
            self.network.issue_token("nonexistent", "new-node")
        self.assertIn("Issuer node nonexistent not found", str(context.exception))
    
    def test_issue_token_duplicate_node(self):
        """Test token issuance to existing node"""
        self.network.create_master_token("master")
        self.network.issue_token("master", "child")
        
        with self.assertRaises(ValueError) as context:
            self.network.issue_token("master", "child")
        self.assertIn("Node child already has a token", str(context.exception))
    
    def test_issue_token_self_issue(self):
        """Test that node cannot issue token to itself"""
        self.network.create_master_token("master")
        
        with self.assertRaises(ValueError) as context:
            self.network.issue_token("master", "master")
        self.assertIn("Issuer and new node cannot be the same", str(context.exception))
    
    def test_get_token_info_existing(self):
        """Test getting token info for existing token"""
        master = self.network.create_master_token("master")
        info = self.network.get_token_info("master")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['node_id'], "master")
        self.assertEqual(info['token_hash'], master.token_hash)
    
    def test_get_token_info_nonexistent(self):
        """Test getting token info for non-existent token"""
        info = self.network.get_token_info("nonexistent")
        self.assertIsNone(info)
    
    def test_list_all_tokens_empty(self):
        """Test listing tokens when network is empty"""
        tokens = self.network.list_all_tokens()
        self.assertEqual(len(tokens), 0)
    
    def test_list_all_tokens_multiple(self):
        """Test listing multiple tokens"""
        self.network.create_master_token("master")
        self.network.issue_token("master", "child1")
        self.network.issue_token("master", "child2")
        
        tokens = self.network.list_all_tokens()
        self.assertEqual(len(tokens), 3)
        
        node_ids = [token['node_id'] for token in tokens]
        self.assertIn("master", node_ids)
        self.assertIn("child1", node_ids)
        self.assertIn("child2", node_ids)

class TestTokenVerification(unittest.TestCase):
    """Tests for token verification functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.network = PKITokenNetwork(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_verify_master_token(self):
        """Test verification of master token"""
        self.network.create_master_token("master")
        is_valid, chain = self.network.verify_token("master")
        
        self.assertTrue(is_valid)
        self.assertEqual(len(chain), 1)
        self.assertIn("master", chain[0])
    
    def test_verify_child_token(self):
        """Test verification of child token"""
        self.network.create_master_token("master")
        self.network.issue_token("master", "child")
        
        is_valid, chain = self.network.verify_token("child")
        
        self.assertTrue(is_valid)
        self.assertEqual(len(chain), 2)
        self.assertIn("child", chain[0])
        self.assertIn("master", chain[1])
    
    def test_verify_grandchild_token(self):
        """Test verification of grandchild token"""
        self.network.create_master_token("master")
        self.network.issue_token("master", "child")
        self.network.issue_token("child", "grandchild")
        
        is_valid, chain = self.network.verify_token("grandchild")
        
        self.assertTrue(is_valid)
        self.assertEqual(len(chain), 3)
        self.assertIn("grandchild", chain[0])
        self.assertIn("child", chain[1])
        self.assertIn("master", chain[2])
    
    def test_verify_nonexistent_token(self):
        """Test verification of non-existent token"""
        self.network.create_master_token("master")
        is_valid, chain = self.network.verify_token("nonexistent")
        
        self.assertFalse(is_valid)
        self.assertEqual(len(chain), 1)
        self.assertIn("not found", chain[0])
    
    def test_verify_token_missing_issuer(self):
        """Test verification when issuer token is missing"""
        # Create a token manually with non-existent issuer
        self.network.create_master_token("master")
        orphan_token = SecureToken("orphan", "fake-hash", "nonexistent-issuer")
        self.network.tokens["orphan"] = orphan_token
        
        is_valid, chain = self.network.verify_token("orphan")
        
        self.assertFalse(is_valid)
        self.assertIn("Issuer nonexistent-issuer not found", chain[-1])
    
    def test_verify_token_broken_hash_chain(self):
        """Test verification with broken hash chain"""
        self.network.create_master_token("master")
        child = self.network.issue_token("master", "child")
        
        # Manually break the hash chain
        child.issuer_token_hash = "broken-hash"
        
        is_valid, chain = self.network.verify_token("child")
        
        self.assertFalse(is_valid)
        self.assertIn("Hash chain broken", chain[-1])

if __name__ == '__main__':
    unittest.main()