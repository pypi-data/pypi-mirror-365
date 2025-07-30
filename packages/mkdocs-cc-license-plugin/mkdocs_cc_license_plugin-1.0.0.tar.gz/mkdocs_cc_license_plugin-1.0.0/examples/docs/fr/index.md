---
title: Accueil
description: Page d'accueil de l'exemple
---

# Plugin MkDocs Creative Commons License - Exemple

Bienvenue dans l'exemple d'utilisation du plugin **mkdocs-cc-license-plugin** !

## Fonctionnalités démontrées

Ce site d'exemple montre comment le plugin gère automatiquement les licences Creative Commons :

### 1. Pages avec licence personnalisée
- Voir la page [Avec licence](with-license.md) qui spécifie `license: "by-nc-sa"`
- Les icônes CC appropriées sont automatiquement générées

### 2. Pages sans licence spécifiée  
- Voir la page [Sans licence](no-license.md) qui utilise la licence par défaut
- La licence par défaut `by-sa` est appliquée automatiquement

### 3. Affichage des licences

Les licences apparaissent sous forme d'icônes SVG avec lien vers la page officielle Creative Commons.

## Configuration actuelle

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"
      language: "fr"
      target_blank: true
      show_icons: true
```

## Licence de cette page

Cette page utilise la licence par défaut : {{ cc_license(page.meta) }}

---

*Cet exemple démontre l'utilisation du plugin mkdocs-cc-license-plugin*
