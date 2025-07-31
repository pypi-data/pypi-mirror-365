#!/bin/bash

# SPT Neo RAG Client Publishing Script
# This script builds and publishes the Python client package

set -e  # Exit on any error

echo "🔧 Building package..."
python -m build

echo "📦 Package built successfully!"
echo "Files created:"
ls -la dist/

echo ""
echo "🚀 Choose publishing option:"
echo "1. Test on TestPyPI first (recommended)"
echo "2. Publish directly to PyPI"
echo "3. Just build (already done)"

read -p "Enter your choice (1/2/3): " choice

case $choice in
    1)
        echo "📤 Uploading to TestPyPI..."
        echo "Note: You'll need your TestPyPI API token"
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to TestPyPI!"
        echo "🧪 Test installation with:"
        echo "pip install --index-url https://test.pypi.org/simple/ spt-neo-rag-client"
        echo "or"
        echo "uv add --index-url https://test.pypi.org/simple/ spt-neo-rag-client"
        ;;
    2)
        echo "📤 Uploading to PyPI..."
        echo "Note: You'll need your PyPI API token"
        twine upload dist/*
        echo ""
        echo "🎉 Published to PyPI!"
        echo "📦 Install with:"
        echo "pip install spt-neo-rag-client"
        echo "or"
        echo "uv add spt-neo-rag-client"
        ;;
    3)
        echo "✅ Build complete. Run this script again to publish."
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🏁 Done!" 