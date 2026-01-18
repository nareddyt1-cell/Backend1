from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    normal = data.get("normal_sequence", "")
    damaged = data.get("damaged_sequence", "")

    differences = []
    for i, (n, d) in enumerate(zip(normal, damaged)):
        if n != d:
            differences.append({
                "position": i + 1,
                "expected": n,
                "found": d,
                "effect": "Potential impact on catalytic or structural function"
            })

    return jsonify({
        "differences": differences,
        "summary": {
            "total_mutations": len(differences),
            "functional_likelihood": max(0, 100 - len(differences) * 5)
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
