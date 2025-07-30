#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
import json
from datetime import datetime, timezone
from pki_network import SecureToken, PKITokenNetwork

class TestSecureToken(unittest.TestCase):
    """Unit tests for SecureToken class"""
    
    def test_token_creation_with_valid_node_id(self):
        """Test successful token creation with valid node ID"""
        token = SecureToken("test-node")
        self.assertEqual(token.node_id, "test-node")
        self.assertIsNone(token.issuer_token_hash)
        self.assertIsNone(token.issuer_id)
        self.assertIsNotNone(token.timestamp)
        self.assertIsNotNone(token.token_id)
        self.assertIsNotNone(token.token_hash)
        self.assertEqual(token.token_data, "token_for_test-node")
    
    def test_token_creation_with_custom_data(self):
        """Test token creation with custom token data"""
        custom_data = "custom token data"
        token = SecureToken("test-node", token_data=custom_data)
        self.assertEqual(token.token_data, custom_data)
    
    def test_token_creation_with_issuer(self):
        """Test token creation with issuer information"""
        issuer_hash = "abc123def456"
        issuer_id = "issuer-node"
        token = SecureToken("child-node", issuer_hash, issuer_id)
        self.assertEqual(token.issuer_token_hash, issuer_hash)
        self.assertEqual(token.issuer_id, issuer_id)
    
    def test_token_hash_generation(self):
        """Test that token hash is generated correctly"""
        token = SecureToken("test-node")
        self.assertEqual(len(token.token_hash), 64)  # SHA256 hex length
        self.assertTrue(all(c in '0123456789abcdef' for c in token.token_hash))
    
    def test_token_hash_uniqueness(self):
        """Test that different tokens have different hashes"""
        token1 = SecureToken("node1")
        token2 = SecureToken("node2")
        self.assertNotEqual(token1.token_hash, token2.token_hash)
    
    def test_invalid_node_id_empty(self):
        """Test that empty node ID raises ValueError"""
        with self.assertRaises(ValueError) as context:
            SecureToken("")
        self.assertIn("Node ID must be a non-empty string", str(context.exception))
    
    def test_invalid_node_id_none(self):
        """Test that None node ID raises ValueError"""
        with self.assertRaises(ValueError) as context:
            SecureToken(None)
        self.assertIn("Node ID must be a non-empty string", str(context.exception))
    
    def test_invalid_node_id_too_long(self):
        """Test that node ID longer than 64 characters raises ValueError"""
        long_id = "a" * 65
        with self.assertRaises(ValueError) as context:
            SecureToken(long_id)
        self.assertIn("Node ID must be 64 characters or less", str(context.exception))
    
    def test_invalid_node_id_special_characters(self):
        """Test that node ID with invalid characters raises ValueError"""
        invalid_ids = ["node@test", "node#test", "node space", "node/test"]
        for invalid_id in invalid_ids:
            with self.assertRaises(ValueError):
                SecureToken(invalid_id)
    
    def test_valid_node_id_characters(self):
        """Test that node ID with valid characters works"""
        valid_ids = ["node-test", "node_test", "node.test", "Node123", "123node"]
        for valid_id in valid_ids:
            token = SecureToken(valid_id)
            self.assertEqual(token.node_id, valid_id)
    
    def test_to_dict_conversion(self):
        """Test token serialization to dictionary"""
        token = SecureToken("test-node", "issuer-hash", "issuer-id", "test-data")
        token_dict = token.to_dict()
        
        expected_keys = ['node_id', 'issuer_token_hash', 'issuer_id', 'timestamp', 
                        'token_id', 'token_data', 'token_hash', 'master_id', 
                        'hierarchy_level', 'master_signature', 'issuer_signature', 
                        'delegation_proof', 'merkle_proof', 'verification_paths']
        self.assertEqual(set(token_dict.keys()), set(expected_keys))
        self.assertEqual(token_dict['node_id'], "test-node")
        self.assertEqual(token_dict['issuer_token_hash'], "issuer-hash")
        self.assertEqual(token_dict['issuer_id'], "issuer-id")
        self.assertEqual(token_dict['token_data'], "test-data")
    
    def test_from_dict_conversion(self):
        """Test token deserialization from dictionary"""
        original = SecureToken("test-node", "issuer-hash", "issuer-id", "test-data")
        token_dict = original.to_dict()
        
        restored = SecureToken.from_dict(token_dict)
        
        self.assertEqual(restored.node_id, original.node_id)
        self.assertEqual(restored.issuer_token_hash, original.issuer_token_hash)
        self.assertEqual(restored.issuer_id, original.issuer_id)
        self.assertEqual(restored.token_hash, original.token_hash)
        self.assertEqual(restored.token_data, original.token_data)
    
    def test_timestamp_format(self):
        """Test that timestamp is in ISO format"""
        token = SecureToken("test-node")
        # Should not raise exception when parsing
        parsed_time = datetime.fromisoformat(token.timestamp.replace('Z', '+00:00'))
        self.assertIsInstance(parsed_time, datetime)

if __name__ == '__main__':
    unittest.main()