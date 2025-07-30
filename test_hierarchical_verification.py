#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
from pki_token import PKITokenNetwork, SecureToken

class TestHierarchicalVerification(unittest.TestCase):
    """Test hierarchical verification capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.network = PKITokenNetwork(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_master_direct_verification(self):
        """Test that master can verify any token directly"""
        # Create hierarchy: master -> level1 -> level2 -> level3
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        level2 = self.network.issue_token("level1", "level2")
        level3 = self.network.issue_token("level2", "level3")
        
        # Master should be able to verify all tokens directly
        tokens_to_verify = ["master", "level1", "level2", "level3"]
        
        for token_id in tokens_to_verify:
            is_valid, result = self.network.verify_token_direct_master(token_id)
            self.assertTrue(is_valid, f"Master should be able to verify {token_id}")
            self.assertIn("Master signature verified", result[0])
    
    def test_master_verification_without_intermediates(self):
        """Test master can verify end tokens without intermediate tokens present"""
        # Create full hierarchy
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        level2 = self.network.issue_token("level1", "level2")
        level3 = self.network.issue_token("level2", "level3")
        
        # Create new network with only master and level3 tokens
        isolated_dir = tempfile.mkdtemp()
        try:
            isolated_network = PKITokenNetwork(isolated_dir)
            
            # Copy keys
            isolated_network.master_private_key = self.network.master_private_key
            isolated_network.master_public_key = self.network.master_public_key
            
            # Add only master and level3 tokens
            isolated_network.master_token = master
            isolated_network.tokens["master"] = master
            isolated_network.tokens["level3"] = level3
            
            # Master direct verification should work
            is_valid, result = isolated_network.verify_token_direct_master("level3")
            self.assertTrue(is_valid, "Master should verify level3 without intermediates")
            
            # Chain verification should fail
            is_valid, result = isolated_network.verify_token("level3")
            self.assertFalse(is_valid, "Chain verification should fail without intermediates")
            self.assertIn("not found", result[-1])
            
        finally:
            shutil.rmtree(isolated_dir)
    
    def test_issuer_direct_verification(self):
        """Test that issuers can verify their direct children"""
        # Create hierarchy
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        level2 = self.network.issue_token("level1", "level2")
        
        # Direct issuer verification should work
        is_valid, result = self.network.verify_token_as_issuer("level1", "level2")
        self.assertTrue(is_valid, "Direct issuer should be able to verify child")
        self.assertIn("verified", result[0])
        
        # Indirect issuer verification should work
        is_valid, result = self.network.verify_token_as_issuer("master", "level2")
        self.assertTrue(is_valid, "Indirect issuer should be able to verify descendant")
    
    def test_verification_path_availability(self):
        """Test that tokens have appropriate verification paths"""
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        
        # Master token should have master-direct path
        self.assertIn("master-direct", master.verification_paths)
        
        # Child token should have multiple paths
        self.assertIn("chain", level1.verification_paths)
        self.assertIn("master-direct", level1.verification_paths)
        self.assertIn("issuer-direct", level1.verification_paths)
    
    def test_hybrid_verification(self):
        """Test hybrid verification using all available methods"""
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        
        # Hybrid verification should use all methods
        is_valid, results = self.network.verify_token_hybrid("level1")
        self.assertTrue(is_valid, "Hybrid verification should succeed")
        
        # Should have results for multiple methods
        self.assertIn("chain", results)
        self.assertIn("master-direct", results)
        self.assertIn("issuer-direct", results)
        
        # All methods should succeed for valid token
        for method, (valid, _) in results.items():
            self.assertTrue(valid, f"Method {method} should succeed")
    
    def test_signature_verification_methods(self):
        """Test individual signature verification methods"""
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        
        # Test master signature verification
        self.assertTrue(level1.verify_master_signature(self.network.master_public_key))
        
        # Test issuer signature verification
        if "master" in self.network.node_keys:
            _, master_public_key = self.network.node_keys["master"]
            self.assertTrue(level1.verify_issuer_signature(master_public_key, "master"))
    
    def test_hierarchy_level_tracking(self):
        """Test that hierarchy levels are correctly tracked"""
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        level2 = self.network.issue_token("level1", "level2")
        level3 = self.network.issue_token("level2", "level3")
        
        self.assertEqual(master.hierarchy_level, 0)
        self.assertEqual(level1.hierarchy_level, 1)
        self.assertEqual(level2.hierarchy_level, 2)
        self.assertEqual(level3.hierarchy_level, 3)
    
    def test_master_id_propagation(self):
        """Test that master ID is correctly propagated to all tokens"""
        master = self.network.create_master_token("test-master")
        level1 = self.network.issue_token("test-master", "level1")
        level2 = self.network.issue_token("level1", "level2")
        
        self.assertEqual(level1.master_id, "test-master")
        self.assertEqual(level2.master_id, "test-master")
    
    def test_token_serialization_with_signatures(self):
        """Test that enhanced tokens serialize/deserialize correctly"""
        master = self.network.create_master_token("master")
        level1 = self.network.issue_token("master", "level1")
        
        # Serialize and deserialize
        token_dict = level1.to_dict()
        restored_token = SecureToken.from_dict(token_dict)
        
        # Enhanced fields should be preserved
        self.assertEqual(restored_token.master_signature, level1.master_signature)
        self.assertEqual(restored_token.issuer_signature, level1.issuer_signature)
        self.assertEqual(restored_token.hierarchy_level, level1.hierarchy_level)
        self.assertEqual(restored_token.master_id, level1.master_id)
        self.assertEqual(restored_token.verification_paths, level1.verification_paths)
    
    def test_backward_compatibility(self):
        """Test that system works with legacy tokens without signatures"""
        # Create a legacy-style token dict
        legacy_token_data = {
            'node_id': 'legacy-node',
            'issuer_token_hash': None,
            'issuer_id': None,
            'timestamp': '2023-01-01T00:00:00+00:00',
            'token_id': 'legacy-uuid',
            'token_data': 'legacy token',
            'token_hash': 'legacy-hash'
        }
        
        # Should load without errors
        legacy_token = SecureToken.from_dict(legacy_token_data)
        
        # Should have default values for new fields
        self.assertEqual(legacy_token.verification_paths, {"chain"})
        self.assertIsNone(legacy_token.master_signature)
        self.assertIsNone(legacy_token.issuer_signature)
    
    def test_key_generation_and_persistence(self):
        """Test that keys are generated and persisted correctly"""
        master = self.network.create_master_token("master")
        
        # Keys should be generated
        self.assertIsNotNone(self.network.master_private_key)
        self.assertIsNotNone(self.network.master_public_key)
        
        # Keys should be persisted
        keys_dir = os.path.join(self.test_dir, "keys")
        self.assertTrue(os.path.exists(os.path.join(keys_dir, "master_private.pem")))
        self.assertTrue(os.path.exists(os.path.join(keys_dir, "master_public.pem")))
        
        # Should load keys correctly in new instance
        network2 = PKITokenNetwork(self.test_dir)
        self.assertIsNotNone(network2.master_private_key)
        self.assertIsNotNone(network2.master_public_key)

if __name__ == '__main__':
    unittest.main()