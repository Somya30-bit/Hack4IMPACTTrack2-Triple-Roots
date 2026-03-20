from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server running"

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    # Currently returning dummy response
    return jsonify({"result": "🌱 Healthy Plant (Demo)"})

if __name__ == "__main__":
    app.run(debug=True)