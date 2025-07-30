# Guide de Publication - MkDocs CC License Plugin

## 📋 Prérequis

### 1. Comptes nécessaires
- [x] Compte GitHub (déjà fait)
- [ ] Compte PyPI : https://pypi.org/account/register/
- [ ] Compte Test PyPI : https://test.pypi.org/account/register/

### 2. Outils de publication
```bash
pip install build twine
```

## 🚀 Publication étape par étape

### Étape 1 : Préparation
1. **Vérifiez que tout fonctionne**
   ```bash
   cd examples
   mkdocs serve  # Test local
   ```

2. **Mettez à jour la version** dans `setup.py` si nécessaire

3. **Committez tous les changements**
   ```bash
   git add .
   git commit -m "Prepare for v1.0.0 release"
   git push
   ```

### Étape 2 : Test de publication (recommandé)

1. **Construire et tester sur Test PyPI**
   ```bash
   # Windows
   publish.bat

   # Unix/Linux/Mac
   chmod +x publish.sh
   ./publish.sh
   ```

2. **Tester l'installation depuis Test PyPI**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ mkdocs-cc-license-plugin
   ```

### Étape 3 : Publication sur PyPI production

1. **Publication manuelle**
   ```bash
   # Construction
   python -m build
   
   # Vérification
   twine check dist/*
   
   # Publication
   twine upload dist/*
   ```

2. **Ou avec le script**
   ```bash
   # Puis choisir "N" pour Test PyPI
   # Et utiliser : twine upload dist/*
   ```

### Étape 4 : Publication automatique via GitHub

1. **Créer un token PyPI**
   - Aller sur https://pypi.org/manage/account/token/
   - Créer un token API pour ce projet
   - Copier le token

2. **Ajouter le secret GitHub**
   - Aller sur votre repo GitHub
   - Settings → Secrets and variables → Actions
   - Ajouter `PYPI_API_TOKEN` avec votre token

3. **Créer une release GitHub**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   - Ou créer via l'interface GitHub : Releases → Create a new release

## 📁 Structure finale pour publication

```
mkdocs_cc_license_plugin/
├── mkdocs_cc_license_plugin/
│   ├── __init__.py
│   └── plugin.py
├── examples/
│   ├── docs/
│   │   ├── en/ (anglais)
│   │   └── fr/ (français)
│   ├── mkdocs.yml
│   └── build-multilingual.*
├── tests/
│   └── test_plugin.py
├── .github/workflows/
│   └── publish.yml
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
├── MANIFEST.in
├── publish.bat
├── publish.sh
└── .gitignore
```

## ✅ Checklist avant publication

- [ ] Tous les tests passent
- [ ] Documentation à jour (README.md)
- [ ] Exemples fonctionnels
- [ ] Version mise à jour
- [ ] LICENSE présent
- [ ] MANIFEST.in configuré
- [ ] setup.py complet
- [ ] Scripts de publication testés

## 🎯 Après publication

1. **Vérifier sur PyPI** : https://pypi.org/project/mkdocs-cc-license-plugin/

2. **Tester l'installation**
   ```bash
   pip install mkdocs-cc-license-plugin
   ```

3. **Mettre à jour README.md** avec le badge PyPI

4. **Annoncer sur les communautés**
   - MkDocs Discussions
   - Reddit r/Python
   - Twitter/LinkedIn

## 🔄 Mises à jour futures

Pour les versions suivantes :
1. Modifier la version dans `setup.py`
2. Mettre à jour le changelog
3. Créer une nouvelle release GitHub
4. L'action GitHub publiera automatiquement

## 📞 Support

En cas de problème :
- GitHub Issues : Problèmes techniques
- PyPI Help : Problèmes de publication
- MkDocs Discord : Questions sur l'intégration
