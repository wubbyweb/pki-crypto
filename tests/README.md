# PKI Token Network - Test Suite

This directory contains all test files for the PKI Token Network system.

## Running Tests

### Run All Tests
```bash
# From project root
python3 tests/run_all_tests.py

# Or from tests directory
cd tests
python3 run_all_tests.py
```

### Run Individual Test Files
```bash
# From project root
python3 -m pytest tests/test_secure_token.py -v
python3 -m pytest tests/test_pki_network.py -v
python3 -m pytest tests/test_integration.py -v
# ... etc
```

## Test Coverage

| Test File | Description | Test Count |
|-----------|-------------|------------|
| `test_secure_token.py` | SecureToken class unit tests | ~15 tests |
| `test_pki_network.py` | PKITokenNetwork class tests | ~20 tests |
| `test_integration.py` | End-to-end integration tests | ~10 tests |
| `test_cli.py` | Command line interface tests | ~8 tests |
| `test_persistence.py` | Data storage and loading tests | ~6 tests |
| `test_security.py` | Security and tamper detection | ~8 tests |
| `test_hierarchical_verification.py` | Verification methods tests | ~15 tests |
| `test_wizard_functionality.py` | Interactive wizard tests | ~5 tests |

## Test Areas Covered

- ✅ **Unit Tests**: Core class functionality
- ✅ **Integration Tests**: Complete workflows
- ✅ **Security Tests**: Tamper detection and validation
- ✅ **CLI Tests**: Command line interface
- ✅ **Persistence Tests**: File storage and loading
- ✅ **Verification Tests**: All verification methods
- ✅ **Error Handling**: Edge cases and invalid inputs
- ✅ **Wizard Tests**: Interactive interface functionality

## Test Dependencies

Tests require the same dependencies as the main system:
- Python 3.6+
- cryptography library

## Test Utilities

- `run_all_tests.py` - Comprehensive test runner with detailed reporting
- `analyze_current_system.py` - System analysis and verification utility