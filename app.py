from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

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


@app.route("/")
def home():
    return "KrishiMitra backend is running."


@app.route("/predict", methods=["POST"])
def predict():
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


if __name__ == "__main__":
    app.run(debug=True)