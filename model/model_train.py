import json
import os
import pickle
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLOTHES_PATH = os.path.join(BASE_DIR, "data", "clothes.json")
HISTORY_PATH = os.path.join(BASE_DIR, "data", "history.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "recommender.pkl")


# ---------------------------------------------------
# Load JSON
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
# Build Lookup
# ---------------------------------------------------

def build_lookup(clothes):

    lookup = {}

    for c in clothes:
        lookup[c["id"]] = c

    return lookup


# ---------------------------------------------------
# Build Dataset
# ---------------------------------------------------

def build_dataset(clothes, history):

    lookup = build_lookup(clothes)

    rows = []

    for record in history:

        outfit = record["outfit"]

        top = lookup.get(outfit.get("top"))
        bottom = lookup.get(outfit.get("bottom"))
        outerwear = lookup.get(outfit.get("outerwear"))
        footwear = lookup.get(outfit.get("footwear"))

        if not top or not bottom:
            continue

        row = {}

        row["top_color"] = top.get("color")
        row["bottom_color"] = bottom.get("color")

        row["top_material"] = top.get("material")
        row["bottom_material"] = bottom.get("material")

        row["top_pattern"] = top.get("pattern")
        row["bottom_pattern"] = bottom.get("pattern")

        row["top_category"] = top.get("category")
        row["bottom_category"] = bottom.get("category")

        row["outerwear_material"] = outerwear.get("material") if outerwear else "none"
        row["outerwear_color"] = outerwear.get("color") if outerwear else "none"

        row["footwear_color"] = footwear.get("color") if footwear else "none"

        row["temperature"] = record.get("temperature", 25)
        row["weather"] = record.get("weather_condition", "clear")
        row["occasion"] = record.get("occasion", "casual")

        rating = record.get("user_rating", 3)

        row["liked_outfit"] = 1 if rating >= 4 else 0

        rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------
# Encode Categorical
# ---------------------------------------------------

def encode_dataframe(df):

    encoders = {}

    for column in df.columns:

        if column == "liked_outfit":
            continue

        encoder = LabelEncoder()

        df[column] = encoder.fit_transform(df[column].astype(str))

        encoders[column] = encoder

    return df, encoders


# ---------------------------------------------------
# Train Model
# ---------------------------------------------------

def train():

    clothes = load_clothes()
    history = load_history()

    if len(history) == 0:
        raise Exception("history.json contains no training data")

    df = build_dataset(clothes, history)

    df, encoders = encode_dataframe(df)

    X = df.drop("liked_outfit", axis=1)
    y = df["liked_outfit"]

    # Ensure everything is numeric
    X = X.astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42
    )

    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)

    print("Model accuracy:", accuracy)

    payload = {
        "model": model,
        "encoders": encoders
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(payload, f)

    print("Model saved:", MODEL_PATH)


# ---------------------------------------------------
# Run
# ---------------------------------------------------

if __name__ == "__main__":

    print("Training ClosetFlow model...")

    train()

    print("Training complete.")