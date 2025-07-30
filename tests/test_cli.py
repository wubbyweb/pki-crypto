#!/usr/bin/env python3

import unittest
import sys
import os
import tempfile
import shutil
import subprocess
import json
from io import StringIO
from unittest.mock import patch, MagicMock

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
cli_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pki-cli.py")
spec = importlib.util.spec_from_file_location("pki_cli", cli_path)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
from pki_network import PKITokenNetwork

class TestCLIFunctions(unittest.TestCase):
    """Test CLI functions directly"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_argv = sys.argv.copy()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        sys.argv = self.original_argv
    
    def test_create_master_success(self):
        """Test create_master function with valid input"""
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.node_id = "test-master"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.create_master(args)
            output = mock_stdout.getvalue()
            
        self.assertIn("Master token created for node: test-master", output)
        self.assertIn("Token hash:", output)
        
        # Verify token was actually created
        network = PKITokenNetwork(self.test_dir)
        self.assertIsNotNone(network.master_token)
        self.assertEqual(network.master_token.node_id, "test-master")
    
    def test_create_master_duplicate(self):
        """Test create_master function with duplicate master"""
        # Create first master
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("existing-master")
        
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.node_id = "new-master"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as context:
                cli.create_master(args)
        
        self.assertEqual(context.exception.code, 1)
    
    def test_issue_token_success(self):
        """Test issue_token function with valid input"""
        # Create master first
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.issuer = "master"
        args.node_id = "child-node"
        args.data = "test data"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.issue_token(args)
            output = mock_stdout.getvalue()
        
        self.assertIn("Token issued to node: child-node", output)
        self.assertIn("Issued by: master", output)
        self.assertIn("Token hash:", output)
        
        # Verify token was created
        network = PKITokenNetwork(self.test_dir)
        self.assertIn("child-node", network.tokens)
    
    def test_issue_token_invalid_issuer(self):
        """Test issue_token function with invalid issuer"""
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.issuer = "nonexistent"
        args.node_id = "child"
        args.data = None
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as context:
                cli.issue_token(args)
        
        self.assertEqual(context.exception.code, 1)
    
    def test_verify_token_valid(self):
        """Test verify_token function with valid token"""
        # Setup network
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        network.issue_token("master", "child")
        
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.node_id = "child"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.verify_token(args)
            output = mock_stdout.getvalue()
        
        self.assertIn("Token verification for node: child", output)
        self.assertIn("Status: VALID", output)
        self.assertIn("Verification chain:", output)
    
    def test_verify_token_invalid(self):
        """Test verify_token function with invalid token"""
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.node_id = "nonexistent"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.verify_token(args)
            output = mock_stdout.getvalue()
        
        self.assertIn("Status: INVALID", output)
    
    def test_show_token_existing(self):
        """Test show_token function with existing token"""
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.node_id = "master"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.show_token(args)
            output = mock_stdout.getvalue()
        
        self.assertIn("Token information for node: master", output)
        self.assertIn('"node_id": "master"', output)
    
    def test_show_token_nonexistent(self):
        """Test show_token function with non-existent token"""
        args = MagicMock()
        args.storage_dir = self.test_dir
        args.node_id = "nonexistent"
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with self.assertRaises(SystemExit) as context:
                cli.show_token(args)
        
        self.assertEqual(context.exception.code, 1)
    
    def test_list_tokens_empty(self):
        """Test list_tokens function with empty network"""
        args = MagicMock()
        args.storage_dir = self.test_dir
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.list_tokens(args)
            output = mock_stdout.getvalue()
        
        self.assertIn("No tokens found in the network", output)
    
    def test_list_tokens_multiple(self):
        """Test list_tokens function with multiple tokens"""
        network = PKITokenNetwork(self.test_dir)
        network.create_master_token("master")
        network.issue_token("master", "child1")
        network.issue_token("master", "child2")
        
        args = MagicMock()
        args.storage_dir = self.test_dir
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.list_tokens(args)
            output = mock_stdout.getvalue()
        
        self.assertIn("Found 3 tokens in the network", output)
        self.assertIn("master", output)
        self.assertIn("child1", output)
        self.assertIn("child2", output)

class TestCLICommandLine(unittest.TestCase):
    """Test CLI through command line interface"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cli_script = "pki-cli.py"
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def run_cli_command(self, args):
        """Helper to run CLI commands"""
        cmd = ["python3", self.cli_script, "--storage-dir", self.test_dir] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        return result
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.run_cli_command(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("PKI Token Network CLI", result.stdout)
        self.assertIn("create-master", result.stdout)
        self.assertIn("issue", result.stdout)
        self.assertIn("verify", result.stdout)
    
    def test_cli_create_master(self):
        """Test CLI create-master command"""
        result = self.run_cli_command(["create-master", "cli-master"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Master token created for node: cli-master", result.stdout)
    
    def test_cli_issue_token(self):
        """Test CLI issue command"""
        # First create master
        self.run_cli_command(["create-master", "master"])
        
        # Then issue token
        result = self.run_cli_command(["issue", "master", "child", "--data", "child data"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Token issued to node: child", result.stdout)
    
    def test_cli_verify_token(self):
        """Test CLI verify command"""
        # Setup tokens
        self.run_cli_command(["create-master", "master"])
        self.run_cli_command(["issue", "master", "child"])
        
        # Verify token
        result = self.run_cli_command(["verify", "child"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Status: VALID", result.stdout)
    
    def test_cli_show_token(self):
        """Test CLI show command"""
        self.run_cli_command(["create-master", "master"])
        
        result = self.run_cli_command(["show", "master"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Token information for node: master", result.stdout)
    
    def test_cli_list_tokens(self):
        """Test CLI list command"""
        self.run_cli_command(["create-master", "master"])
        self.run_cli_command(["issue", "master", "child1"])
        self.run_cli_command(["issue", "master", "child2"])
        
        result = self.run_cli_command(["list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Found 3 tokens in the network", result.stdout)
    
    def test_cli_error_handling(self):
        """Test CLI error handling"""
        # Try to issue without master
        result = self.run_cli_command(["issue", "nonexistent", "child"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stdout)
    
    def test_cli_no_command(self):
        """Test CLI with no command shows help"""
        result = self.run_cli_command([])
        self.assertNotEqual(result.returncode, 0)
    
    def test_cli_custom_storage_dir(self):
        """Test CLI with custom storage directory"""
        custom_dir = tempfile.mkdtemp()
        try:
            cmd = ["python3", self.cli_script, "--storage-dir", custom_dir, "create-master", "test"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
            
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(os.path.join(custom_dir, "test_token.json")))
        finally:
            shutil.rmtree(custom_dir)

if __name__ == '__main__':
    unittest.main()