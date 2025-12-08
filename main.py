from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json

app = Flask(__name__)
app.secret_key = "change-this-secret-key"   # fine for now

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

MENU_PATH = os.path.join(DATA_DIR, "menu.json")


# ---------- Helpers to load / save menu ----------
def load_menu():
    if not os.path.exists(MENU_PATH):
        return []
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_menu(menu):
    with open(MENU_PATH, "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=2)


# ---------- Public API for frontend ----------
@app.route("/api/menu")
def api_menu():
    """Return all dishes as JSON for FoodGalaxy frontend."""
    menu = load_menu()
    return jsonify(menu)


# ---------- Health (optional) ----------
@app.route("/health")
def health():
    return {"status": "ok"}, 200


# ---------- Customer Home ----------
@app.route("/")
def home():
    return render_template("food.html")


# ---------- Admin login ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # simple fixed creds – you said you’re fine with this
        if username == "shirlyn" and password == "2806":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("admin_login.html", error=error)


# ---------- Admin dashboard (list + edit/delete) ----------
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    menu = load_menu()
    # Sort by category then name just to look neat
    menu_sorted = sorted(menu, key=lambda x: (x.get("category", ""), x.get("name", "")))
    return render_template("admin_dashboard.html", menu=menu_sorted)


# ---------- Add dish from admin ----------
@app.route("/admin/add-dish", methods=["POST"])
def admin_add_dish():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    menu = load_menu()

    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    category = request.form.get("category", "").strip()
    calories = request.form.get("calories", "").strip()
    image = request.form.get("image", "").strip()

    if not name or not price or not category:
        # simple check; you can show better errors later
        return redirect(url_for("admin_dashboard"))

    try:
        price_val = int(price)
    except ValueError:
        price_val = 0

    try:
        calories_val = int(calories) if calories else 0
    except ValueError:
        calories_val = 0

    # generate new ID
    existing_ids = [item.get("id", 0) for item in menu]
    new_id = (max(existing_ids) + 1) if existing_ids else 1

    new_item = {
        "id": new_id,
        "name": name,
        "category": category,
        "price": price_val,
        "calories": calories_val,
        "image": image
    }
    menu.append(new_item)
    save_menu(menu)

    return redirect(url_for("admin_dashboard"))


# ---------- Edit dish ----------
@app.route("/admin/dish/<int:dish_id>/edit", methods=["POST"])
def admin_edit_dish(dish_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    menu = load_menu()
    for item in menu:
        if item.get("id") == dish_id:
            item["name"] = request.form.get("name", item.get("name", "")).strip()
            item["category"] = request.form.get("category", item.get("category", "")).strip()

            price = request.form.get("price", "")
            try:
                item["price"] = int(price) if price else item.get("price", 0)
            except ValueError:
                pass

            calories = request.form.get("calories", "")
            try:
                item["calories"] = int(calories) if calories else item.get("calories", 0)
            except ValueError:
                pass

            image = request.form.get("image", "")
            if image:
                item["image"] = image.strip()
            break

    save_menu(menu)
    return redirect(url_for("admin_dashboard"))


# ---------- Delete dish ----------
@app.route("/admin/dish/<int:dish_id>/delete", methods=["POST"])
def admin_delete_dish(dish_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    menu = load_menu()
    menu = [item for item in menu if item.get("id") != dish_id]
    save_menu(menu)

    return redirect(url_for("admin_dashboard"))


# ---------- Logout ----------
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)
