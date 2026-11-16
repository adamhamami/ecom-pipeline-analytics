# Structure du projet

## Classification

Projet **backend / pipeline ETL batch local**. C'est un dépôt Python unique, sans frontend, API, package publié, ni services déployables séparés. Les données sortent sous forme de Parquet, d'une base SQLite et de CSV analytiques destinés à la BI.

## Modules et couches

| Couche | Fichiers source | Rôle |
|---|---:|---|
| Orchestration ETL | 1 | Enchaîne extraction, validation, transformation et chargement. |
| Étapes ETL | 4 | Extraction, contrôles qualité, enrichissement et chargement dimensionnel. |
| Export analytique | 1 | Lit les vues SQLite et produit des CSV de marts. |
| Configuration | 1 YAML | Chemins des CSV, Parquet d'entrée et base SQLite. |
| SQL | 2 fichiers | `marts.sql` définit les vues; `schema.sql` est vide. |
| Documentation | 3 Markdown | Démarrage, dictionnaire de données et rapport qualité. |

Il n'y a pas de couche web, service métier distinct, ORM, ni couche repository. La logique métier est portée par les fonctions Pandas d'`etl/transform.py`; le modèle analytique est déclaré dans `etl/load.py` et interrogé par `sql/marts.sql`.

## Entrées exécutables

Chaque script possède un bloc `if __name__ == "__main__"` et peut être lancé indépendamment depuis la racine :

- `python etl/pipeline.py` — commande complète; étapes invoquées dans l'ordre extrait → validé → transformé → chargé (`etl/pipeline.py:21-38`).
- `python etl/extract.py` — CSV bruts vers Parquet (`etl/extract.py:31,60-61`).
- `python etl/validate.py` — contrôle des commandes et rapport qualité (`etl/validate.py:22,72,93-94`).
- `python etl/transform.py` — ajoute les champs dérivés (`etl/transform.py:30,73,109-110`).
- `python etl/load.py` — crée/remplit les tables SQLite (`etl/load.py:31-91,148-149`).
- `python etl/export_marts.py` — exporte les vues existantes vers CSV (`etl/export_marts.py:15,28`).

`sql/marts.sql` n'est pas une entrée d'exécution dans la pipeline Python. Aucun serveur, ordonnanceur, route ou événement externe n'est déclaré.

## Domaines fonctionnels

1. **Ingestion** : lecture des trois CSV `orders`, `order_items` et `customers`; écriture des Parquet bruts.
2. **Qualité des commandes** : colonnes obligatoires, dates, total calculé, total négatif, doublons.
3. **Enrichissement analytique** : GMV, revenus, délai/ponctualité d'expédition, mois de commande, statut normalisé, prix étendu et mois d'inscription.
4. **Entrepôt SQLite** : dimensions client/date/produit et faits commandes/lignes de commande.
5. **Marts BI** : KPI quotidiens, revenu par canal, AOV par segment et performance d'expédition; export CSV.

## Chemin des données et configuration

`data/raw/*.csv` → `data/processed/*.parquet` → `*_transformed.parquet` → `data/processed/ecom_analytics.db` → vues SQL → `data/processed/marts/*.csv`.

`config/config.yaml` fournit les chemins d'entrée et de sortie Parquet et l'URL SQLite. Plusieurs chemins de sorties transformées, de chargement et d'export sont toutefois codés en dur dans les scripts. Les chemins relatifs supposent que le processus démarre depuis la racine du projet.

## Inventaire constaté

- Code : **6 scripts Python** sous `etl/`.
- SQL : **2 fichiers**, dont `sql/schema.sql` vide et `sql/marts.sql` non appelé par l'orchestrateur.
- Configuration : **1 YAML**; documentation : **3 Markdown**; fichier VS Code : **1 JSON**.
- Données brutes présentes : 3 CSV, total **10 lignes** (3 commandes, 4 lignes de commande, 3 clients).
- Données traitées présentes : 6 Parquet, 1 SQLite et 4 CSV de marts.
- Aucun manifeste de dépendances, répertoire de tests ou configuration CI n'a été trouvé dans l'inventaire du projet.

## Constats de fonctionnement

- `run_validation` calcule un DataFrame nettoyé, mais `pipeline.py` ignore cette valeur; `run_transforms` relit le Parquet extrait. Les lignes éliminées par la validation peuvent donc encore être chargées.
- `load.py` exécute un DDL avec clés primaires/étrangères, puis chaque table est écrite avec `if_exists="replace"`. La base présente confirme que les tables résultantes n'ont plus ces contraintes.
- La pipeline ne lance ni `sql/marts.sql` ni `etl/export_marts.py`. La base observée contient déjà les vues, mais une reconstruction complète depuis les étapes de la pipeline ne les crée pas.
- Le DDL est maintenu dans `etl/load.py`; le fichier annoncé `sql/schema.sql` est vide.
- Le rapport qualité existant décrit des contrôles sans erreurs sur le petit jeu présent; ce n'est pas une preuve de couverture automatisée.
