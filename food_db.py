"""
Base nutritionnelle multi-sources pour stabiliser l'estimation calorique
des check-ins en texte libre.

=======================================================================
SOURCES (à citer telles quelles dans le rapport de PFE)
=======================================================================

1) TCAT — Table de Composition des Aliments Tunisiens
   El Ati J., Béji C., Farhat A., Haddad S., Cherif S., Trabelsi T.,
   Danguir J., Gaigi S., Le Bihan G., Landais E., Eymard-Duvernay S.,
   Maire B., Delpeuch F. (2007). Table de composition des aliments
   tunisiens. Tunis : INNTA ; Montpellier : IRD, 294 p.
   ISBN 9789973998002.
   PDF officiel : https://horizon.documentation.ird.fr/exl-doc/pleins_textes/divers20-05/010041597.pdf
   -> Source PRIMAIRE et prioritaire : c'est la référence académique
      tunisienne officielle (228+ aliments/plats, 34 nutriments,
      noms en français/anglais/arabe littéraire/dialecte tunisien).
   -> Valeurs ci-dessous extraites directement du PDF (aliments crus,
      pour 100g de partie comestible). L'extraction automatique du
      document s'est arrêtée après une dizaine d'entrées (limite de
      l'outil, pas de la source) -- la table ci-dessous est donc un
      sous-ensemble fidèle mais partiel des 228+ aliments du document.
      Le reste peut être complété manuellement depuis le PDF (table
      des matières complète conservée en commentaire en bas de
      fichier pour référence).

2) CIQUAL — Table de composition nutritionnelle des aliments (ANSES,
   France). Agence nationale de sécurité sanitaire de l'alimentation,
   de l'environnement et du travail. Disponible sur https://ciqual.anses.fr
   -> Table française de référence (3480+ aliments), utilisée en
      COMPLÉMENT quand un aliment n'existe pas dans la TCAT (produits
      transformés, plats non spécifiquement tunisiens).
   -> Le site officiel ciqual.anses.fr ne permet pas l'extraction
      automatisée en masse (interface JS). Les valeurs ci-dessous
      proviennent de pages qui citent explicitement leur source
      Ciqual ; à re-vérifier sur ciqual.anses.fr avant publication
      académique si une précision au gramme près est nécessaire.

3) USDA FoodData Central. U.S. Department of Agriculture, Agricultural
   Research Service, Beltsville Human Nutrition Research Center.
   Disponible sur https://fdc.nal.usda.gov/ (données CC0, domaine public)
   -> Référence internationale, utilisée en dernier recours pour les
      aliments absents de TCAT et CIQUAL. FDC ID cité pour chaque
      entrée -> vérifiable directement sur fdc.nal.usda.gov/food-details/<FDC_ID>.

4) Dataset GitHub "Tunisian Food Database" (elyesmanai/Data-Science-Datasets)
   https://github.com/elyesmanai/Data-Science-Datasets/blob/main/EDA%20-%20Tunisian%20Food%20Database%20-%20Products.csv
   -> Produits DE MARQUE vendus en Tunisie (biscuits, chocolats, etc.),
      231 lignes, calories déjà annotées par marque/produit.
   -> Fichier protégé par robots.txt : non téléchargeable par un outil
      automatisé. Les quelques entrées ci-dessous viennent d'un extrait
      visible publiquement (aperçu de recherche) ; pour le jeu complet,
      téléchargez-le manuellement depuis GitHub ("Download raw file")
      et exécutez load_github_branded_csv() ci-dessous dessus, puis
      register_branded_products().

=======================================================================
PRIORITÉ DE RECHERCHE (dans match_food_item)
=======================================================================
Toutes les tables sont indexées une seule fois au démarrage. Pour
chaque aliment, on garde la MEILLEURE correspondance (score), puis en
cas d'égalité l'alias le plus spécifique, puis l'ordre de priorité :
1. Plats tunisiens composites (COMPOSITE_DISHES) -- estimations
   internes ("source": "internal_estimate"), à valider avec un(e)
   nutritionniste avant production.
2. Aliments courants CUITS / prêts à manger (COOKED_FOODS) -- évite
   d'appliquer une valeur CRUE (riz cru ~360 kcal/100g) à un aliment
   que l'utilisateur a mangé cuit (riz cuit ~130 kcal/100g).
3. Ingrédients bruts officiels (TCAT, puis CIQUAL, puis USDA)
4. Produits de marque tunisiens (GitHub dataset)
5. Fallback LLM si rien n'est trouvé
"""

import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache

# =======================================================================
# 1) TCAT -- valeurs officielles extraites du PDF (aliments crus, /100g)
#    "state": "raw"  -> valeur à l'état cru/sec
#    "unit_g"        -> poids d'une unité (pour "3 biscottes")
# =======================================================================
TCAT_INGREDIENTS = {
    "amidon": {
        "aliases": ["amidon", "cornstarch", "maizena"],
        "kcal_100g": 381, "protein_g": 0.26, "fat_g": 0.05, "carbs_g": 91.27,
        "source": "TCAT", "tcat_page": 4, "state": "raw",
        "portion_g": {"small": 5, "medium": 10, "large": 20},
    },
    "biscotte_ordinaire": {
        "aliases": ["biscotte", "biscotte ordinaire", "toast craker salted"],
        "kcal_100g": 390, "protein_g": 12.10, "fat_g": 3.20, "carbs_g": 76.60,
        "source": "TCAT", "tcat_page": 5,
        "unit_g": 10, "portion_g": {"small": 10, "medium": 20, "large": 40},
    },
    "biscotte_sans_sel": {
        "aliases": ["biscotte sans sel", "toast craker unsalted"],
        "kcal_100g": 390, "protein_g": 12.10, "fat_g": 3.20, "carbs_g": 76.60,
        "source": "TCAT", "tcat_page": 6,
        "unit_g": 10, "portion_g": {"small": 10, "medium": 20, "large": 40},
    },
    "ble_graines": {
        "aliases": ["ble", "ble en graines", "wheat dry", "قمح"],
        "kcal_100g": 327, "protein_g": 12.61, "fat_g": 1.54, "carbs_g": 65.68,
        "source": "TCAT", "tcat_page": 7, "state": "raw",
    },
    "brioche": {
        "aliases": ["brioche"],
        "kcal_100g": 406, "protein_g": 8.20, "fat_g": 21.00, "carbs_g": 45.80,
        "source": "TCAT", "tcat_page": 8,
        "unit_g": 50, "portion_g": {"small": 30, "medium": 50, "large": 100},
    },
    "couscous_sec": {
        "aliases": ["couscous sec", "couscous cru", "couscous-dry-cup"],
        "kcal_100g": 350, "protein_g": 13.44, "fat_g": 1.50, "carbs_g": 73.98,
        "source": "TCAT", "tcat_page": 9, "state": "raw",
    },
    "farine_blanche": {
        "aliases": ["farine", "farine blanche", "wheat flour white", "طحين"],
        "kcal_100g": 364, "protein_g": 11.00, "fat_g": 1.20, "carbs_g": 74.70,
        "source": "TCAT", "tcat_page": 10, "state": "raw",
    },
    "farine_orge": {
        "aliases": ["farine d'orge", "barley flour"],
        "kcal_100g": 380, "protein_g": 12.00, "fat_g": 4.00, "carbs_g": 76.00,
        "source": "TCAT", "tcat_page": 11, "state": "raw",
    },
    "mais_graines_seches": {
        "aliases": ["mais graines seches", "corn dry seeds"],
        "kcal_100g": 365, "protein_g": 9.42, "fat_g": 4.74, "carbs_g": 74.26,
        "source": "TCAT", "tcat_page": 12, "state": "raw",
    },
    "orge_perle_cru": {
        "aliases": ["orge", "orge perle", "pearled barley", "شعير"],
        "kcal_100g": 352, "protein_g": 9.91, "fat_g": 1.16, "carbs_g": 77.72,
        "source": "TCAT", "tcat_page": 13, "state": "raw",
    },
}

# Index complet des 228+ aliments/plats couverts par la TCAT (noms
# français/anglais tels qu'en table des matières du PDF) -- utile pour
# savoir QUOI compléter en priorité, même si les valeurs numériques ne
# sont pas encore toutes saisies ici. Voir le PDF officiel pour les
# valeurs manquantes (pages 14-272).
TCAT_KNOWN_FOOD_NAMES = [
    "Pain au chocolat", "Pain de mie", "Pain, baguette", "Pain, complet",
    "Pain, mbassess", "Pain, mlawi", "Pain, orge", "Pain, tabouna",
    "Pain, tagine", "Pâte alimentaire crue", "Pâte feuilletée crue",
    "Riz cru", "Semoule", "Sorgho", "Patate douce crue",
    "Pomme de terre frite", "Pomme de terre crue", "Fenugrec",
    "Fève sèche crue", "Haricot blanc sec cru", "Lentille sèche",
    "Pois chiches secs", "Artichaut cru", "Aubergine crue", "Bette crue",
    "Betterave rouge crue", "Carotte crue", "Céleri", "Champignon cru",
    "Chou vert cru", "Chou-fleur cru", "Concombre cru", "Courge crue",
    "Courgette crue", "Épinard cru", "Fenouil", "Fève fraîche crue",
    "Gombo cru", "Haricot vert cru", "Laitue crue", "Navet cru",
    "Oignon cru", "Persil frais", "Petit pois cru", "Poireau cru",
    "Poivron vert cru", "Radis cru", "Tomate concentrée", "Tomate crue",
    "Abricot", "Ananas frais", "Avocat frais", "Banane pulpe fraîche",
    "Datte pulpe et peau", "Citron pulpe frais", "Clémentine/mandarine",
    "Figue de barbarie", "Figue sèche", "Melon pulpe frais",
    "Fraise fraîche", "Grenade fraîche", "Jus d'orange frais",
    "Mangue pulpe fraîche", "Olive noire en saumure",
    "Olive verte en saumure", "Orange douce pulpe fraîche",
    "Pastèque pulpe fraîche", "Pêche", "Pomme fraîche", "Raisin frais",
    "Amande sèche", "Cacahuète grillée", "Noisette naturelle",
    "Noix naturelle", "Pistache grillée", "Sésame graine",
    "Foie d'agneau cru", "Rognon d'agneau cru", "Viande de lapin crue",
    "Viande de bœuf crue", "Viande de chameau crue", "Viande de chèvre crue",
    "Viande d'agneau crue", "Viande de poulet crue", "Viande de dinde crue",
    "Anchois frais", "Calamar cru", "Thon conserve", "Maquereau cru",
    "Merlu cru", "Moule crue", "Poulpe cru", "Sardine conserve",
    "Sardine crue", "Seiche crue", "Sole crue", "Crevette crue",
    "Œuf frais", "Lait entier UHT", "Leben", "Rayeb",
    "Yaourt au lait demi-écrémé nature", "Fromage pâte dure",
    "Beurre", "Huile d'olive extra vierge", "Huile de tournesol",
    "Margarine", "Smen", "Chamia", "Confiture", "Glace", "Miel",
    "Sucre", "Ail frais", "Cannelle", "Cumin en poudre", "Harissa",
    "Menthe fraîche", "Piment rouge moulu", "Café noir", "Thé",
    # ... liste complète des 228+ items dans le PDF officiel (voir
    # sommaire pages i-iv du document source)
]



# =======================================================================
# 2) CIQUAL (ANSES) -- valeurs complémentaires, citées via sources
#    secondaires qui référencent explicitement Ciqual. À reconfirmer
#    sur ciqual.anses.fr si une précision académique stricte est requise.
# =======================================================================
CIQUAL_INGREDIENTS = {
    "semoule_couscous_cru": {
        "aliases": ["semoule crue", "couscous semoule crue"],
        "kcal_100g": 376, "protein_g": 13.0, "fat_g": 0.6, "carbs_g": 77.0,
        "source": "CIQUAL", "note": "ANSES/Ciqual 2024, via sorn.fr (à revérifier sur ciqual.anses.fr)",
        "state": "raw",
    },
    "legumes_couscous_cuits": {
        "aliases": ["legumes couscous cuits", "legumes pour couscous"],
        "kcal_100g": 20, "protein_g": None, "fat_g": None, "carbs_g": None,
        "source": "CIQUAL", "note": "Ciqual 2017, via alimentation-et-nutrition.fr",
    },
}

# =======================================================================
# 3) USDA FoodData Central -- FDC ID cité pour vérification directe
# =======================================================================
USDA_INGREDIENTS = {
    "poulet_blanc_cru": {
        "aliases": ["poulet cru", "blanc de poulet cru", "chicken breast raw", "دجاج نيء"],
        "kcal_100g": 114, "protein_g": 21.2, "fat_g": 2.6, "carbs_g": 0.0,
        "source": "USDA", "fdc_id": 171077,
        "fdc_url": "https://fdc.nal.usda.gov/food-details/171077/nutrients",
        "state": "raw",
    },
    "poulet_blanc_cuit": {
        "aliases": ["poulet", "poulet cuit", "blanc de poulet", "blanc de poulet cuit",
                    "chicken breast cooked", "poulet grille", "dajaj", "دجاج"],
        "kcal_100g": 165, "protein_g": 31.0, "fat_g": 3.6, "carbs_g": 0.0,
        "source": "USDA", "fdc_id": 171477,
        "fdc_url": "https://fdc.nal.usda.gov/food-details/171477/nutrients",
    },
}

# =======================================================================
# 3 bis) Aliments courants CUITS / prêts à manger, /100g.
#    Valeurs génériques de référence (ordre de grandeur USDA/CIQUAL).
#    TODO PFE : ajouter le FDC ID ou le code Ciqual exact de chaque
#    entrée après vérification sur fdc.nal.usda.gov / ciqual.anses.fr.
# =======================================================================
COOKED_FOODS = {
    "riz_blanc_cuit": {
        "aliases": ["riz", "riz blanc", "riz cuit", "rouz", "roz", "رز", "أرز", "rice"],
        "kcal_100g": 130, "protein_g": 2.7, "fat_g": 0.3, "carbs_g": 28.2,
        "source": "reference_cooked", "portion_g": {"small": 100, "medium": 180, "large": 280},
    },
    "pomme_de_terre_bouillie": {
        "aliases": ["pomme de terre", "pommes de terre", "batata", "بطاطا", "potato"],
        "kcal_100g": 87, "protein_g": 1.9, "fat_g": 0.1, "carbs_g": 20.1,
        "source": "reference_cooked", "unit_g": 150,
    },
    "lentilles_cuites": {
        "aliases": ["lentilles", "lentille", "adas", "عدس", "lentils"],
        "kcal_100g": 116, "protein_g": 9.0, "fat_g": 0.4, "carbs_g": 20.1,
        "source": "reference_cooked", "portion_g": {"small": 120, "medium": 200, "large": 300},
    },
    "pois_chiches_cuits": {
        "aliases": ["pois chiches", "pois chiche", "chickpeas"],
        "kcal_100g": 164, "protein_g": 8.9, "fat_g": 2.6, "carbs_g": 27.4,
        "source": "reference_cooked",
    },
    "banane": {
        "aliases": ["banane", "banana", "موز", "mouz"],
        "kcal_100g": 89, "protein_g": 1.1, "fat_g": 0.3, "carbs_g": 22.8,
        "source": "reference_cooked", "unit_g": 120,
        "portion_g": {"small": 90, "medium": 120, "large": 180},
    },
    "pomme": {
        "aliases": ["pomme", "apple", "تفاح", "toffeh"],
        "kcal_100g": 52, "protein_g": 0.3, "fat_g": 0.2, "carbs_g": 13.8,
        "source": "reference_cooked", "unit_g": 150,
        "portion_g": {"small": 100, "medium": 150, "large": 220},
    },
    "orange": {
        "aliases": ["orange", "برتقال", "bordgen", "bortgen"],
        "kcal_100g": 47, "protein_g": 0.9, "fat_g": 0.1, "carbs_g": 11.8,
        "source": "reference_cooked", "unit_g": 150,
        "portion_g": {"small": 100, "medium": 150, "large": 220},
    },
    "datte": {
        "aliases": ["datte", "dattes", "deglet", "deglet nour", "تمر", "tmar"],
        "kcal_100g": 282, "protein_g": 2.5, "fat_g": 0.4, "carbs_g": 75.0,
        "source": "reference_cooked", "unit_g": 8,
        "portion_g": {"small": 24, "medium": 40, "large": 80},
    },
    "lait_entier": {
        "aliases": ["lait", "lait entier", "milk", "حليب", "7lib", "hlib"],
        "kcal_100g": 61, "protein_g": 3.2, "fat_g": 3.3, "carbs_g": 4.8,
        "source": "reference_cooked", "unit_g": 250,
        "portion_g": {"small": 150, "medium": 250, "large": 350},
    },
    "yaourt_nature": {
        "aliases": ["yaourt", "yaourt nature", "yogurt", "yaghourt", "ياغرت", "رايب"],
        "kcal_100g": 61, "protein_g": 3.5, "fat_g": 3.3, "carbs_g": 4.7,
        "source": "reference_cooked", "unit_g": 125,
        "portion_g": {"small": 100, "medium": 125, "large": 250},
    },
    "huile_olive": {
        "aliases": ["huile", "huile d'olive", "zit", "zit zitoun", "زيت", "زيت زيتون", "olive oil"],
        "kcal_100g": 884, "protein_g": 0.0, "fat_g": 100.0, "carbs_g": 0.0,
        "source": "reference_cooked", "unit_g": 13,
        "portion_g": {"small": 5, "medium": 13, "large": 26},
    },
    "sucre": {
        "aliases": ["sucre", "sugar", "sokkor", "سكر"],
        "kcal_100g": 400, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 100.0,
        "source": "reference_cooked", "unit_g": 5,
        "portion_g": {"small": 5, "medium": 10, "large": 20},
    },
    "miel": {
        "aliases": ["miel", "honey", "عسل", "3sal", "asal"],
        "kcal_100g": 304, "protein_g": 0.3, "fat_g": 0.0, "carbs_g": 82.4,
        "source": "reference_cooked", "unit_g": 21,
        "portion_g": {"small": 10, "medium": 21, "large": 40},
    },
}

# =======================================================================
# 4) Produits de marque tunisiens -- échantillon du dataset GitHub
#    (extrait visible publiquement ; jeu complet à récupérer
#    manuellement, voir load_github_branded_csv() plus bas)
# =======================================================================
GITHUB_BRANDED_PRODUCTS = {
    "saida_break_kids_chocolat": {
        "aliases": ["break kids chocolat", "saida break kids"],
        "kcal_100g": 340, "protein_g": 4.5, "fat_g": 12.5, "carbs_g": 52.6,
        "source": "GitHub:Tunisian Food Database (elyesmanai)", "producer": "Saida",
    },
    "saida_plum_cakes": {
        "aliases": ["plum cakes", "plum-cakes", "saida plum cake"],
        "kcal_100g": 359, "protein_g": 5.58, "fat_g": 17.74, "carbs_g": 44.30,
        "source": "GitHub:Tunisian Food Database (elyesmanai)", "producer": "Saida",
    },
    "saida_falfoul_nounours": {
        "aliases": ["falfoul nounours", "chocolat falfoul"],
        "kcal_100g": 364, "protein_g": 0.37, "fat_g": 0.3, "carbs_g": 90.9,
        "source": "GitHub:Tunisian Food Database (elyesmanai)", "producer": "Saida",
    },
}


def load_github_branded_csv(csv_path: str) -> dict:
    """À utiliser une fois le CSV téléchargé manuellement depuis GitHub
    (le fichier est protégé par robots.txt, non récupérable par un outil
    automatisé). Colonnes attendues : Producer,Category,Product,
    Calories (100g),Lipides,Satures,Glucides,Sucre,Protein,Sel,Portion Size.

    Exemple :
        products = load_github_branded_csv("tunisian_food_products.csv")
        register_branded_products(products)
    """
    import csv as csv_module

    def parse_number(value: str):
        if not value:
            return None
        cleaned = re.sub(r"[^\d.,]", "", value).replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    products = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv_module.DictReader(f)
        for row in reader:
            name = (row.get("Product") or "").strip()
            if not name:
                continue
            key = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            products[key] = {
                "aliases": [name.lower()],
                "kcal_100g": parse_number(row.get("Calories (100g)")),
                "protein_g": parse_number(row.get("Protein")),
                "fat_g": parse_number(row.get("Lipides (Fat)")),
                "carbs_g": parse_number(row.get("Glucides (Carbs)")),
                "source": "GitHub:Tunisian Food Database (elyesmanai)",
                "producer": row.get("Producer"),
            }
    return products


# =======================================================================
# 5) Plats tunisiens composites -- ESTIMATIONS INTERNES (pas de source
#    officielle pour un plat composé -- TCAT/CIQUAL/USDA ne couvrent que
#    des ingrédients bruts). À faire valider par un(e) nutritionniste.
#    "kcal_unit" : calories par pièce, utilisé quand l'utilisateur donne
#    une quantité ("2 briks", "3 oeufs").
# =======================================================================
COMPOSITE_DISHES = {
    "couscous_poulet": {
        "aliases": ["couscous poulet", "couscous dajaj", "كسكسي بالدجاج", "كسكسي دجاج"],
        "kcal_small": 450, "kcal_medium": 650, "kcal_large": 900,
        "source": "internal_estimate",
    },
    "couscous_legumes": {
        "aliases": ["couscous", "kosksi", "كسكسي", "couscous khodhra",
                    "couscous vegetarien", "couscous legumes", "كسكسي بالخضرة"],
        "kcal_small": 350, "kcal_medium": 500, "kcal_large": 700,
        "source": "internal_estimate",
    },
    "couscous_viande": {
        "aliases": ["couscous viande", "couscous agneau", "couscous lham", "كسكسي باللحم"],
        "kcal_small": 500, "kcal_medium": 720, "kcal_large": 980,
        "source": "internal_estimate",
    },
    "couscous_poisson": {
        "aliases": ["couscous poisson", "couscous hout", "كسكسي بالحوت"],
        "kcal_small": 420, "kcal_medium": 600, "kcal_large": 830,
        "source": "internal_estimate",
    },
    "mloukhia": {
        "aliases": ["mloukhia", "mloukheya", "ملوخية"],
        "kcal_small": 300, "kcal_medium": 450, "kcal_large": 600,
        "source": "internal_estimate",
    },
    "brik": {
        "aliases": ["brik", "brik a l'oeuf", "brik thon", "بريك"],
        "kcal_small": 200, "kcal_medium": 280, "kcal_large": 350,
        "kcal_unit": 280,
        "source": "internal_estimate",
    },
    "makloub": {
        "aliases": ["makloub", "مقلوب"],
        "kcal_small": 350, "kcal_medium": 500, "kcal_large": 650,
        "kcal_unit": 500,
        "source": "internal_estimate",
    },
    "chorba": {
        "aliases": ["chorba", "soupe", "شربة", "soup"],
        "kcal_small": 150, "kcal_medium": 220, "kcal_large": 300,
        "source": "internal_estimate",
    },
    "tajine_tunisien": {
        "aliases": ["tajine", "tajine tounsi", "طاجين"],
        "kcal_small": 250, "kcal_medium": 380, "kcal_large": 500,
        "source": "internal_estimate",
    },
    "pates_sauce": {
        "aliases": ["pate", "pates", "maqarouna", "makarouna", "ماكرونة", "spaghetti", "pasta"],
        "kcal_small": 350, "kcal_medium": 550, "kcal_large": 750,
        "source": "internal_estimate",
    },
    "salade_mechouia": {
        "aliases": ["mechouia", "salade mechouia", "مشوية"],
        "kcal_small": 100, "kcal_medium": 150, "kcal_large": 200,
        "source": "internal_estimate",
    },
    "salade_verte": {
        "aliases": ["salade", "salade verte", "سلطة", "salad"],
        "kcal_small": 60, "kcal_medium": 100, "kcal_large": 150,
        "source": "internal_estimate",
    },
    "salade_tunisienne": {
        "aliases": ["salade tunisienne", "slata tounsia", "سلطة تونسية"],
        "kcal_small": 150, "kcal_medium": 250, "kcal_large": 350,
        "source": "internal_estimate",
    },
    "poisson_grille": {
        "aliases": ["poisson", "hout", "حوت", "poisson grille", "fish"],
        "kcal_small": 180, "kcal_medium": 280, "kcal_large": 380,
        "source": "internal_estimate",
    },
    "oeufs": {
        "aliases": ["oeuf", "oeufs", "bayd", "baydh", "بيض", "egg", "eggs"],
        "kcal_small": 80, "kcal_medium": 160, "kcal_large": 240,
        "kcal_unit": 78,
        "source": "internal_estimate",
    },
    "ojja": {
        "aliases": ["ojja", "ojja merguez", "عجة"],
        "kcal_small": 300, "kcal_medium": 420, "kcal_large": 580,
        "source": "internal_estimate",
    },
    "pain": {
        "aliases": ["pain", "khobz", "خبز", "baguette", "bread"],
        "kcal_small": 120, "kcal_medium": 200, "kcal_large": 300,
        "source": "internal_estimate",
    },
    "tabouna": {
        "aliases": ["tabouna", "khobz tabouna", "طابونة"],
        "kcal_small": 150, "kcal_medium": 250, "kcal_large": 380,
        "source": "internal_estimate",
    },
    "mlawi": {
        "aliases": ["mlawi", "mlewi", "ملاوي"],
        "kcal_small": 300, "kcal_medium": 420, "kcal_large": 580,
        "kcal_unit": 420,
        "source": "internal_estimate",
    },
    "chapati": {
        "aliases": ["chapati", "chapatti", "شباتي"],
        "kcal_small": 450, "kcal_medium": 600, "kcal_large": 800,
        "kcal_unit": 600,
        "source": "internal_estimate",
    },
    "casse_croute": {
        "aliases": ["casse croute", "kaskrout", "sandwich", "sandwich thon", "كسكروت", "sandwitch"],
        "kcal_small": 450, "kcal_medium": 650, "kcal_large": 900,
        "kcal_unit": 650,
        "source": "internal_estimate",
    },
    "lablabi": {
        "aliases": ["lablabi", "leblebi", "لبلابي"],
        "kcal_small": 350, "kcal_medium": 500, "kcal_large": 650,
        "source": "internal_estimate",
    },
    "kafteji": {
        "aliases": ["kafteji", "kaftaji", "كفتاجي"],
        "kcal_small": 400, "kcal_medium": 550, "kcal_large": 700,
        "source": "internal_estimate",
    },
    "fricasse": {
        "aliases": ["fricasse", "fricassé", "فريكاسي"],
        "kcal_small": 220, "kcal_medium": 300, "kcal_large": 420,
        "kcal_unit": 300,
        "source": "internal_estimate",
    },
    "bambalouni": {
        "aliases": ["bambalouni", "بمبالوني"],
        "kcal_small": 220, "kcal_medium": 300, "kcal_large": 420,
        "kcal_unit": 300,
        "source": "internal_estimate",
    },
    "frites": {
        "aliases": ["frites", "frite", "french fries", "fries", "بطاطا مقلية"],
        "kcal_small": 250, "kcal_medium": 350, "kcal_large": 500,
        "source": "internal_estimate",
    },
    "pizza": {
        "aliases": ["pizza", "بيتزا"],
        "kcal_small": 500, "kcal_medium": 800, "kcal_large": 1100,
        "source": "internal_estimate",
    },
    "burger": {
        "aliases": ["burger", "hamburger", "برقر", "بورقر"],
        "kcal_small": 450, "kcal_medium": 650, "kcal_large": 900,
        "kcal_unit": 650,
        "source": "internal_estimate",
    },
    "viennoiserie": {
        "aliases": ["croissant", "pain au chocolat", "كرواسون"],
        "kcal_small": 200, "kcal_medium": 280, "kcal_large": 400,
        "kcal_unit": 280,
        "source": "internal_estimate",
    },
    "makroudh": {
        "aliases": ["makroudh", "makrouth", "مقروض"],
        "kcal_small": 150, "kcal_medium": 250, "kcal_large": 350,
        "kcal_unit": 150,
        "source": "internal_estimate",
    },
    "fruits": {
        "aliases": ["fruit", "fruits", "ghalla", "غلة"],
        "kcal_small": 60, "kcal_medium": 100, "kcal_large": 150,
        "kcal_unit": 80,
        "source": "internal_estimate",
    },
    "cafe_au_lait": {
        "aliases": ["cafe au lait", "cafe creme", "capucin", "direct", "قهوة بالحليب"],
        "kcal_small": 60, "kcal_medium": 100, "kcal_large": 150,
        "kcal_unit": 100,
        "source": "internal_estimate",
    },
    "the_sucre": {
        "aliases": ["the", "thé", "tay", "شاي", "tea"],
        "kcal_small": 30, "kcal_medium": 60, "kcal_large": 90,
        "kcal_unit": 60,
        "source": "internal_estimate",
    },
    "jus": {
        "aliases": ["jus", "juice", "عصير", "jus d'orange"],
        "kcal_small": 80, "kcal_medium": 120, "kcal_large": 180,
        "kcal_unit": 120,
        "source": "internal_estimate",
    },
    "soda": {
        "aliases": ["soda", "coca", "coca cola", "boga", "fanta", "gazouz", "قازوز"],
        "kcal_small": 100, "kcal_medium": 140, "kcal_large": 210,
        "kcal_unit": 140,
        "source": "internal_estimate",
    },
}

_PORTION_ALIASES = {
    "small": ["small", "petit", "petite", "un peu", "sghir", "شوية", "صغير"],
    "medium": ["medium", "moyen", "moyenne", "wast", "وسط"],
    "large": ["large", "grand", "grande", "beaucoup", "barcha", "kbir", "برشا", "كبير"],
}

# Grammage par défaut quand on matche une entrée "/100g" sans portion
# spécifique (petite ~70g, moyenne ~150g, grande ~250g). Chaque entrée
# peut surcharger avec "portion_g" ou "unit_g".
_PORTION_GRAMS = {"small": 70, "medium": 150, "large": 250}

# Garde-fous contre les quantités aberrantes renvoyées par le LLM
_MAX_QUANTITY = 20
_MAX_GRAMS = 2000

# Mots vides ignorés pour le matching ("couscous au poulet" == "couscous poulet")
_STOP_WORDS = {
    "de", "du", "des", "la", "le", "les", "l", "d", "a", "au", "aux", "un", "une",
    "et", "with", "and", "of", "bel", "bil", "b", "el", "fi",
}

# Ordre de priorité des tables (utilisé seulement pour départager les égalités)
_TABLES = [
    ("composite_dish", COMPOSITE_DISHES),
    ("cooked_reference", COOKED_FOODS),
    ("tcat", TCAT_INGREDIENTS),
    ("ciqual", CIQUAL_INGREDIENTS),
    ("usda", USDA_INGREDIENTS),
    ("github_branded", GITHUB_BRANDED_PRODUCTS),
]


# =======================================================================
# Normalisation & index
# =======================================================================
def _normalize(text: str) -> str:
    """minuscules, sans accents (é->e, œ->oe), sans harakat arabes,
    sans ponctuation, espaces compactés."""
    text = (text or "").lower().replace("œ", "oe").replace("æ", "ae")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("\u0640", "")  # tatweel arabe
    text = re.sub(r"[^\w\s]", " ", text)
    text = text.replace("_", " ")
    return re.sub(r"\s+", " ", text).strip()


def _stem(token: str) -> str:
    # pluriel simple pour l'alphabet latin : oeufs->oeuf, pates->pate
    if len(token) > 3 and token.isascii() and token.endswith(("s", "x")):
        return token[:-1]
    return token


def _tokens(normalized: str) -> frozenset:
    return frozenset(
        _stem(tok) for tok in normalized.split()
        if tok not in _STOP_WORDS and not tok.isdigit()
    )


_INDEX = None


def _build_index():
    index = []
    for priority, (table_name, table) in enumerate(_TABLES):
        for key, entry in table.items():
            candidates = [key.replace("_", " ")] + entry.get("aliases", [])
            for candidate in candidates:
                norm = _normalize(candidate)
                toks = _tokens(norm)
                if not toks:
                    continue
                index.append({
                    "norm": " ".join(sorted(toks)),
                    "tokens": toks,
                    "priority": priority,
                    "table": table_name,
                    "key": key,
                    "entry": entry,
                })
    return index


def _get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    return _INDEX


def rebuild_index():
    """À appeler après avoir modifié une table à l'exécution."""
    global _INDEX
    _INDEX = None
    _match_cached.cache_clear()


def register_branded_products(products: dict):
    GITHUB_BRANDED_PRODUCTS.update(products)
    rebuild_index()


def _score(input_tokens: frozenset, input_norm: str, alias: dict, threshold: float) -> float:
    alias_tokens = alias["tokens"]

    if input_tokens == alias_tokens:
        return 1.0

    # Tous les mots de l'alias sont présents comme MOTS ENTIERS dans
    # l'entrée (évite "pain" dans "épinards", "oeuf" dans "boeuf").
    if alias_tokens <= input_tokens:
        coverage = len(alias_tokens) / len(input_tokens)
        return 0.85 + 0.1 * coverage

    # Fautes de frappe : "mloukheyya", "lablebi"...
    # Même première lettre exigée pour éviter "boeuf" -> "oeuf".
    if input_norm[:1] != alias["norm"][:1]:
        return 0.0
    ratio = SequenceMatcher(None, input_norm, alias["norm"]).ratio()
    if ratio >= threshold:
        return ratio * 0.9

    return 0.0


@lru_cache(maxsize=2048)
def _match_cached(normalized: str, threshold: float):
    input_tokens = _tokens(normalized)
    if not input_tokens:
        return None

    input_norm = " ".join(sorted(input_tokens))
    best, best_rank = None, None

    for alias in _get_index():
        score = _score(input_tokens, input_norm, alias, threshold)
        if score <= 0:
            continue
        # meilleur score, puis alias le plus spécifique, puis priorité de table
        rank = (round(score, 4), len(alias["tokens"]), -alias["priority"])
        if best_rank is None or rank > best_rank:
            best, best_rank = alias, rank

    if best is None or best_rank[0] < threshold:
        return None
    return best["key"], best["table"], best_rank[0]


def normalize_portion(portion_text: str) -> str:
    normalized = _normalize(portion_text)
    for size, aliases in _PORTION_ALIASES.items():
        if any(_normalize(a) in normalized for a in aliases):
            return size
    return "medium"


def match_food_item(item_name: str, threshold: float = 0.75) -> dict:
    """Retourne la meilleure correspondance toutes tables confondues,
    ou {"matched": False, "source": None} si rien n'est trouvé."""
    normalized = _normalize(item_name)
    if not normalized:
        return {"matched": False, "source": None}

    found = _match_cached(normalized, threshold)
    if not found:
        return {"matched": False, "source": None}

    key, table_name, score = found
    entry = dict(_TABLES)[table_name][key]
    return {"matched": True, "key": key, "entry": entry, "table": table_name, "score": score}


def _positive_number(value, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    return min(number, maximum)


def estimate_calories_for_item(
    item_name: str,
    portion_text: str = "medium",
    quantity=None,
    grams=None,
) -> dict:
    portion = normalize_portion(portion_text)
    qty = _positive_number(quantity, _MAX_QUANTITY)
    grams_given = _positive_number(grams, _MAX_GRAMS)
    match = match_food_item(item_name)

    base = {
        "item": item_name,
        "portion": portion,
        "quantity": qty,
        "grams": grams_given,
    }

    if not match["matched"]:
        return {
            **base,
            "matched_food": None,
            "estimated_calories": None,
            "source": "llm_fallback_needed",
            "confidence": "low",
        }

    entry = match["entry"]

    if match["table"] == "composite_dish":
        if qty and entry.get("kcal_unit"):
            calories = entry["kcal_unit"] * qty
        else:
            calories = entry[f"kcal_{portion}"] * (qty or 1)
        confidence = "medium"
    else:
        kcal_per_100g = entry.get("kcal_100g")
        if grams_given:
            grams_used = grams_given
        elif qty and entry.get("unit_g"):
            grams_used = entry["unit_g"] * qty
        else:
            grams_used = entry.get("portion_g", _PORTION_GRAMS)[portion] * (qty or 1)
        calories = (
            kcal_per_100g * grams_used / 100
            if kcal_per_100g is not None else None
        )
        # une valeur crue appliquée à un aliment probablement cuit reste approximative
        confidence = "medium" if entry.get("state") == "raw" else "high"

    return {
        **base,
        "matched_food": match["key"],
        "match_score": match["score"],
        "estimated_calories": round(calories) if calories is not None else None,
        "source": entry.get("source", match["table"]),
        "confidence": confidence,
    }


def estimate_meal_calories(food_items: list[dict]) -> dict:
    """food_items: [{"name": "couscous poulet", "portion": "medium",
                     "quantity": null, "grams": null}, ...]"""
    results = [
        estimate_calories_for_item(
            item.get("name", ""),
            item.get("portion", "medium"),
            item.get("quantity"),
            item.get("grams"),
        )
        for item in (food_items or [])
        if isinstance(item, dict) and (item.get("name") or "").strip()
    ]

    known_total = sum(r["estimated_calories"] for r in results if r["estimated_calories"] is not None)
    unknown_items = [r["item"] for r in results if r["estimated_calories"] is None]

    if not results:
        confidence = "low"
    elif not unknown_items:
        confidence = "high"
    elif known_total > 0:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "items": results,
        "known_calories_total": known_total,
        "items_needing_llm_estimate": unknown_items,
        "confidence": confidence,
    }