import json
import os
from datetime import datetime
import uuid
from flask import Flask, render_template, request, redirect, session, jsonify

from services.recommendation import recommend_outfit, recommend_multiple
from services.analytics import full_analytics
from services.weather_engine import get_weather
from services.compatibility import outfit_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_PATH = os.path.join(DATA_DIR, "users.json")
CLOTHES_PATH = os.path.join(DATA_DIR, "clothes.json")
SECTIONS_PATH = os.path.join(DATA_DIR, "sections.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev_key")


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
# ---------------------------------------------------
# Utilities
# ---------------------------------------------------

def load_json(path):

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------
# Authentication Helpers
# ---------------------------------------------------

def find_user_by_email(email):

    users = load_json(USERS_PATH).get("users", [])

    for user in users:
        if user["email"] == email:
            return user

    return None


def get_current_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    users = load_json(USERS_PATH).get("users", [])

    for user in users:
        if user["user_id"] == user_id:
            return user

    return None


def require_login():

    if "user_id" not in session:
        return False

    return True


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.route("/")
def home():

    if require_login():
        return redirect("/dashboard")

    return redirect("/login")


# ---------------------------------------------------
# Login
# ---------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = find_user_by_email(email)

        if not user:
            return render_template("login.html", error="User not found")

        if user["password_hash"] != password:
            return render_template("login.html", error="Incorrect password")

        session["user_id"] = user["user_id"]

        return redirect("/dashboard")

    return render_template("login.html")


# ---------------------------------------------------
# Register
# ---------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        users_data = load_json(USERS_PATH)
        users = users_data.get("users", [])

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user_id = "U" + str(len(users) + 1).zfill(3)

        new_user = {
            "user_id": user_id,
            "username": username,
            "full_name": username,
            "email": email,
            "password_hash": password,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "profile": {
                "location": "Pune"
            }
        }

        users.append(new_user)

        users_data["users"] = users

        save_json(USERS_PATH, users_data)

        return redirect("/login")

    return render_template("register.html")


# ---------------------------------------------------
# Logout
# ---------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------------------------------------------
# Dashboard
# ---------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    user = {
        "user_id": user_id,
        "username": "User"
    }

    with open("data/clothes.json") as f:
        db = json.load(f)

    clothes = [c for c in db["clothes"] if c["user_id"] == user_id]

    # simple outfit suggestion (top + bottom)
    tops = [c for c in clothes if c["category"] == "top"]
    bottoms = [c for c in clothes if c["category"] == "bottom"]

    recommendation = None

    if tops and bottoms:
        recommendation = {
            "top": tops[0],
            "bottom": bottoms[0]
        }

    weather = {
        "temperature": 26,
        "condition": "clear"
    }

    return render_template(
        "dashboard.html",
        user=user,
        clothes=clothes,
        weather=weather,
        recommendation=recommendation
    )

# ---------------------------------------------------
# Planner Page
# ---------------------------------------------------

@app.route("/planner")
def planner():

    if not require_login():
        return redirect("/login")

    user = get_current_user()

    clothes = load_json(CLOTHES_PATH).get("clothes", [])

    user_clothes = [c for c in clothes if c["user_id"] == user["user_id"]]

    return render_template(
        "planner.html",
        clothes=user_clothes
    )


# ---------------------------------------------------
# Analytics Page
# ---------------------------------------------------

@app.route("/analytics")
def analytics_page():

    if not require_login():
        return redirect("/login")

    return render_template("analytics.html")


# ---------------------------------------------------
# API: Outfit Recommendation
# ---------------------------------------------------

@app.route("/api/recommend")
def api_recommend():

    if not require_login():
        return jsonify({"error": "not logged in"})

    user_id = session["user_id"]

    outfit = recommend_outfit(user_id)

    return jsonify(outfit)


# ---------------------------------------------------
# API: Multiple Recommendations
# ---------------------------------------------------

@app.route("/api/recommend/multiple")
def api_recommend_multiple():

    if not require_login():
        return jsonify({"error": "not logged in"})

    user_id = session["user_id"]

    outfits = recommend_multiple(user_id)

    return jsonify(outfits)


# ---------------------------------------------------
# API: Analytics
# ---------------------------------------------------

@app.route("/api/analytics")
def api_analytics():

    if "user_id" not in session:
        return jsonify({"error": "not logged in"})

    user_id = session["user_id"]

    with open("data/clothes.json") as f:
        db = json.load(f)

    clothes = [c for c in db["clothes"] if c["user_id"] == user_id]

    total_clothes = len(clothes)

    worn = [c for c in clothes if c.get("status") == "worn"]

    category_distribution = {}

    for c in clothes:

        cat = c.get("category", "other")

        if cat not in category_distribution:
            category_distribution[cat] = 0

        category_distribution[cat] += 1

    most_worn = sorted(
        clothes,
        key=lambda x: x.get("wear_count", 0),
        reverse=True
    )[:5]

    least_worn = sorted(
        clothes,
        key=lambda x: x.get("wear_count", 0)
    )[:5]

    heatmap = {}

    for i in range(60):
        heatmap[str(i)] = 1 if i < len(worn) else 0

    return jsonify({

        "wardrobe_stats": {
            "total_clothes": total_clothes,
            "total_outfits_worn": len(worn),
            "favorite_category": max(category_distribution, key=category_distribution.get) if category_distribution else "-"
        },

        "category_distribution": category_distribution,

        "weekly_usage": {
            "Week 1": 2,
            "Week 2": 3,
            "Week 3": 4,
            "Week 4": 1
        },

        "most_worn_items": most_worn,
        "least_worn_items": least_worn,

        "not_worn_long_time": [],

        "heatmap": heatmap

    })

# ---------------------------------------------------
# API: Wardrobe
# ---------------------------------------------------

@app.route("/api/wardrobe")
def api_wardrobe():

    if not require_login():
        return jsonify({"error": "not logged in"})

    user = get_current_user()

    clothes = load_json(CLOTHES_PATH).get("clothes", [])

    user_clothes = [c for c in clothes if c["user_id"] == user["user_id"]]

    return jsonify(user_clothes)

@app.route("/api/clothes/add", methods=["POST"])
def add_cloth():

    data = request.json

    with open("data/clothes.json") as f:
        db = json.load(f)

    new_item = {
        "id": str(uuid.uuid4()),
        "user_id": session["user_id"],
        "name": data["name"],
        "section": data["section"],
        "color": data["color"],
        "status": "unworn",
        "wear_count": 0
    }

    db["clothes"].append(new_item)

    with open("data/clothes.json","w") as f:
        json.dump(db,f,indent=2)

    return jsonify({"success":True})


@app.route("/api/clothes/delete/<cloth_id>", methods=["DELETE"])
def delete_cloth(cloth_id):

    with open("data/clothes.json") as f:
        db=json.load(f)

    db["clothes"]=[c for c in db["clothes"] if c["id"]!=cloth_id]

    with open("data/clothes.json","w") as f:
        json.dump(db,f,indent=2)

    return jsonify({"success":True})
# ---------------------------------------------------
# Outfit History Logging
# ---------------------------------------------------
@app.route("/wardrobe")
def wardrobe():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    with open("data/clothes.json") as f:
        data = json.load(f)

    clothes = [c for c in data["clothes"] if c["user_id"] == user_id]

    return render_template("wardrobe.html", clothes=clothes)



@app.route("/api/wear", methods=["POST"])
def log_outfit():

    if not require_login():
        return jsonify({"error": "not logged in"})

    data = request.json

    history_data = load_json(HISTORY_PATH)
    history = history_data.get("wear_history", [])

    history_id = "H" + str(len(history) + 1).zfill(3)

    record = {
        "history_id": history_id,
        "user_id": session["user_id"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "outfit": data.get("outfit"),
        "temperature": data.get("temperature", 25),
        "weather_condition": data.get("weather", "clear"),
        "occasion": "casual",
        "planner_generated": False,
        "recommended_by_ai": True,
        "user_rating": 5
    }

    history.append(record)

    history_data["wear_history"] = history

    save_json(HISTORY_PATH, history_data)

    return jsonify({"status": "saved"})

# ---------------------------------------------------
# Toggle Worn / Unworn Status
# ---------------------------------------------------
from datetime import datetime

@app.route("/api/clothes/toggle/<cloth_id>", methods=["POST"])
def toggle_cloth(cloth_id):

    with open("data/clothes.json") as f:
        db = json.load(f)

    for cloth in db["clothes"]:

        if cloth["id"] == cloth_id:

            if cloth.get("status") == "worn":

                cloth["status"] = "unworn"

            else:

                cloth["status"] = "worn"
                cloth["wear_count"] = cloth.get("wear_count", 0) + 1
                cloth["last_worn"] = datetime.now().strftime("%Y-%m-%d")

    with open("data/clothes.json", "w") as f:
        json.dump(db, f, indent=2)

    return jsonify({"success": True})

# ---------------------------------------------------
# Modify Clothing Item (Update Name)
# ---------------------------------------------------

@app.route("/api/clothes/update/<cloth_id>", methods=["POST"])
def update_cloth(cloth_id):

    data = request.json

    with open("data/clothes.json") as f:
        db = json.load(f)

    for cloth in db["clothes"]:

        if cloth["id"] == cloth_id:

            cloth["name"] = data.get("name", cloth["name"])

    with open("data/clothes.json", "w") as f:
        json.dump(db, f, indent=2)

    return jsonify({"success": True})


@app.route("/api/analytics")
def analytics_api():

    with open("data/clothes.json") as f:
        db = json.load(f)

    user_id = session["user_id"]

    clothes = [c for c in db["clothes"] if c["user_id"] == user_id]

    total_clothes = len(clothes)

    worn = len([c for c in clothes if c.get("status") == "worn"])

    category_counts = {}

    for c in clothes:

        cat = c.get("category", "other")

        if cat not in category_counts:
            category_counts[cat] = 0

        category_counts[cat] += 1

    most_worn = sorted(
        clothes,
        key=lambda x: x.get("wear_count", 0),
        reverse=True
    )[:5]

    least_worn = sorted(
        clothes,
        key=lambda x: x.get("wear_count", 0)
    )[:5]

    return jsonify({

        "wardrobe_stats": {
            "total_clothes": total_clothes,
            "total_outfits_worn": worn,
            "favorite_category": max(category_counts, key=category_counts.get) if category_counts else "-"
        },

        "category_distribution": category_counts,

        "weekly_usage": {
            "Week 1": 2,
            "Week 2": 3,
            "Week 3": 4,
            "Week 4": 1
        },

        "most_worn_items": most_worn,
        "least_worn_items": least_worn,

        "not_worn_long_time": [],

        "heatmap": {str(i): 1 for i in range(60)}

    })


# ---------------------------------------------------
# Save Weekly Planner
# ---------------------------------------------------

# ---------------------------------------------------
# Save Planner
# ---------------------------------------------------

# ---------------------------------------------------
# Save Planner
# ---------------------------------------------------

@app.route("/api/planner/save", methods=["POST"])
def save_planner():

    if "user_id" not in session:
        return jsonify({"error": "not logged in"})

    user_id = session["user_id"]

    plan = request.json

    try:

        with open("data/planner.json") as f:
            db = json.load(f)

    except:
        db = {"plans": []}

    # remove old plan
    db["plans"] = [p for p in db["plans"] if p["user_id"] != user_id]

    db["plans"].append({
        "user_id": user_id,
        "plan": plan
    })

    with open("data/planner.json", "w") as f:
        json.dump(db, f, indent=2)

    return jsonify({"success": True})

# ---------------------------------------------------
# Load Planner
# ---------------------------------------------------
# ---------------------------------------------------
# Load Planner
# ---------------------------------------------------

@app.route("/api/planner/load")
def load_planner():

    if "user_id" not in session:
        return jsonify({})

    user_id = session["user_id"]

    try:

        with open("data/planner.json") as f:
            db = json.load(f)

    except:
        return jsonify({})

    for p in db["plans"]:

        if p["user_id"] == user_id:
            return jsonify(p["plan"])

    return jsonify({})

   
# ---------------------------------------------------
# Start Server
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
