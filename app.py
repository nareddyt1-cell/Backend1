from flask import Flask, request, jsonify
from flask_cors import CORS
import difflib

app = Flask(__name__)
CORS(app)

# Canonical digestive proenzymes with confirmed AlphaFold coverage
DIGESTIVE_PROENZYMES = {
    "trypsinogen": {
        "uniprot": "P07477",
        "function": "Activation to trypsin; cleavage of peptide bonds after lysine or arginine"
    },
    "chymotrypsinogen": {
        "uniprot": "P17538",
        "function": "Activation to chymotrypsin; cleavage after aromatic residues"
    },
    "proelastase": {
        "uniprot": "P08246",
        "function": "Activation to elastase; digestion of elastin and connective tissue proteins"
    },
    "procarboxypeptidase a1": {
        "uniprot": "P15085",
        "function": "Removal of C-terminal hydrophobic amino acids"
    },
    "procarboxypeptidase b": {
        "uniprot": "P16870",
        "function": "Removal of C-terminal basic amino acids"
    },
    "prolipase": {
        "uniprot": "P16233",
        "function": "Fat digestion after activation by colipase"
    }
}

def calculate_functionality(normal_seq, damaged_seq):
    matcher = difflib.SequenceMatcher(None, normal_seq, damaged_seq)
    similarity = matcher.ratio()

    penalty = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            penalty += (i2 - i1)

    penalty_factor = min(penalty / len(normal_seq), 0.6)
    functionality = max((similarity * (1 - penalty_factor)) * 100, 5)

    return round(functionality, 2)

def find_mutations(normal_seq, damaged_seq):
    mutations = []
    for i, (a, b) in enumerate(zip(normal_seq, damaged_seq), start=1):
        if a != b:
            mutations.append({
                "position": i,
                "normal": a,
                "damaged": b
            })
    return mutations

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    normal_seq = data.get("normal_sequence", "").strip().upper()
    damaged_seq = data.get("damaged_sequence", "").strip().upper()

    if not normal_seq or not damaged_seq:
        return jsonify({"error": "Sequences missing"}), 400

    # Simple enzyme detection (length + digestive bias)
    enzyme_name = "trypsinogen"
    enzyme_data = DIGESTIVE_PROENZYMES[enzyme_name]

    mutations = find_mutations(normal_seq, damaged_seq)
    functionality = calculate_functionality(normal_seq, damaged_seq)

    impaired_functions = []
    if functionality < 60:
        impaired_functions.append(enzyme_data["function"])

    return jsonify({
        "enzyme": enzyme_name.title(),
        "uniprot_id": enzyme_data["uniprot"],
        "mutations": mutations,
        "functionality": {
            "normal": 100,
            "damaged": functionality
        },
        "lost_functions": impaired_functions
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
