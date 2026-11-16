# Modèle de données existant

## Sources et entités

Les structures source sont décrites dans `docs/data_dictionary.md` et corroborées par les en-têtes CSV.

| Entité | Source / grain | Champs |
|---|---|---|
| Commande | `orders.csv`; une ligne par commande | `order_id`, `order_date`, `customer_id`, `channel`, `status`, `subtotal`, `shipping_fee`, `discount`, `tax`, `total`, `promised_ship_date`, `actual_ship_date`. |
| Ligne de commande | `order_items.csv`; une ligne par article commandé | `order_id`, `sku`, `qty`, `unit_price`, `category`. |
| Client | `customers.csv`; une ligne par client | `customer_id`, `signup_date`, `city`, `state`, `segment`. |

## Modèle analytique défini par le code

Le DDL exécuté par `etl/load.py` définit les cinq tables ci-dessous. `sql/schema.sql` ne contient aucun DDL.

### Dimensions

- **`dim_customer`** : `customer_id INTEGER PRIMARY KEY`, `signup_date TEXT`, `city TEXT`, `state TEXT`, `segment TEXT`, `signup_year_month TEXT`.
- **`dim_date`** : `date_key TEXT PRIMARY KEY`, `year INTEGER`, `month INTEGER`, `day INTEGER`, `year_month TEXT`; une date distincte issue de `order_date`.
- **`dim_product`** : `sku TEXT PRIMARY KEY`, `category TEXT`.

### Faits

- **`fact_orders`** : `order_id INTEGER PRIMARY KEY`, `order_date TEXT`, `customer_id INTEGER`, `channel TEXT`, `status TEXT`, `subtotal REAL`, `shipping_fee REAL`, `discount REAL`, `tax REAL`, `total REAL`, `promised_ship_date TEXT`, `actual_ship_date TEXT`, `gmv REAL`, `net_revenue REAL`, `days_to_ship INTEGER`, `on_time INTEGER`, `year_month TEXT`, `status_normalized TEXT`. Le DDL déclare une FK de `customer_id` vers `dim_customer(customer_id)`.
- **`fact_order_items`** : `order_id INTEGER`, `sku TEXT`, `qty INTEGER`, `unit_price REAL`, `category TEXT`, `extended_price REAL`. Le DDL déclare les FK vers `fact_orders(order_id)` et `dim_product(sku)`; aucune PK de ligne n'est définie.

## Relations et flux

- Un client est référencé par plusieurs commandes via `fact_orders.customer_id`.
- Une commande est référencée par plusieurs lignes via `fact_order_items.order_id`.
- Un produit est référencé par des lignes via `fact_order_items.sku`.
- `dim_date` est créée à partir des dates de commande, mais aucune FK `fact_orders.order_date → dim_date.date_key` n'est déclarée.
- `fact_order_items.category` est conservé en plus de `dim_product.category`.
- Le code calcule `gmv = subtotal`, `net_revenue = total`, `days_to_ship`, `on_time`, `year_month`, le statut normalisé, `extended_price = qty * unit_price` et `signup_year_month`.

## Résumé des entités clés

1. `orders` — événement d'achat et montants agrégés.
2. `order_items` — détail des SKU/quantités/prix par commande.
3. `customers` — attributs de profil et de segment.
4. `dim_customer` — dimension client analytique avec période d'inscription.
5. `dim_date` — calendrier dérivé pour regroupements temporels.
6. `dim_product` — catalogue SKU/catégorie observé dans les lignes.
7. `fact_orders` — fait de commande avec mesures financières et d'expédition.
8. `fact_order_items` — fait au grain de la ligne de commande avec prix étendu.

## Vues et grain de restitution

`sql/marts.sql` définit `v_kpi_daily` (jour), `v_revenue_by_channel` (canal/mois), `v_aov_by_segment` (segment/mois) et `v_ship_perf` (mois). Le détail des colonnes et calculs est décrit dans le SQL et le dictionnaire de données.

## Écart entre DDL et base présente

Dans le fichier SQLite inspecté, `dim_customer`, `dim_date`, `dim_product`, `fact_orders` et `fact_order_items` ont été recréées par Pandas : les métadonnées réelles ne montrent ni PK ni FK, contrairement au DDL embarqué. Cette différence est produite par les appels `to_sql(..., if_exists="replace")` du chargeur. Le schéma décrit ci-dessus est donc le schéma déclaré dans le code, pas celui effectivement imposé par la base présente.
