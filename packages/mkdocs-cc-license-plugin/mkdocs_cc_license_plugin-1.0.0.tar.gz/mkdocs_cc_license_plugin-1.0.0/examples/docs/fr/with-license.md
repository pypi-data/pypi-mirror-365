---
title: Page avec licence personnalisée
license: "by-nc-sa"
author: Exemple Auteur
description: Cette page montre l'utilisation d'une licence personnalisée
tags:
  - exemple
  - licence
---

# Page avec licence personnalisée

Cette page démontre l'utilisation d'une **licence Creative Commons personnalisée**.

## Configuration de la licence

Dans l'en-tête YAML de cette page, nous avons spécifié :

```yaml
---
title: Page avec licence personnalisée
license: "by-nc-sa"   # Attribution-NonCommercial-ShareAlike
author: Exemple Auteur
---
```

## Résultat

Le plugin génère automatiquement les icônes et le lien appropriés pour cette licence :

**Licence de cette page :** {{ cc_license(page.meta) }}

## Test direct des fonctions

Voici un test direct des fonctions du plugin :

{% set license_info = get_license_info(page.meta) %}

- **Code de licence :** `{{ license_info.license_code }}`
- **Nom complet :** {{ license_info.full_name }}
- **Éléments :** {{ license_info.elements | join(', ') }}
- **URL :** [{{ license_info.url }}]({{ license_info.url }})

## Signification de BY-NC-SA

Cette licence Creative Commons signifie :

- **BY (Attribution)** : Vous devez créditer l'auteur original
- **NC (NonCommercial)** : Utilisation non commerciale uniquement
- **SA (ShareAlike)** : Les œuvres dérivées doivent utiliser la même licence

---

[Retour à l'accueil](index.md)
