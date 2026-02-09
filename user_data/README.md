# Ce dossier contient les données utilisateur de DermaLogic

Les fichiers dans ce dossier sont ignorés par git pour protéger vos données personnelles.

## Fichiers générés automatiquement

- `config.json` - Configuration de la ville actuelle et favoris
- `produits_derma.json` - Vos produits cosmétiques personnalisés

## Dossier historique/

Le dossier `historique/` contient l'historique de vos analyses :

- `analyses_recentes.json` - Analyses des 2 dernières semaines
- `analyses_archives.json` - Analyses plus anciennes (archivées automatiquement)

### Rotation automatique

Les analyses de plus de **14 jours** sont automatiquement déplacées vers les archives au démarrage de l'application et lors de chaque nouvelle analyse.
