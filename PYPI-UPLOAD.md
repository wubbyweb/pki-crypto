# PyPI Upload Instructions

This guide explains how to prepare and upload the PKI Token Network package to PyPI.

## Prerequisites

### 1. Install Build Tools
```bash
pip install --upgrade pip setuptools wheel twine build
```

### 2. Create PyPI Account
- Create account at [PyPI](https://pypi.org/account/register/)
- Create account at [TestPyPI](https://test.pypi.org/account/register/) for testing
- Generate API tokens for both accounts

### 3. Configure PyPI Credentials
Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Package Preparation

### 1. Update Package Information
Edit the following files with your details:

**setup.py & pyproject.toml:**
- Change `author` and `author_email`
- Update `url` to your GitHub repository
- Update project URLs

**pki_token_network/__init__.py:**
- Update `__author__` and `__email__`

### 2. Version Management
Update version in:
- `setup.py` (line 19)
- `pyproject.toml` (line 6) 
- `pki_token_network/__init__.py` (line 9)
- `CHANGELOG.md` (add new version entry)

### 3. Pre-upload Checklist
- [ ] All tests pass: `python3 tests/run_all_tests.py`
- [ ] Documentation is complete and accurate
- [ ] LICENSE file is present
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are consistent
- [ ] Author information is correct
- [ ] GitHub repository URL is correct

## Build and Upload Process

### Step 1: Clean Previous Builds
```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/
```

### Step 2: Build the Package
```bash
# Build using modern build tool
python -m build

# Alternative: Build using setup.py
python setup.py sdist bdist_wheel
```

This creates:
- `dist/pki-token-network-1.0.0.tar.gz` (source distribution)
- `dist/pki_token_network-1.0.0-py3-none-any.whl` (wheel distribution)

### Step 3: Test the Build
```bash
# Check the package
twine check dist/*

# Test installation locally
pip install dist/pki_token_network-1.0.0-py3-none-any.whl
```

### Step 4: Upload to TestPyPI (Recommended First)
```bash
# Upload to TestPyPI for testing
twine upload --repository testpypi dist/*
```

### Step 5: Test Installation from TestPyPI
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pki-token-network

# Test the installation
pki-cli --help
token-manager --version
```

### Step 6: Upload to Production PyPI
```bash
# Upload to production PyPI
twine upload dist/*
```

## Post-Upload Verification

### 1. Verify Package Page
- Check package page at https://pypi.org/project/pki-token-network/
- Verify description, documentation, and metadata

### 2. Test Installation
```bash
# Install from PyPI
pip install pki-token-network

# Test console scripts
pki-cli --help
token-manager
```

### 3. Test Import
```python
import pki_token_network
from pki_token_network import PKITokenNetwork, create_secure_token_package

print(pki_token_network.__version__)
```

## Automation Scripts

### Build Script (build.sh)
```bash
#!/bin/bash
set -e

echo "🔨 Building PKI Token Network package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Run tests
echo "🧪 Running tests..."
python3 tests/run_all_tests.py

# Build package
echo "📦 Building package..."
python -m build

# Check package
echo "🔍 Checking package..."
twine check dist/*

echo "✅ Build complete! Files ready in dist/"
ls -la dist/
```

### Upload Script (upload.sh)
```bash
#!/bin/bash
set -e

echo "🚀 Uploading PKI Token Network to PyPI..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ No dist directory found. Run build.sh first."
    exit 1
fi

# Upload to TestPyPI first
echo "📤 Uploading to TestPyPI..."
twine upload --repository testpypi dist/*

echo "🧪 Test installation with:"
echo "pip install --index-url https://test.pypi.org/simple/ pki-token-network"
echo ""
echo "If testing passes, upload to production PyPI with:"
echo "twine upload dist/*"
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError during build**
   - Ensure all imports use relative imports in package modules
   - Check that `__init__.py` files are present

2. **Twine upload fails**
   - Verify PyPI credentials in `~/.pypirc`
   - Check API token permissions
   - Ensure package name is available

3. **Console scripts don't work**
   - Verify entry points in `setup.py`
   - Check that main functions exist in target modules
   - Test with `pip install -e .` first

4. **Package metadata issues**
   - Ensure `README.md` exists and is valid markdown
   - Check that all URLs are accessible
   - Verify classifiers are valid PyPI trove classifiers

### Version Updates

For subsequent releases:
1. Update version in all files
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.0.1`
4. Push tag: `git push origin v1.0.1`
5. Build and upload new version

## Security Notes

- Never commit API tokens to git
- Use environment variables for sensitive data
- Regularly rotate API tokens
- Keep private keys out of the package
- Review package contents before upload

## Support

For issues with the package or upload process:
- Check [PyPI Help](https://pypi.org/help/)
- Review [Python Packaging Guide](https://packaging.python.org/)
- File issues at your project repository