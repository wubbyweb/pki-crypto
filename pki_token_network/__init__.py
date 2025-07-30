"""
PKI Token Network - A secure blockchain-inspired PKI token system

This package provides a comprehensive PKI token network implementation with
hierarchical verification, cryptographic security, and multiple interfaces.
"""

__version__ = "1.0.0"
__author__ = "PKI Development Team"
__email__ = "developer@example.com"

# Import main classes for easy access
try:
    from .core import PKITokenNetwork, SecureToken
    from .cli import main as cli_main
    from .manager import PKIWizard
    from .packager import create_secure_token_package
except ImportError:
    # Handle import errors gracefully during setup
    pass

__all__ = [
    'PKITokenNetwork',
    'SecureToken', 
    'PKIWizard',
    'create_secure_token_package',
    'cli_main'
]