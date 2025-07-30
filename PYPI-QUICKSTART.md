# PyPI Quick Start Guide

## 🚀 Upload to PyPI in 5 Steps

### Step 1: Install Build Tools
```bash
pip install --upgrade pip setuptools wheel twine build
```

### Step 2: Update Package Details
Edit these files with your information:
- `setup.py` - Update author, email, URL
- `pyproject.toml` - Update author, email, URL  
- `pki_token_network/__init__.py` - Update author, email

### Step 3: Build Package
```bash
# Run the build script
./build.sh

# Or manually:
rm -rf build/ dist/ *.egg-info/
python -m build
twine check dist/*
```

### Step 4: Configure PyPI Credentials
Create `~/.pypirc`:
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

### Step 5: Upload Package
```bash
# Use the upload script
./upload.sh

# Or manually:
# Test upload first
twine upload --repository testpypi dist/*

# Then production upload
twine upload dist/*
```

## 📋 Required Files Checklist

All these files are already created:

- ✅ `setup.py` - Package configuration
- ✅ `pyproject.toml` - Modern Python packaging
- ✅ `MANIFEST.in` - File inclusion rules
- ✅ `LICENSE` - MIT License
- ✅ `CHANGELOG.md` - Version history
- ✅ `README.md` - Project documentation
- ✅ `requirements.txt` - Dependencies
- ✅ `pki_token_network/` - Package directory
- ✅ `.gitignore` - Git ignore rules
- ✅ `build.sh` - Build automation
- ✅ `upload.sh` - Upload automation

## 🧪 Test Installation

After upload, test with:
```bash
# Install from PyPI
pip install pki-token-network

# Test console commands
pki-cli --help
token-manager

# Test Python import
python -c "import pki_token_network; print(pki_token_network.__version__)"
```

## 📦 Package Contents

The package will include:
- Core PKI network implementation
- Command-line interface (`pki-cli`)
- Interactive token manager (`token-manager`)
- Secure token packager (`token-packager`)
- Complete documentation
- Test suite

## 🔗 Useful Links

- [PyPI Account](https://pypi.org/account/register/)
- [TestPyPI Account](https://test.pypi.org/account/register/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

## ⚠️ Important Notes

1. **Test First**: Always upload to TestPyPI before production
2. **Version Control**: Update version numbers in all files
3. **Security**: Never commit API tokens to git
4. **Documentation**: Ensure README.md displays correctly on PyPI
5. **Dependencies**: Verify all requirements are in requirements.txt

## 🎉 You're Ready!

Your PKI Token Network package is ready for PyPI upload. Run `./build.sh` to get started!