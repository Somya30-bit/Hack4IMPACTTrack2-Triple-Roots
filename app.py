import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from weather_service import get_weather_forecast
from advisory_engine import generate_weather_advisory

app = Flask(__name__)
CORS(app)

# Upload folder for disease detection images
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it does not exist
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
# Disease prediction logic
# -----------------------------
def basic_predict_from_filename(filename: str):
    name = filename.lower()

    if "powder" in name or "mildew" in name:
        return "Powdery Mildew", 88.0
    if "blight" in name or "spot" in name:
        return "Leaf Blight", 84.0

    return "Healthy", 81.0


def verify_prediction(prediction, q1, q2, q3):
    q1 = (q1 or "").lower()
    q2 = (q2 or "").lower()
    q3 = (q3 or "").lower()

    if prediction == "Powdery Mildew":
        if q1 == "yes":
            return "Powdery Mildew", "Symptoms match Powdery Mildew."
        elif q2 == "yes":
            return "Leaf Blight", "Image result adjusted based on symptom answers."
        else:
            return prediction, "Prediction kept based on uploaded image."

    if prediction == "Leaf Blight":
        if q2 == "yes" or q3 == "yes":
            return "Leaf Blight", "Symptoms support the detected disease."
        elif q1 == "yes":
            return "Powdery Mildew", "Image result adjusted based on symptom answers."
        else:
            return prediction, "Prediction kept based on uploaded image."

    if prediction == "Healthy":
        if q1 == "yes":
            return "Powdery Mildew", "Healthy prediction changed after symptom confirmation."
        elif q2 == "yes" or q3 == "yes":
            return "Leaf Blight", "Healthy prediction changed after symptom confirmation."
        else:
            return "Healthy", "No strong disease symptoms confirmed."

    return prediction, "Prediction completed."


def detect_disease(image_path, crop):
    """
    Dummy page-based disease prediction.
    Replace this later with your real ML model prediction.
    """
    crop = (crop or "").strip().lower()

    if crop == "tomato":
        return "Predicted Disease: Tomato Early Blight"
    elif crop == "potato":
        return "Predicted Disease: Potato Late Blight"
    elif crop in ["rice", "paddy"]:
        return "Predicted Disease: Rice Leaf Blast"
    else:
        return f"Predicted Disease: Unknown disease pattern for {crop}"


# -----------------------------
# Helper for weather + disease connection
# -----------------------------
def get_weather_based_tip(prediction_text, advisories):
    joined_alerts = " ".join(advisories).lower() if advisories else ""
    prediction_text = (prediction_text or "").lower()

    if "blight" in prediction_text or "fung" in prediction_text:
        if "humidity" in joined_alerts or "rain" in joined_alerts:
            return "High humidity or rain may worsen this disease. Keep the field well-drained and inspect leaves regularly."
        return "Monitor the crop closely because fungal diseases can spread quickly."

    if "healthy" in prediction_text:
        if advisories and "no major weather-related risk" not in joined_alerts:
            return "Crop looks healthy now, but current weather may increase future disease risk."
        return "Crop looks healthy and current weather risk appears low."

    return "Combine crop inspection with weather monitoring for better prevention."


# -----------------------------
# Page Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather", methods=["GET", "POST"])
def weather():
    advisories = []
    city = ""
    crop = ""

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        crop = request.form.get("crop", "").strip()

        if not city or not crop:
            advisories = ["Please enter both city and crop name."]
        else:
            weather_data = get_weather_forecast(city)

            if weather_data:
                advisories = generate_weather_advisory(crop, weather_data)
            else:
                advisories = ["Weather data unavailable. Please check the city name or try again later."]

    return render_template("weather.html", advisories=advisories, city=city, crop=crop)


@app.route("/disease", methods=["GET", "POST"])
def disease():
    prediction = None
    weather_tip = None

    if request.method == "POST":
        file = request.files.get("leaf_image")
        crop = request.form.get("crop", "").strip()
        city = request.form.get("city", "").strip()

        if not file or file.filename == "":
            prediction = "Please upload an image."
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            prediction = detect_disease(file_path, crop)

            if city and crop:
                weather_data = get_weather_forecast(city)

                if weather_data:
                    advisories = generate_weather_advisory(crop, weather_data)
                    weather_tip = get_weather_based_tip(prediction, advisories)
                else:
                    weather_tip = "Disease detected, but weather data could not be fetched right now."
            else:
                weather_tip = "Add city and crop name to also connect disease result with weather risk."

    return render_template("disease.html", prediction=prediction, weather_tip=weather_tip)


# -----------------------------
# API Routes
# -----------------------------
@app.route("/api/predict", methods=["POST"])
def api_predict():
    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    q1 = request.form.get("q1", "")
    q2 = request.form.get("q2", "")
    q3 = request.form.get("q3", "")

    predicted_disease, confidence = basic_predict_from_filename(file.filename)
    final_disease, verification_note = verify_prediction(predicted_disease, q1, q2, q3)

    info = disease_data.get(final_disease, disease_data["Healthy"])

    return jsonify({
        "disease": final_disease,
        "confidence": confidence,
        "description": info["description"],
        "solution": info["solution"],
        "prevention": info["prevention"],
        "verification_note": verification_note
    })


@app.route("/api/weather", methods=["POST"])
def api_weather():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    city = data.get("city", "").strip()
    crop = data.get("crop", "").strip()

    if not city or not crop:
        return jsonify({"error": "City and crop are required"}), 400

    weather_data = get_weather_forecast(city)
    if not weather_data:
        return jsonify({"error": "Weather data unavailable"}), 404

    advisories = generate_weather_advisory(crop, weather_data)

    return jsonify({
        "city": city,
        "crop": crop,
        "advisories": advisories
    })


@app.route("/api/predict-with-weather", methods=["POST"])
def api_predict_with_weather():
    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    city = request.form.get("city", "").strip()
    crop = request.form.get("crop", "").strip()
    q1 = request.form.get("q1", "")
    q2 = request.form.get("q2", "")
    q3 = request.form.get("q3", "")

    if not city or not crop:
        return jsonify({"error": "City and crop are required"}), 400

    predicted_disease, confidence = basic_predict_from_filename(file.filename)
    final_disease, verification_note = verify_prediction(predicted_disease, q1, q2, q3)
    info = disease_data.get(final_disease, disease_data["Healthy"])

    weather_data = get_weather_forecast(city)
    if not weather_data:
        return jsonify({"error": "Weather data unavailable"}), 404

    advisories = generate_weather_advisory(crop, weather_data)
    combined_tip = get_weather_based_tip(final_disease, advisories)

    return jsonify({
        "disease_result": {
            "disease": final_disease,
            "confidence": confidence,
            "description": info["description"],
            "solution": info["solution"],
            "prevention": info["prevention"],
            "verification_note": verification_note
        },
        "weather_result": {
            "city": city,
            "crop": crop,
            "advisories": advisories
        },
        "combined_tip": combined_tip
    })


if __name__ == "__main__":
    app.run(debug=True)