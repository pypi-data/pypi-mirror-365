#! /bin/bash

# This script is used to publish the xml-analysis-framework to PyPI.
# Clean previous builds to avoid uploading old versions
rm -rf dist/ build/
python -m build
python -m twine upload dist/*
