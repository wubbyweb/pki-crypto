#!/usr/bin/env python3
"""
Check package structure and readiness for PyPI upload
"""

import os
import sys

def check_file_exists(path, description):
    """Check if a file exists and report status"""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (MISSING)")
        return False

def check_directory_exists(path, description):
    """Check if a directory exists and report status"""
    if os.path.isdir(path):
        file_count = len(os.listdir(path))
        print(f"✅ {description}: {path} ({file_count} files)")
        return True
    else:
        print(f"❌ {description}: {path} (MISSING)")
        return False

def main():
    print("🔍 PKI Token Network - Package Structure Check")
    print("=" * 60)
    
    checks_passed = 0
    total_checks = 0
    
    # Core package files
    files_to_check = [
        ("setup.py", "Setup configuration"),
        ("pyproject.toml", "Modern Python packaging"),
        ("LICENSE", "License file"),
        ("README.md", "Main documentation"),
        ("CHANGELOG.md", "Version history"),
        ("requirements.txt", "Dependencies"),
        ("MANIFEST.in", "File inclusion rules"),
        (".gitignore", "Git ignore rules")
    ]
    
    print("\n📄 Required Files:")
    print("-" * 30)
    for file_path, description in files_to_check:
        if check_file_exists(file_path, description):
            checks_passed += 1
        total_checks += 1
    
    # Directories
    directories_to_check = [
        ("pki_token_network", "Python package"),
        ("tests", "Test suite"),
    ]
    
    print("\n📁 Required Directories:")
    print("-" * 30)
    for dir_path, description in directories_to_check:
        if check_directory_exists(dir_path, description):
            checks_passed += 1
        total_checks += 1
    
    # Package modules
    package_files = [
        ("pki_token_network/__init__.py", "Package init"),
        ("pki_token_network/core.py", "Core PKI implementation"),
        ("pki_token_network/cli.py", "CLI module"),
        ("pki_token_network/manager.py", "Token manager"),
        ("pki_token_network/packager.py", "Token packager"),
        ("pki_token_network/scripts.py", "Entry point scripts")
    ]
    
    print("\n🐍 Python Package Modules:")
    print("-" * 30)
    for file_path, description in package_files:
        if check_file_exists(file_path, description):
            checks_passed += 1
        total_checks += 1
    
    # Documentation files
    doc_files = [
        ("HOWTO.md", "Tutorial guide"),
        ("WIZARD_README.md", "Token manager guide"),
        ("PYPI-UPLOAD.md", "PyPI upload instructions"),
        ("PYPI-QUICKSTART.md", "Quick start guide")
    ]
    
    print("\n📚 Documentation:")
    print("-" * 30)
    for file_path, description in doc_files:
        if check_file_exists(file_path, description):
            checks_passed += 1
        total_checks += 1
    
    # Build scripts
    script_files = [
        ("build.sh", "Build script"),
        ("upload.sh", "Upload script")
    ]
    
    print("\n🔧 Build Scripts:")
    print("-" * 30)
    for file_path, description in script_files:
        if check_file_exists(file_path, description):
            checks_passed += 1
        total_checks += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PACKAGE READINESS SUMMARY")
    print("=" * 60)
    
    success_rate = (checks_passed / total_checks) * 100
    print(f"Files/Directories: {checks_passed}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 95:
        print("🎉 PACKAGE READY FOR PYPI!")
        print("\n🚀 Next Steps:")
        print("1. Install build tools: pip install build twine")
        print("2. Update author info in setup.py and pyproject.toml")
        print("3. Run: python -m build")
        print("4. Run: twine upload --repository testpypi dist/*")
        print("5. Test: pip install --index-url https://test.pypi.org/simple/ pki-token-network")
        print("6. Run: twine upload dist/*")
        return True
    elif success_rate >= 80:
        print("⚠️  PACKAGE MOSTLY READY")
        print("   Some optional files missing, but core structure is good")
        return True
    else:
        print("❌ PACKAGE NOT READY")
        print("   Major files/directories missing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)