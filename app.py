from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import difflib

app = Flask(__name__)
CORS(app)

# Digestive proenzymes with confirmed AlphaFold structures
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

VALID_UNIPROT_IDS = [v["uniprot"] for v in DIGESTIVE_PROENZYMES.values()]

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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    normal_seq = data.get("normal_sequence", "").strip().upper()
    damaged_seq = data.get("damaged_sequence", "").strip().upper()

    if not normal_seq or not damaged_seq:
        return jsonify({"error": "Sequences missing"}), 400

    # For simplicity, pick trypsinogen as example enzyme
    enzyme_name = "trypsinogen"
    enzyme_data = DIGESTIVE_PROENZYMES[enzyme_name]

    mutations = find_mutations(normal_seq, damaged_seq)
    functionality = calculate_functionality(normal_seq, damaged_seq)

    lost_functions = []
    if functionality < 60:
        lost_functions.append(enzyme_data["function"])

    # Only send AlphaFold ID if it's valid
    uniprot_id = enzyme_data["uniprot"] if enzyme_data["uniprot"] in VALID_UNIPROT_IDS else None

    return jsonify({
        "enzyme": enzyme_name.title(),
        "uniprot_id": uniprot_id,
        "mutations": mutations,
        "functionality": {
            "normal": 100,
            "damaged": functionality
        },
        "lost_functions": lost_functions
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
