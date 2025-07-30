---
title: Page sans licence spécifiée
author: Autre Auteur
description: Cette page utilise la licence par défaut
tags:
  - exemple
  - défaut
---

# Page sans licence spécifiée

Cette page démontre le comportement du plugin quand **aucune licence n'est spécifiée** dans l'en-tête YAML.

## Configuration de cette page

Dans l'en-tête YAML de cette page, nous n'avons **pas** inclus de propriété `license` :

```yaml
---
title: Page sans licence spécifiée
author: Autre Auteur
description: Cette page utilise la licence par défaut
# Pas de propriété 'license' ici !
---
```

## Résultat

Le plugin utilise automatiquement la **licence par défaut** configurée dans `mkdocs.yml` :

**Licence de cette page :** {{ cc_license(page.meta) }}

## Configuration par défaut

Dans le fichier `mkdocs.yml`, nous avons configuré :

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"  # ← Licence par défaut
      language: "fr"
      target_blank: true
      show_icons: true
```

## Détails de la licence par défaut

{% set license_info = get_license_info(page.meta) %}

- **Code de licence :** `{{ license_info.license_code }}`
- **Nom complet :** {{ license_info.full_name }}
- **Éléments :** {{ license_info.elements | join(', ') }}

## Signification de BY-SA

Cette licence Creative Commons par défaut signifie :

- **BY (Attribution)** : Vous devez créditer l'auteur original
- **SA (ShareAlike)** : Les œuvres dérivées doivent utiliser la même licence

C'est une licence **permissive** qui autorise l'usage commercial tout en préservant l'attribution et le partage à l'identique.

---

[Retour à l'accueil](index.md)
