#!/bin/bash

# Script de publication sur PyPI
# Usage: ./publish.sh

echo "🚀 Publication du plugin mkdocs-cc-license-plugin..."

# Vérification des prérequis
echo "Vérification des prérequis..."
python3 -c "import twine, build" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installation des outils de publication..."
    pip install build twine
fi

# Nettoyage des builds précédents
echo "Nettoyage des builds précédents..."
rm -rf build/ dist/ *.egg-info/

# Construction du package
echo "Construction du package..."
python3 -m build

# Vérification du package
echo "Vérification du package..."
python3 -m twine check dist/*

echo "✅ Package construit et vérifié avec succès !"
echo ""
echo "Fichiers générés dans dist/ :"
ls -la dist/

echo ""
echo "Pour publier sur PyPI :"
echo "  1. Test PyPI : twine upload --repository testpypi dist/*"
echo "  2. PyPI prod : twine upload dist/*"
echo ""
read -p "Voulez-vous publier sur Test PyPI maintenant ? (y/N): " upload
if [[ "$upload" =~ ^[Yy]$ ]]; then
    echo "Publication sur Test PyPI..."
    python3 -m twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Publié sur Test PyPI !"
    echo "Testez avec : pip install --index-url https://test.pypi.org/simple/ mkdocs-cc-license-plugin"
fi

echo ""
echo "Publication terminée ! 🎉"
