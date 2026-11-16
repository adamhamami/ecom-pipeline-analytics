# Pile technologique observée

## Langage et exécution

- Python; l'interpréteur observé dans l'environnement est **3.14.4**. Le projet ne déclare pas de version Python minimale/maximale.
- Scripts synchrones exécutables par `python etl/<script>.py`; orchestration par appels de fonctions Python et impressions sur stdout.
- Chemins relatifs et exécution depuis la racine attendus. Il n'y a ni packaging déclaré, ni point d'entrée de console configuré.

## Bibliothèques et stockage

| Technologie | Version observée / déclaration | Usage |
|---|---|---|
| pandas | 2.3.3 installé dans l'environnement; non épinglé par le projet | Lecture CSV/Parquet, transformation tabulaire, `DataFrame.to_sql`, requêtes SQL. |
| PyYAML (`yaml`) | 6.0.3 installé; non épinglé | Chargement de `config/config.yaml`. |
| PyArrow | 24.0.0 installé; non épinglé | Support Parquet utilisé par Pandas dans l'environnement observé. |
| `sqlite3` | Bibliothèque standard Python; version SQLite non inventoriée | Entrepôt local, vues SQL et lecture des marts. |
| `pathlib`, `csv` (outil d'inspection seulement) | Bibliothèque standard Python | Gestion des chemins dans le code. |

Le projet ne contient pas de `requirements.txt`, `pyproject.toml`, fichier de lock ou autre manifeste de dépendances. Les versions ci-dessus décrivent l'environnement inspecté et ne constituent pas une déclaration reproductible du dépôt.

## Architecture d'exécution

- **ETL** : scripts Python Pandas, synchrones et séquentiels.
- **Stockage intermédiaire** : CSV en entrée, Parquet en zone traitée.
- **Entrepôt** : SQLite local `data/processed/ecom_analytics.db`.
- **Marts** : vues SQLite dans `sql/marts.sql`; extraction vers CSV par `etl/export_marts.py`.
- **Configuration** : chemins YAML, mais certaines destinations restent codées en dur.
- **BI** : exports annoncés comme prêts pour Power BI; aucun modèle Power BI n'est présent dans l'inventaire.

## Fichiers de configuration pertinents

- `config/config.yaml` — `data_paths`, `processed_paths`, `database.url`.
- `.vscode/settings.json` — connexion SQLTools SQLite; le nom d'espace de travail référencé (`ecom-mini-pipeline`) diffère du nom du répertoire observé (`ecom-pipeline-analytics`).
- `.gitignore` — exclut l'environnement virtuel, le cache Python, Parquet et la base SQLite, mais pas les CSV de marts.

## Limitations de l'inventaire

Aucun cadre web, ORM, système de messages, client réseau, moteur de workflow, dépendance de validation ou suite de tests n'est déclaré. Aucun API ou schéma d'API n'a été trouvé. L'état de fin de vie des versions ne peut pas être établi à partir de métadonnées de dépendances du projet, puisqu'il n'y a pas de manifeste/version cible.
