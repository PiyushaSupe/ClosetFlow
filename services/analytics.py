import json
import os
from collections import defaultdict
from datetime import datetime, timedelta


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLOTHES_PATH = os.path.join(BASE_DIR, "data", "clothes.json")
HISTORY_PATH = os.path.join(BASE_DIR, "data", "history.json")


# ---------------------------------------------------
# Utilities
# ---------------------------------------------------

def load_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def load_clothes():
    return load_json(CLOTHES_PATH).get("clothes", [])


def load_history():
    return load_json(HISTORY_PATH).get("wear_history", [])


# ---------------------------------------------------
# User Filters
# ---------------------------------------------------

def get_user_clothes(user_id):

    clothes = load_clothes()

    return [c for c in clothes if c["user_id"] == user_id]


def get_user_history(user_id):

    history = load_history()

    return [h for h in history if h["user_id"] == user_id]


# ---------------------------------------------------
# Category Distribution
# ---------------------------------------------------

def category_distribution(user_id):

    clothes = get_user_clothes(user_id)

    distribution = defaultdict(int)

    for item in clothes:
        distribution[item["category"]] += 1

    return dict(distribution)


# ---------------------------------------------------
# Most Worn Items
# ---------------------------------------------------

def most_worn_items(user_id, limit=5):

    clothes = get_user_clothes(user_id)

    sorted_items = sorted(
        clothes,
        key=lambda x: x.get("wear_count", 0),
        reverse=True
    )

    return sorted_items[:limit]


# ---------------------------------------------------
# Least Worn Items
# ---------------------------------------------------

def least_worn_items(user_id, limit=5):

    clothes = get_user_clothes(user_id)

    sorted_items = sorted(
        clothes,
        key=lambda x: x.get("wear_count", 0)
    )

    return sorted_items[:limit]


# ---------------------------------------------------
# Not Worn For Long Time
# ---------------------------------------------------

def days_since(date_str):

    if not date_str:
        return 999

    last = datetime.strptime(date_str, "%Y-%m-%d")

    return (datetime.now() - last).days


def not_worn_long_time(user_id, threshold=30):

    clothes = get_user_clothes(user_id)

    results = []

    for item in clothes:

        days = days_since(item.get("last_worn"))

        if days >= threshold:
            results.append({
                "item": item,
                "days_unused": days
            })

    return sorted(results, key=lambda x: x["days_unused"], reverse=True)


# ---------------------------------------------------
# Wear Frequency By Clothing
# ---------------------------------------------------

def wear_frequency(user_id):

    history = get_user_history(user_id)

    counter = defaultdict(int)

    for record in history:

        outfit = record["outfit"]

        for key in outfit:

            item_id = outfit[key]

            if item_id:
                counter[item_id] += 1

    return dict(counter)


# ---------------------------------------------------
# Weekly Usage Trends
# ---------------------------------------------------

def weekly_usage(user_id):

    history = get_user_history(user_id)

    weekly = defaultdict(int)

    for record in history:

        date = datetime.strptime(record["date"], "%Y-%m-%d")

        week = date.strftime("%Y-W%U")

        weekly[week] += 1

    return dict(weekly)


# ---------------------------------------------------
# Daily Wear Heatmap
# ---------------------------------------------------

def wear_heatmap(user_id):

    history = get_user_history(user_id)

    heatmap = defaultdict(int)

    for record in history:

        date = record["date"]

        heatmap[date] += 1

    return dict(heatmap)


# ---------------------------------------------------
# Outfit Combination Trends
# ---------------------------------------------------

def outfit_combinations(user_id):

    history = get_user_history(user_id)

    combos = defaultdict(int)

    for record in history:

        outfit = record["outfit"]

        combo = tuple(sorted([
            outfit.get("top"),
            outfit.get("bottom"),
            outfit.get("outerwear"),
            outfit.get("footwear")
        ]))

        combos[combo] += 1

    sorted_combos = sorted(
        combos.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_combos[:10]


# ---------------------------------------------------
# Overall Wardrobe Stats
# ---------------------------------------------------

def wardrobe_stats(user_id):

    clothes = get_user_clothes(user_id)
    history = get_user_history(user_id)

    total_clothes = len(clothes)
    total_outfits = len(history)

    categories = category_distribution(user_id)

    most_used_category = None
    if categories:
        most_used_category = max(categories, key=categories.get)

    return {
        "total_clothes": total_clothes,
        "total_outfits_worn": total_outfits,
        "category_distribution": categories,
        "favorite_category": most_used_category
    }


# ---------------------------------------------------
# Full Analytics Package
# ---------------------------------------------------

def full_analytics(user_id):

    return {

        "wardrobe_stats": wardrobe_stats(user_id),

        "category_distribution": category_distribution(user_id),

        "most_worn_items": most_worn_items(user_id),

        "least_worn_items": least_worn_items(user_id),

        "not_worn_long_time": not_worn_long_time(user_id),

        "wear_frequency": wear_frequency(user_id),

        "weekly_usage": weekly_usage(user_id),

        "heatmap": wear_heatmap(user_id),

        "top_outfit_combinations": outfit_combinations(user_id)
    }