from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import math
import os

app = Flask(__name__, template_folder="templates")
CORS(app)

DIGESTIVE_PROENZYMES = {
    "Trypsinogen": {
        "uniprot": "P07477",
        "function": "Initiates protein digestion by cleaving peptide bonds"
    },
    "Chymotrypsinogen": {
        "uniprot": "P17538",
        "function": "Cleaves proteins at aromatic amino acids"
    },
    "Procarboxypeptidase A1": {
        "uniprot": "P15085",
        "function": "Removes C-terminal amino acids from peptides"
    }
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    normal = data["normal_sequence"].upper()
    damaged = data["damaged_sequence"].upper()

    # --- Mutation detection ---
    mutations = []
    for i, (a, b) in enumerate(zip(normal, damaged)):
        if a != b:
            mutations.append({
                "position": i + 1,
                "from": a,
                "to": b
            })

    mutation_rate = len(mutations) / max(len(normal), 1)

    # --- Mathematical functionality model ---
    # Exponential decay (enzyme active sites are fragile)
    k = 4.0
    damaged_function = math.exp(-k * mutation_rate)
    normal_function = 1.0

    damaged_percent = round(damaged_function * 100, 2)
    normal_percent = 100.0

    # --- Simple enzyme classification heuristic ---
    identified = "Unknown digestive proenzyme"
    lost_function = "Unknown biological impact"

    if len(normal) > 200:
        identified = "Trypsinogen"
        lost_function = DIGESTIVE_PROENZYMES["Trypsinogen"]["function"]

    return jsonify({
        "identified_enzyme": identified,
        "mutation_count": len(mutations),
        "mutations": mutations,
        "normal_percent": normal_percent,
        "damaged_percent": damaged_percent,
        "lost_function": lost_function
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
