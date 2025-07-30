#!/usr/bin/env python3
"""
Entry point scripts for PKI Token Network console commands
"""

def pki_cli_main():
    """Entry point for pki-cli command"""
    from .cli import main
    main()

def token_manager_main():
    """Entry point for token-manager command"""
    from .manager import main
    main()

def token_packager_main():
    """Entry point for token-packager command"""
    from .packager import main
    if hasattr(main, '__call__'):
        main()
    else:
        print("Token packager is a library module. Use 'from pki_token_network import create_secure_token_package'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'cli':
            pki_cli_main()
        elif sys.argv[1] == 'manager':
            token_manager_main()
        elif sys.argv[1] == 'packager':
            token_packager_main()
        else:
            print("Usage: python -m pki_token_network.scripts [cli|manager|packager]")
    else:
        print("PKI Token Network - Available commands: cli, manager, packager")