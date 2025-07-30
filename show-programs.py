#!/usr/bin/env python3

print("🔐 PKI Token Network - Program Overview")
print("=" * 60)
print()

programs = [
    ("pki-cli.py", "Command-line interface for PKI operations"),
    ("token-manager.py", "Interactive GUI for PKI management"),
    ("pki-network.py", "Core PKI network implementation"),
    ("token-packager.py", "Secure token distribution packages"),
    ("token-manager-demo.py", "Demonstration of token manager features")
]

print("📋 Main Programs:")
print("-" * 30)
for program, description in programs:
    print(f"  🔧 {program:<22} - {description}")

print()
print("📁 Support Files:")
print("-" * 30)
support_files = [
    ("README.md", "Project documentation"),
    ("HOWTO.md", "Tutorial guide"),
    ("WIZARD_README.md", "Token manager guide"),
    ("requirements.txt", "Python dependencies"),
    ("tests/", "Test suite directory")
]

for file, description in support_files:
    print(f"  📄 {file:<22} - {description}")

print()
print("🚀 Quick Start:")
print("-" * 30)
print("  Interactive Mode:  python3 token-manager.py")
print("  Command Line:      python3 pki-cli.py --help")
print("  Run Tests:         python3 tests/run_all_tests.py")
print()