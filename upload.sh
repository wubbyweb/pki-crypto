#!/bin/bash
set -e

echo "🚀 Uploading PKI Token Network to PyPI..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ No dist directory found. Run ./build.sh first."
    exit 1
fi

# Check if files exist in dist
if [ -z "$(ls -A dist/)" ]; then
    echo "❌ No files in dist directory. Run ./build.sh first."
    exit 1
fi

echo "📤 Files to upload:"
ls -la dist/

# Confirm upload
echo ""
read -p "🤔 Upload to TestPyPI first? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to TestPyPI..."
    twine upload --repository testpypi dist/*
    
    echo "✅ Upload to TestPyPI complete!"
    echo ""
    echo "🧪 Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ pki-token-network"
    echo ""
    echo "🧪 Test the installation:"
    echo "  pki-cli --help"
    echo "  python -c 'import pki_token_network; print(pki_token_network.__version__)'"
    echo ""
    
    read -p "📤 Continue with production PyPI upload? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Uploading to production PyPI..."
        twine upload dist/*
        echo "✅ Upload to PyPI complete!"
        echo ""
        echo "🎉 Package is now available at:"
        echo "  https://pypi.org/project/pki-token-network/"
        echo ""
        echo "📦 Install with:"
        echo "  pip install pki-token-network"
    else
        echo "⏸️  Production upload cancelled."
    fi
else
    echo "📤 Uploading directly to production PyPI..."
    read -p "⚠️  Are you sure? This will publish to production PyPI (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload dist/*
        echo "✅ Upload to PyPI complete!"
        echo ""
        echo "🎉 Package is now available at:"
        echo "  https://pypi.org/project/pki-token-network/"
    else
        echo "⏸️  Upload cancelled."
    fi
fi