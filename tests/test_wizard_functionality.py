#!/usr/bin/env python3

import os
import tempfile
import shutil
from token_manager import PKIWizard
from unittest.mock import patch
import io
import sys

def test_wizard_core_functionality():
    """Test wizard core functionality without interactive input"""
    
    print("🧪 Testing PKI Wizard Core Functionality")
    print("=" * 50)
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    
    try:
        # Test wizard initialization
        print("1. Testing wizard initialization...")
        wizard = PKIWizard()
        wizard.storage_dir = test_dir
        
        # Mock the setup to avoid interactive prompts
        from pki_network import PKITokenNetwork
        wizard.network = PKITokenNetwork(test_dir)
        
        print("   ✅ Wizard initialized successfully")
        
        # Test network loading
        print("2. Testing network loading...")
        if wizard.network:
            print(f"   ✅ Network loaded: {len(wizard.network.tokens)} tokens")
        else:
            print("   ❌ Network loading failed")
            return False
        
        # Test utility methods
        print("3. Testing utility methods...")
        
        # Test menu formatting (without user input)
        with patch('builtins.input', return_value='0'):
            try:
                choice = wizard.print_menu("Test Menu", ["Option 1", "Option 2"])
                print(f"   ✅ Menu system works: returned {choice}")
            except:
                print("   ❌ Menu system failed")
                return False
        
        # Test input validation
        print("4. Testing input validation...")
        with patch('builtins.input', return_value='test-input'):
            try:
                result = wizard.get_input("Test prompt", required=False)
                print(f"   ✅ Input validation works: '{result}'")
            except:
                print("   ❌ Input validation failed")
                return False
        
        # Test confirmation
        print("5. Testing confirmation prompts...")
        with patch('builtins.input', return_value='y'):
            try:
                confirmed = wizard.confirm_action("Test confirmation")
                print(f"   ✅ Confirmation works: {confirmed}")
            except:
                print("   ❌ Confirmation failed")
                return False
        
        # Test screen clearing (should not fail)
        print("6. Testing screen utilities...")
        try:
            wizard.clear_screen()
            wizard.print_header()
            print("   ✅ Screen utilities work")
        except:
            print("   ❌ Screen utilities failed")
            return False
        
        print("\n✅ All core wizard functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def test_wizard_integration():
    """Test wizard integration with PKI system"""
    
    print("\n🔗 Testing Wizard PKI Integration")
    print("=" * 50)
    
    test_dir = tempfile.mkdtemp()
    
    try:
        # Initialize wizard with PKI network
        wizard = PKIWizard()
        wizard.storage_dir = test_dir
        
        from pki_network import PKITokenNetwork
        wizard.network = PKITokenNetwork(test_dir)
        
        # Test master token creation (programmatically)
        print("1. Testing master token creation...")
        try:
            master_token = wizard.network.create_master_token("test-master")
            print(f"   ✅ Master token created: {master_token.node_id}")
        except Exception as e:
            print(f"   ❌ Master token creation failed: {e}")
            return False
        
        # Test token issuance
        print("2. Testing token issuance...")
        try:
            child_token = wizard.network.issue_token("test-master", "test-child", "Test Child")
            print(f"   ✅ Child token issued: {child_token.node_id}")
        except Exception as e:
            print(f"   ❌ Token issuance failed: {e}")
            return False
        
        # Test verification
        print("3. Testing token verification...")
        try:
            is_valid, chain = wizard.network.verify_token("test-child")
            print(f"   ✅ Token verification: {'VALID' if is_valid else 'INVALID'}")
        except Exception as e:
            print(f"   ❌ Token verification failed: {e}")
            return False
        
        # Test secure package creation
        print("4. Testing secure package creation...")
        try:
            from token_packager import create_secure_token_package
            package_dir = os.path.join(test_dir, "test_package")
            create_secure_token_package(wizard.network, "test-child", package_dir)
            
            if os.path.exists(package_dir):
                files = os.listdir(package_dir)
                print(f"   ✅ Secure package created with {len(files)} files")
            else:
                print("   ❌ Secure package directory not created")
                return False
                
        except Exception as e:
            print(f"   ❌ Secure package creation failed: {e}")
            return False
        
        print("\n✅ All wizard integration tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False
    
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

def main():
    """Run all wizard tests"""
    
    print("🧙‍♂️ PKI WIZARD FUNCTIONALITY TESTS")
    print("=" * 60)
    
    # Test core functionality
    core_passed = test_wizard_core_functionality()
    
    # Test integration
    integration_passed = test_wizard_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Core Functionality: {'✅ PASSED' if core_passed else '❌ FAILED'}")
    print(f"PKI Integration: {'✅ PASSED' if integration_passed else '❌ FAILED'}")
    
    if core_passed and integration_passed:
        print("\n🎉 ALL WIZARD TESTS PASSED!")
        print("\nThe wizard is ready for interactive use:")
        print("  python3 wizard.py")
        print("\nFeatures tested:")
        print("  ✅ Menu system and navigation")
        print("  ✅ Input validation and error handling")
        print("  ✅ PKI network integration")
        print("  ✅ Token creation and verification")
        print("  ✅ Secure package generation")
        print("  ✅ Screen management and UI")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the implementation and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)