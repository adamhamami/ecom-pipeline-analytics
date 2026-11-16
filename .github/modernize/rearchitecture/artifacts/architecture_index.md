# Index d'architecture

## Périmètre

Analyse statique du pipeline Python/Pandas, des fichiers SQL, de la configuration et des sorties présentes. Aucun framework cible, besoin de migration ou point de coupure déclaré. `migration_boundary.yaml` et `seams.yaml` ne sont donc pas produits.

## Implementation Guide

**This index is not the full contract. Do not implement from this file alone; follow the artifact paths below.**

### Artifacts globaux

- `unit_graph.yaml`
  - À lire par tous; source de vérité pour les commandes, signatures, dépendances et modules partagés.
  - Repérer le nom de l'unité assignée, puis lire ses ancres et références communes.
- `shared_modules.yaml`
  - À lire par les unités qui utilisent de la configuration partagée.
  - Filtrer les modules par `used_by_units`; chaque `shared_refs[].used_fields` doit rester dans `fields`.
- `wire_contracts.yaml`
  - À lire par les unités d'extraction et d'export.
  - Filtrer par `unit`; préserver noms, colonnes et sens des fichiers/vues décrits.
- `cross_unit_state.yaml`
  - Aucun flux implicite inter-unités n'a été détecté (`flows: []`).
- `project-structure.md`, `tech-stack.md`, `data-model.md`
  - Vues globales de navigation, pile existante et modèle de données. Le modèle distingue le DDL déclaré des tables réellement présentes.

### Unités exécutables

| Unité | Déclencheur | Fichiers par unité à lire | Contrats globaux pertinents |
|---|---|---|---|
| `full-pipeline` | `python etl/pipeline.py` | `units/full-pipeline/behavior.yaml`, `units/full-pipeline/bindings.yaml`, `units/full-pipeline/unit_decomposition.yaml` | Dépendances `unit_graph.yaml`; aucun module partagé. |
| `extract` | `python etl/extract.py` | `units/extract/behavior.yaml`, `units/extract/bindings.yaml`, `units/extract/unit_decomposition.yaml` | `wire_contracts.yaml` pour les trois CSV; `shared_modules.yaml` pour `pipeline-config`. |
| `validate` | `python etl/validate.py` | `units/validate/behavior.yaml`, `units/validate/bindings.yaml`, `units/validate/unit_decomposition.yaml` | `shared_modules.yaml` pour `pipeline-config`. |
| `transform` | `python etl/transform.py` | `units/transform/behavior.yaml`, `units/transform/bindings.yaml`, `units/transform/unit_decomposition.yaml` | `shared_modules.yaml` pour `pipeline-config`. |
| `load` | `python etl/load.py` | `units/load/behavior.yaml`, `units/load/bindings.yaml`, `units/load/unit_decomposition.yaml` | `shared_modules.yaml` pour `pipeline-config`; comparer le DDL aux faits documentés dans `data-model.md`. |
| `export-marts` | `python etl/export_marts.py` | `units/export-marts/behavior.yaml`, `units/export-marts/bindings.yaml`, `units/export-marts/unit_decomposition.yaml` | `wire_contracts.yaml` pour les quatre vues SQL. |

### Preuve attendue avant de déclarer une unité terminée

Indiquer les artefacts lus, les effets de bord/branches/erreurs conservés, les contrats non résolus ou différés, et les éléments de vérification réellement exécutés (tests, build ou exécution). Ne pas présenter l'analyse statique comme une preuve d'exécution.

Les `unit_decomposition.yaml` sont des pistes à examiner, avec `commit: false`; ils ne prescrivent pas de nouvelle unité cible.
