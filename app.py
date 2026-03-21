import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from weather_service import get_weather_forecast
from advisory_engine import generate_weather_advisory
from market_service import get_market_data, generate_market_advice   # ✅ NEW

app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# Disease data
# -----------------------------
disease_data = {
    "Healthy": {
        "description": "The crop appears healthy with no major visible disease symptoms.",
        "solution": "No treatment is required right now. Continue regular care and monitoring.",
        "prevention": "Maintain proper irrigation, balanced nutrients, and periodic field inspection."
    },
    "Powdery Mildew": {
        "description": "A fungal disease that causes white powder-like patches on leaves and stems.",
        "solution": "Remove affected leaves and apply a suitable fungicide.",
        "prevention": "Avoid overcrowding, improve airflow, and reduce excess moisture on leaves."
    },
    "Leaf Blight": {
        "description": "A leaf disease that causes brown or yellow lesions and may spread quickly.",
        "solution": "Prune infected portions and use a recommended fungicide after expert advice.",
        "prevention": "Use disease-free seeds, avoid water stagnation, and monitor leaves regularly."
    }
}

# -----------------------------
# Disease logic
# -----------------------------
def basic_predict_from_filename(filename: str):
    name = filename.lower()
    if "powder" in name or "mildew" in name:
        return "Powdery Mildew", 88.0
    if "blight" in name or "spot" in name:
        return "Leaf Blight", 84.0
    return "Healthy", 81.0


def verify_prediction(prediction, q1, q2, q3):
    q1, q2, q3 = (q1 or "").lower(), (q2 or "").lower(), (q3 or "").lower()

    if prediction == "Powdery Mildew":
        if q1 == "yes":
            return "Powdery Mildew", "Symptoms match Powdery Mildew."
        elif q2 == "yes":
            return "Leaf Blight", "Adjusted based on answers."
    if prediction == "Leaf Blight":
        if q2 == "yes" or q3 == "yes":
            return "Leaf Blight", "Symptoms support result."
        elif q1 == "yes":
            return "Powdery Mildew", "Adjusted based on answers."
    if prediction == "Healthy":
        if q1 == "yes":
            return "Powdery Mildew", "Changed after verification."
        elif q2 == "yes" or q3 == "yes":
            return "Leaf Blight", "Changed after verification."

    return prediction, "Prediction completed."


def detect_disease(image_path, crop):
    crop = (crop or "").lower()
    if crop == "tomato":
        return "Predicted Disease: Tomato Early Blight"
    elif crop == "potato":
        return "Predicted Disease: Potato Late Blight"
    elif crop in ["rice", "paddy"]:
        return "Predicted Disease: Rice Leaf Blast"
    return f"Predicted Disease: Unknown for {crop}"


# -----------------------------
# WEATHER + DISEASE LINK
# -----------------------------
def get_weather_based_tip(prediction_text, advisories):
    alerts = " ".join(advisories).lower() if advisories else ""
    prediction_text = prediction_text.lower()

    if "blight" in prediction_text and ("rain" in alerts or "humidity" in alerts):
        return "High humidity/rain may worsen disease."

    if "healthy" in prediction_text:
        return "Crop healthy but monitor weather risks."

    return "Monitor crop regularly with weather."


# -----------------------------
# PAGE ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather", methods=["GET", "POST"])
def weather():
    advisories, city, crop = [], "", ""

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        crop = request.form.get("crop", "").strip()

        if city and crop:
            data = get_weather_forecast(city)
            advisories = generate_weather_advisory(crop, data) if data else ["Weather unavailable"]
        else:
            advisories = ["Enter city & crop"]

    return render_template("weather.html", advisories=advisories, city=city, crop=crop)


@app.route("/disease", methods=["GET", "POST"])
def disease():
    prediction, weather_tip = None, None

    if request.method == "POST":
        file = request.files.get("leaf_image")
        crop = request.form.get("crop", "")
        city = request.form.get("city", "")

        if file:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            prediction = detect_disease(path, crop)

            if city and crop:
                weather_data = get_weather_forecast(city)
                if weather_data:
                    advisories = generate_weather_advisory(crop, weather_data)
                    weather_tip = get_weather_based_tip(prediction, advisories)

    return render_template("disease.html", prediction=prediction, weather_tip=weather_tip)


# -----------------------------
# ✅ NEW: MARKET PAGE
# -----------------------------
@app.route("/market", methods=["GET", "POST"])
def market():
    crop = ""
    result = []

    if request.method == "POST":
        crop = request.form.get("crop", "").strip()

        if crop:
            data = get_market_data(crop)
            result = generate_market_advice(crop, data)
        else:
            result = ["Please enter crop name"]

    return render_template("market.html", crop=crop, result=result)


# -----------------------------
# API ROUTES
# -----------------------------
@app.route("/api/market", methods=["POST"])
def api_market():
    data = request.get_json()

    crop = data.get("crop", "").strip()

    if not crop:
        return jsonify({"error": "Crop required"}), 400

    market_data = get_market_data(crop)
    advice = generate_market_advice(crop, market_data)

    return jsonify({
        "crop": crop,
        "price": market_data["price"],
        "trend": market_data["trend"],
        "advice": advice
    })


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)