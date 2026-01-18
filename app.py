from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend requests

def simulate_blast_uniprot_analysis(normal_seq, damaged_seq):
    analysis = []
    min_len = min(len(normal_seq), len(damaged_seq))

    for i in range(min_len):
        if normal_seq[i] != damaged_seq[i]:
            analysis.append(
                f"Position {i+1}: {normal_seq[i]} -> {damaged_seq[i]} | Possible effect: may disrupt enzyme activity or binding."
            )

    if len(damaged_seq) > len(normal_seq):
        for i in range(len(normal_seq), len(damaged_seq)):
            analysis.append(
                f"Position {i+1}: extra residue {damaged_seq[i]} | Possible effect: structural disruption."
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

    result_text = simulate_blast_uniprot_analysis(normal_seq, damaged_seq)
    return jsonify({"result": result_text})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
