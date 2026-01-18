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
    params = {"query": sequence, "format": "json", "size": 5}
    r = requests.get(url, params=params, timeout=10)
    results = []
    if r.status_code == 200:
        for entry in r.json().get("results", []):
            gene = entry.get("genes", [{}])[0].get("geneName", {}).get("value")
            if gene in DIGESTIVE_PROENZYMES:
                results.append({
                    "gene": gene,
                    "name": DIGESTIVE_PROENZYMES[gene],
                    "accession": entry["primaryAccession"]
                })
    return results

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
                "effect": "Potential loss of catalytic or structural function"
            })

    mutations = len(differences)
    # dynamic likelihood calculation
    normal_score = 100
    damaged_score = max(0, 100 * (0.95 ** mutations))  # 5% functional impact per mutation

    return jsonify({
        "differences": differences,
        "matched_enzymes": uniprot_lookup(normal),
        "summary": {
            "total_mutations": mutations,
            "functional_likelihood": round(damaged_score, 2)
        },
        "likelihoods": {
            "normal": normal_score,
            "damaged": round(damaged_score, 2)
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
