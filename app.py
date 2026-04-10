from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import pickle
import pandas as pd
from functools import wraps
import os

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    static_url_path='/static',
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)
app.secret_key = "super-secret-key-123"  # Replace with a secure random secret in production

# Load model
model = pickle.load(open("model/model.pkl", "rb"))

# Simple in-memory user store (replace with DB for production)
USERS = {
    "admin": "admin123",
    "user": "password"
}

# Helpers
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to continue", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def build_prediction_payload(data):
    required = ["Store", "Product", "Customers", "Promo", "Holiday", "Day", "Month", "Year"]
    if not isinstance(data, dict):
        raise ValueError("Payload must be JSON object with keys: %s" % ", ".join(required))

    payload = {}
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    try:
        payload["Store"] = int(data["Store"])
        product = data["Product"]
        if str(product).upper() not in ["A", "B"]:
            raise ValueError("Product must be 'A' or 'B'")
        payload["Product"] = 0 if str(product).upper() == "A" else 1
        payload["Customers"] = int(data["Customers"])
        payload["Promo"] = int(data["Promo"])
        payload["Holiday"] = int(data["Holiday"])
        payload["Day"] = int(data["Day"])
        payload["Month"] = int(data["Month"])
        payload["Year"] = int(data["Year"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid field value: {exc}") from exc

    return payload

@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("All fields are required", "danger")
            return redirect(url_for("login"))

        if USERS.get(username) == password:
            session["logged_in"] = True
            session["username"] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    try:
        df = pd.read_csv("data/sales.csv", parse_dates=["Date"])
        summary = {
            "total_records": len(df),
            "total_sales": float(df["Sales"].sum()),
            "avg_sales": float(df["Sales"].mean()),
            "total_customers": int(df["Customers"].sum()),
            "promo_count": int(df["Promo"].sum())
        }
        monthly_stats = df.groupby(df["Date"].dt.to_period("M"))["Sales"].sum().reset_index()
        monthly_stats["Date"] = monthly_stats["Date"].astype(str)
        monthly_stats = monthly_stats.to_dict(orient="records")

        return render_template("dashboard.html", summary=summary, monthly_stats=monthly_stats)
    except Exception as err:
        app.logger.error(f"Dashboard data load failed: {err}")
        flash("Unable to load dashboard data. Please try again later.", "danger")
        return render_template("dashboard.html", summary={}, monthly_stats=[])

@app.route("/predict", methods=["POST"])
def api_predict():
    if not request.is_json:
        return jsonify({"error": "JSON payload required"}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        payload = build_prediction_payload(data)
        df = pd.DataFrame([payload])
        result = model.predict(df)
        return jsonify({"Sales": float(result[0])})
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as err:
        app.logger.error(f"Predict API error: {err}")
        return jsonify({"error": "Prediction failed"}), 500

@app.route("/predict_page", methods=["GET", "POST"])
@login_required
def predict_page():
    prediction = None

    if request.method == "POST":
        try:
            form = request.form
            form_input = {
                "Store": form.get("store"),
                "Product": form.get("product"),
                "Customers": form.get("customers"),
                "Promo": form.get("promo"),
                "Holiday": form.get("holiday"),
                "Day": form.get("day"),
                "Month": form.get("month"),
                "Year": form.get("year")
            }

            payload = build_prediction_payload(form_input)
            df = pd.DataFrame([payload])
            result = model.predict(df)
            prediction = float(result[0])
            flash(f"Predicted sales: {prediction:.2f}", "success")
        except ValueError as err:
            app.logger.warning(f"Prediction failed: {err}")
            flash(str(err), "danger")
        except Exception as err:
            app.logger.error(f"Prediction failed: {err}")
            flash("Prediction failed. Check input values and try again.", "danger")

    return render_template("predict.html", prediction=prediction)

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", code=500, message="Server error, try again later"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5500)