import time
import requests
import difflib
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DIGESTIVE_KEYWORDS = [
    "trypsinogen",
    "chymotrypsinogen",
    "proelastase",
    "procarboxypeptidase",
    "prolipase"
]

def blast_sequence(sequence):
    # Step 1: submit BLAST job
    submit = requests.post(
        "https://blast.ncbi.nlm.nih.gov/Blast.cgi",
        data={
            "CMD": "Put",
            "PROGRAM": "blastp",
            "DATABASE": "swissprot",
            "QUERY": sequence
        }
    )

    rid = None
    for line in submit.text.splitlines():
        if "RID =" in line:
            rid = line.split("=")[1].strip()

    if not rid:
        return None

    # Step 2: poll for results
    for _ in range(10):
        time.sleep(3)
        check = requests.get(
            "https://blast.ncbi.nlm.nih.gov/Blast.cgi",
            params={"CMD": "Get", "RID": rid, "FORMAT_TYPE": "JSON2"}
        )
        if "BlastOutput2" in check.text:
            data = check.json()
            break
    else:
        return None

    # Step 3: parse hits
    hits = data["BlastOutput2"][0]["report"]["results"]["search"]["hits"]
    for hit in hits:
        desc = hit["description"][0]["title"].lower()
        for keyword in DIGESTIVE_KEYWORDS:
            if keyword in desc:
                accession = hit["description"][0]["accession"]
                return {
                    "enzyme": keyword.title(),
                    "uniprot": accession
                }

    return None

def calculate_functionality(normal, damaged):
    matcher = difflib.SequenceMatcher(None, normal, damaged)
    similarity = matcher.ratio()
    mutation_penalty = sum(
        (i2 - i1)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes()
        if tag in ("replace", "delete")
    )
    penalty_factor = min(mutation_penalty / len(normal), 0.6)
    return round(max((similarity * (1 - penalty_factor)) * 100, 5), 2)

def find_mutations(normal, damaged):
    return [
        {"position": i+1, "normal": a, "damaged": b}
        for i, (a, b) in enumerate(zip(normal, damaged))
        if a != b
    ]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    normal = data["normal_sequence"].upper().strip()
    damaged = data["damaged_sequence"].upper().strip()

    enzyme_hit = blast_sequence(damaged)

    mutations = find_mutations(normal, damaged)
    functionality = calculate_functionality(normal, damaged)

    lost = []
    if functionality < 60 and enzyme_hit:
        lost.append(f"Reduced activity of {enzyme_hit['enzyme']}")

    return jsonify({
        "enzyme": enzyme_hit["enzyme"] if enzyme_hit else "Unknown digestive enzyme",
        "uniprot_id": enzyme_hit["uniprot"] if enzyme_hit else None,
        "mutations": mutations,
        "functionality": {
            "normal": 100,
            "damaged": functionality
        },
        "lost_functions": lost
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
v
