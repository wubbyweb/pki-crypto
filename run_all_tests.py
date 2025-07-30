#!/usr/bin/env python3

import unittest
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all test suites and generate comprehensive coverage report"""
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See details above'}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'See details above'}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED! 🎉")
    else:
        print("❌ Some tests failed. See details above.")
    
    return result.wasSuccessful()

def list_test_modules():
    """List all test modules and their test counts"""
    print("Test Modules and Coverage:")
    print("-" * 50)
    
    test_modules = [
        ('test_secure_token.py', 'SecureToken class unit tests'),
        ('test_pki_network.py', 'PKITokenNetwork class and verification tests'),
        ('test_integration.py', 'Integration tests for complete workflows'),
        ('test_cli.py', 'Command line interface tests'),
        ('test_persistence.py', 'Data persistence and storage tests'),
        ('test_security.py', 'Security and tamper detection tests'),
    ]
    
    total_tests = 0
    for module, description in test_modules:
        if os.path.exists(module):
            # Count tests in module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(module[:-3])  # Remove .py extension
            test_count = suite.countTestCases()
            total_tests += test_count
            print(f"{module:25} {test_count:3d} tests - {description}")
        else:
            print(f"{module:25}   - tests - {description} (FILE NOT FOUND)")
    
    print("-" * 50)
    print(f"{'TOTAL':25} {total_tests:3d} tests")
    print()

if __name__ == '__main__':
    print("PKI Token Network - Comprehensive Test Suite")
    print("=" * 70)
    
    list_test_modules()
    
    success = run_all_tests()
    
    if success:
        print("\n✅ TDD Implementation Complete - All Tests Pass!")
        print("\nTest Coverage Areas:")
        print("- Unit tests for core classes")
        print("- Integration tests for complete workflows")
        print("- Error handling and edge cases")
        print("- CLI interface functionality")
        print("- Data persistence and storage")
        print("- Security and tamper detection")
        print("- Input validation and sanitization")
        print("- Hash chain integrity verification")
    else:
        print("\n❌ TDD Implementation needs attention - Some tests failed")
        sys.exit(1)