from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

DIGESTIVE_PROENZYMES = {
    "PRSS1": "Trypsinogen",
    "PRSS2": "Trypsinogen-2",
    "CTRB1": "Chymotrypsinogen B",
    "CTRC": "Chymotrypsin C",
    "CPA1": "Procarboxypeptidase A1",
    "CPB1": "Procarboxypeptidase B",
    "CELA2A": "Proelastase 2A"
}

@app.route("/")
def home():
    return render_template("index.html")

def uniprot_lookup(sequence):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": sequence, "format": "json", "size": 1}
    r = requests.get(url, params=params, timeout=10)

    if r.status_code == 200 and r.json()["results"]:
        entry = r.json()["results"][0]
        gene = entry.get("genes", [{}])[0].get("geneName", {}).get("value")
        if gene in DIGESTIVE_PROENZYMES:
            return {
                "gene": gene,
                "name": DIGESTIVE_PROENZYMES[gene],
                "accession": entry["primaryAccession"]
            }
    return None

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    normal = data["normal_sequence"]
    damaged = data["damaged_sequence"]

    differences = []
    mutation_effects = []

    for i, (n, d) in enumerate(zip(normal, damaged)):
        if n != d:
            differences.append({"position": i + 1})
            mutation_effects.append({
                "position": i + 1,
                "effect": f"Residue change {n}→{d} may destabilize folding or catalytic activity"
            })

    mutations = len(differences)
    damaged_score = max(0, 100 * (0.95 ** mutations))

    enzyme = uniprot_lookup(normal)

    return jsonify({
        "differences": differences,
        "mutation_effects": mutation_effects,
        "summary": {
            "total_mutations": mutations,
            "functional_likelihood": round(damaged_score, 2)
        },
        "alphafold_id": enzyme["accession"] if enzyme else None
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
