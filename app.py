from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb/search"

def get_uniprot_info(sequence_fragment):
    """
    Searches UniProt for entries matching the given sequence fragment.
    Returns functional info for mutated residues.
    """
    params = {
        "query": sequence_fragment,
        "fields": "accession,id,feature(INTERPRO),feature(ACTIVE_SITE),feature(BINDING_SITE),feature(MUTAGENESIS),feature(VARIANT)",
        "format": "json",
        "size": 1
    }
    try:
        response = requests.get(UNIPROT_BASE, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            entry = data["results"][0]
            info_lines = []
            info_lines.append(f"UniProt ID: {entry.get('primaryAccession', 'N/A')}")
            features = entry.get("features", [])
            for f in features:
                ft_type = f.get("type", "UNKNOWN")
                ft_desc = f.get("description", "")
                location = f.get("location", {}).get("start", "?")
                info_lines.append(f"{ft_type} at position {location}: {ft_desc}")
            return "\n".join(info_lines)
        else:
            return "No UniProt match found for this fragment."
    except Exception as e:
        return f"UniProt query failed: {e}"

def analyze_sequences(normal_seq, damaged_seq):
    """
    Compares normal and damaged sequences and retrieves functional info for mutated residues.
    """
    min_len = min(len(normal_seq), len(damaged_seq))
    analysis = []

    for i in range(min_len):
        if normal_seq[i] != damaged_seq[i]:
            fragment = damaged_seq[max(0, i-3):i+4]  # small fragment around mutation
            uniprot_info = get_uniprot_info(fragment)
            analysis.append(
                f"Position {i+1}: {normal_seq[i]} -> {damaged_seq[i]}\n{uniprot_info}\n"
            )

    if len(damaged_seq) > len(normal_seq):
        for i in range(len(normal_seq), len(damaged_seq)):
            fragment = damaged_seq[max(0, i-3):i+4]
            uniprot_info = get_uniprot_info(fragment)
            analysis.append(
                f"Position {i+1}: extra residue {damaged_seq[i]}\n{uniprot_info}\n"
            )

    if not analysis:
        analysis.append("No differences detected. The enzyme is likely normal.")

    return "\n".join(analysis)

@app.route('/analyze', methods=['POST'])
def analyze_sequence():
    data = request.get_json()
    normal_seq = data.get('normalSeq', '').upper()
    damaged_seq = data.get('damagedSeq', '').upper()

    if not normal_seq or not damaged_seq:
        return jsonify({"result": "Both sequences are required."}), 400

    result_text = analyze_sequences(normal_seq, damaged_seq)
    return jsonify({"result": result_text})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
