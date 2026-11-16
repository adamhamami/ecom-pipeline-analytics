# E-commerce Analytics Pipeline

Pipeline ETL local qui transforme des fichiers CSV de commandes, clients et articles en fichiers Parquet, charge un entrepôt analytique SQLite et fournit des vues SQL et des exports CSV pour l’analyse.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture et flux de données](#architecture-et-flux-de-données)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Exécution](#exécution)
- [Entrepôt et marts](#entrepôt-et-marts)
- [Configuration](#configuration)
- [Qualité et limites connues](#qualité-et-limites-connues)
- [Documentation](#documentation)

## Fonctionnalités

- Extraction de trois sources CSV vers Parquet.
- Contrôles de qualité sur les commandes et génération d’un rapport Markdown.
- Calcul de mesures et dimensions temporelles utiles à l’analyse.
- Chargement des dimensions et faits dans une base SQLite locale.
- Vues analytiques SQL et export de ces vues en CSV pour des outils de BI.

## Architecture et flux de données

```text
data/raw/*.csv
      │
      ▼
python etl/pipeline.py
      ├── 1. Extraction ──► data/processed/*.parquet
      ├── 2. Validation ──► docs/data_quality.md
      ├── 3. Transformation ──► data/processed/*_transformed.parquet
      └── 4. Chargement ──► data/processed/ecom_analytics.db
                                      │
                         sql/marts.sql (à appliquer séparément)
                                      │
                         python etl/export_marts.py
                                      ▼
                         data/processed/marts/*.csv
```

### Structure du dépôt

```text
.
├── config/
│   └── config.yaml
├── data/
│   ├── raw/                    # CSV sources
│   └── processed/              # Parquet, base SQLite et exports générés
├── docs/
│   ├── data_dictionary.md      # Champs, tables et vues
│   ├── data_quality.md         # Rapport de qualité généré
│   └── README.md               # Documentation du projet
├── etl/
│   ├── extract.py
│   ├── validate.py
│   ├── transform.py
│   ├── load.py
│   ├── pipeline.py             # Orchestrateur des quatre étapes ETL
│   └── export_marts.py         # Export des vues SQL vers des CSV
└── sql/
    ├── marts.sql               # Définitions des vues analytiques
    └── schema.sql              # Réservé; le DDL utilisé est actuellement dans load.py
```

## Prérequis

- Python 3.9 ou plus récent.
- `pip`.
- SQLite pour appliquer le fichier SQL avec la commande proposée ci-dessous, ou un outil graphique compatible SQLite.

Les dépendances Python utilisées sont `pandas`, `PyYAML` et `pyarrow`. Le projet ne fournit pas actuellement de fichier de dépendances verrouillé.

## Installation

Depuis la racine du dépôt, dans PowerShell :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas PyYAML pyarrow
```

Si l’activation de l’environnement virtuel est restreinte par la stratégie PowerShell de votre poste, utilisez directement son interpréteur :

```powershell
.\.venv\Scripts\python.exe -m pip install pandas PyYAML pyarrow
```

## Exécution

Lancer les commandes depuis la racine du projet : les chemins configurés et certains chemins de sortie sont relatifs au répertoire courant.

### Pipeline ETL

```powershell
python etl/pipeline.py
```

L’orchestrateur lance, dans cet ordre, l’extraction, la validation, la transformation et le chargement. Les étapes peuvent aussi être lancées individuellement :

```powershell
python etl/extract.py
python etl/validate.py
python etl/transform.py
python etl/load.py
```

### Création des vues et export BI

La pipeline ne lance pas `sql/marts.sql` ni l’export CSV. Sur une base neuve, appliquer les définitions de vues après le chargement :

```powershell
sqlite3 data/processed/ecom_analytics.db ".read sql/marts.sql"
```

La commande `sqlite3` doit être disponible sur le `PATH`. Il est également possible d’ouvrir `data/processed/ecom_analytics.db` dans un outil SQLite et d’y exécuter le contenu de `sql/marts.sql`.

Puis exporter les vues en CSV :

```powershell
python etl/export_marts.py
```

Les exports sont créés dans `data/processed/marts/`.

## Entrepôt et marts

### Tables

| Type | Tables | Grain |
|---|---|---|
| Dimensions | `dim_customer`, `dim_date`, `dim_product` | Client, date distincte de commande, SKU |
| Faits | `fact_orders`, `fact_order_items` | Commande, ligne d’article |

### Vues analytiques

| Vue | Grain | Mesures principales |
|---|---|---|
| `v_kpi_daily` | Jour de commande | Nombre de commandes, GMV, revenu net, taux à l’heure |
| `v_revenue_by_channel` | Canal et mois | Revenu net, nombre de commandes |
| `v_aov_by_segment` | Segment client et mois | Panier moyen, nombre de commandes |
| `v_ship_perf` | Mois | Délai moyen d’expédition, taux de retard |

Les vues sont définies dans [`sql/marts.sql`](sql/marts.sql). Les champs, tables et règles de calcul sont détaillés dans [`docs/data_dictionary.md`](docs/data_dictionary.md).

## Configuration

[`config/config.yaml`](config/config.yaml) contient :

- `data_paths` : chemins des fichiers CSV source.
- `processed_paths` : chemins des fichiers Parquet extraits.
- `database.url` : URL SQLite, par défaut `sqlite:///data/processed/ecom_analytics.db`.

Exécuter les scripts depuis la racine du projet et conserver des chemins compatibles avec les chemins utilisés dans le code. Certaines destinations de transformation et d’export sont actuellement définies directement dans les scripts.

## Qualité et limites connues

- La validation porte sur `orders` : champs requis, valeurs nulles, totaux négatifs, cohérence du total, dates d’expédition et doublons.
- Le rapport est écrit dans [`docs/data_quality.md`](docs/data_quality.md) et est remplacé à chaque exécution de la validation orchestrée.
- **Les lignes filtrées par la validation ne sont actuellement pas transmises à la transformation.** La fonction de validation retourne un DataFrame nettoyé, mais l’orchestrateur ignore ce résultat et la transformation relit les Parquet extraits. Le rapport ne doit donc pas être interprété comme une garantie que les données invalides ont été exclues de la base.
- Le chargement remplace les tables SQLite à chaque exécution. Le DDL est défini dans [`etl/load.py`](etl/load.py); [`sql/schema.sql`](sql/schema.sql) est actuellement vide. Les appels Pandas avec `if_exists="replace"` recréent les tables et ne préservent pas nécessairement les contraintes déclarées par le DDL.
- Les fichiers CSV sources doivent contenir les colonnes attendues par les transformations; les validations ne couvrent pas les trois jeux de données de façon uniforme.
- Aucun test automatisé ni manifeste de dépendances reproductible n’est fourni dans le dépôt.

## Documentation

- [`docs/data_dictionary.md`](docs/data_dictionary.md) — description des CSV, fichiers transformés, tables et vues.
- [`docs/data_quality.md`](docs/data_quality.md) — dernier rapport qualité généré.
- [`docs/README.md`](docs/README.md) — documentation complémentaire du pipeline.
