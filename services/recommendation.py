import json
import os
import pickle
import random
from datetime import datetime

from services.compatibility import compatibility_score
from services.weather_engine import get_weather_temperature


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLOTHES_PATH = os.path.join(BASE_DIR, "data", "clothes.json")
HISTORY_PATH = os.path.join(BASE_DIR, "data", "history.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "recommender.pkl")


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


def load_model():

    if not os.path.exists(MODEL_PATH):
        return None

    with open(MODEL_PATH, "rb") as f:
        payload = pickle.load(f)

    return payload


# ---------------------------------------------------
# Wardrobe Filters
# ---------------------------------------------------

def get_user_clothes(user_id):

    clothes = load_clothes()

    return [c for c in clothes if c["user_id"] == user_id]


def split_by_category(clothes):

    tops = []
    bottoms = []
    outerwear = []
    footwear = []
    accessories = []

    for c in clothes:

        if c["category"] == "top":
            tops.append(c)

        elif c["category"] == "bottom":
            bottoms.append(c)

        elif c["category"] == "outerwear":
            outerwear.append(c)

        elif c["category"] == "footwear":
            footwear.append(c)

        elif c["category"] == "accessory":
            accessories.append(c)

    return tops, bottoms, outerwear, footwear, accessories


# ---------------------------------------------------
# Recently Worn Logic
# ---------------------------------------------------

def days_since(date_string):

    if not date_string:
        return 100

    last = datetime.strptime(date_string, "%Y-%m-%d")

    delta = datetime.now() - last

    return delta.days


def wear_penalty(item):

    days = days_since(item.get("last_worn"))

    if days < 2:
        return -15

    if days < 5:
        return -5

    return 0


def unused_bonus(item):

    days = days_since(item.get("last_worn"))

    if days > 30:
        return 20

    if days > 10:
        return 10

    return 0


# ---------------------------------------------------
# Weather Filtering
# ---------------------------------------------------

def weather_match_score(item, temperature):

    min_t, max_t = item.get("temperature_range", [0, 40])

    if min_t <= temperature <= max_t:
        return 10

    return -10


# ---------------------------------------------------
# Outfit Feature Vector
# ---------------------------------------------------

def build_feature_vector(top, bottom, outerwear, footwear, temperature):

    features = {}

    features["top_color"] = top["color"]
    features["bottom_color"] = bottom["color"]

    features["top_material"] = top["material"]
    features["bottom_material"] = bottom["material"]

    features["top_pattern"] = top["pattern"]
    features["bottom_pattern"] = bottom["pattern"]

    features["top_category"] = top["category"]
    features["bottom_category"] = bottom["category"]

    if outerwear:
        features["outerwear_material"] = outerwear["material"]
        features["outerwear_color"] = outerwear["color"]
    else:
        features["outerwear_material"] = "none"
        features["outerwear_color"] = "none"

    if footwear:
        features["footwear_color"] = footwear["color"]
    else:
        features["footwear_color"] = "none"

    features["temperature"] = temperature
    features["weather"] = "clear"
    features["occasion"] = "casual"

    return features


# ---------------------------------------------------
# ML Score
# ---------------------------------------------------
def ml_score(model_payload, features):

    if not model_payload:
        return 0

    model = model_payload["model"]
    encoders = model_payload["encoders"]

    X = []

    for key in features:

        val = features[key]

        if key in encoders:

            encoder = encoders[key]

            try:
                val = encoder.transform([str(val)])[0]
            except:
                val = 0

        X.append(val)

    try:

        probs = model.predict_proba([X])

        # if model trained with only one class
        if probs.shape[1] == 1:
            return probs[0][0] * 100

        return probs[0][1] * 100

    except Exception as e:

        print("ML scoring fallback:", e)

        return 0
# ---------------------------------------------------
# Generate Outfit Combinations
# ---------------------------------------------------

def generate_outfits(tops, bottoms, outerwear, footwear):

    outfits = []

    for top in tops:
        for bottom in bottoms:

            if footwear:

                for shoe in footwear:

                    outfits.append((top, bottom, None, shoe))

            if outerwear:

                for jacket in outerwear:
                    outfits.append((top, bottom, jacket, None))

    return outfits


# ---------------------------------------------------
# Outfit Scoring
# ---------------------------------------------------

def score_outfit(outfit, temperature, model_payload):

    top, bottom, outerwear, footwear = outfit

    score = 0

    score += compatibility_score(top, bottom)

    if outerwear:
        score += compatibility_score(top, outerwear)

    score += wear_penalty(top)
    score += wear_penalty(bottom)

    score += unused_bonus(top)
    score += unused_bonus(bottom)

    score += weather_match_score(top, temperature)
    score += weather_match_score(bottom, temperature)

    features = build_feature_vector(top, bottom, outerwear, footwear, temperature)

    score += ml_score(model_payload, features)

    return score


# ---------------------------------------------------
# Recommend Outfit
# ---------------------------------------------------

def recommend_outfit(user_id):

    clothes = get_user_clothes(user_id)

    tops, bottoms, outerwear, footwear, accessories = split_by_category(clothes)

    if not tops or not bottoms:
        return None

    temperature = get_weather_temperature()

    outfits = generate_outfits(tops, bottoms, outerwear, footwear)

    model_payload = load_model()

    best_score = -999
    best_outfit = None

    for outfit in outfits:

        score = score_outfit(outfit, temperature, model_payload)

        if score > best_score:
            best_score = score
            best_outfit = outfit

    return format_outfit(best_outfit, best_score)


# ---------------------------------------------------
# Random Outfit
# ---------------------------------------------------

def random_outfit(user_id):

    clothes = get_user_clothes(user_id)

    tops, bottoms, outerwear, footwear, accessories = split_by_category(clothes)

    if not tops or not bottoms:
        return None

    outfit = {
        "top": random.choice(tops),
        "bottom": random.choice(bottoms),
        "outerwear": random.choice(outerwear) if outerwear else None,
        "footwear": random.choice(footwear) if footwear else None
    }

    return outfit


# ---------------------------------------------------
# Outfit Formatter
# ---------------------------------------------------

def format_outfit(outfit, score):

    if not outfit:
        return None

    top, bottom, outerwear, footwear = outfit

    return {

        "top": top,
        "bottom": bottom,
        "outerwear": outerwear,
        "footwear": footwear,

        "compatibility_score": round(score, 2),

        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# ---------------------------------------------------
# Suggest Multiple Outfits
# ---------------------------------------------------

def recommend_multiple(user_id, limit=5):

    clothes = get_user_clothes(user_id)

    tops, bottoms, outerwear, footwear, accessories = split_by_category(clothes)

    temperature = get_weather_temperature()

    outfits = generate_outfits(tops, bottoms, outerwear, footwear)

    model_payload = load_model()

    scored = []

    for outfit in outfits:

        score = score_outfit(outfit, temperature, model_payload)

        scored.append((outfit, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    results = []

    for outfit, score in scored[:limit]:

        results.append(format_outfit(outfit, score))

    return results