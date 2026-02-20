from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import math
import os

# finding frontend
app = Flask(__name__, template_folder="templates")
CORS(app)

# dictionary
proenzymes = {
    "P07477": ("Trypsinogen", "MNPLLILTFVAAALAAPFDDDDKIVGGYNCEENSVPYQVSLNSGYHFCGGSLINEQWVVSAGHCYKSR"
    "IQVRLGEHNIEVLEGNEQFINAAKIIRHPQYDRKTLNNDIMLIKLSSRAVINARVSTISLPTAPPATGTKCLISGWGNTASSGADYPDELQCLD"
    "APVLSQAKCEASYPGKITSNMFCVGFLEGGKDSCQGDSGGPVVCNGQLQGVVSWGDGCAQKNKPGVYTKVYNYVKWIKNTIAANS"),
    "P17538": ("Chymotrypsinogen", "MASLWLLSCFSLVGAAFGCGVPAIHPVLSGLSRIVNGEDAVPGSWPWQVSLQDKTGFHFCGGS"
    "LISEDWVVTAAHCGVRTSDVVVAGEFDQGSDEENIQVLKIAKVFKNPKFSILTVNNDITLLKLATPARFSQTVSAVCLPSADDDFPAGTLCATT"
    "GWGKTKYNANKTPDKLQQAALPLLSNAECKKSWGRRITDVMICAGASGVSSCMGDSGGPLVCQKDGAWTLVGIVSWGSDTCSTSSPGVYARVTK"
    "LIPWVQKILAAN"),
    "P15085": ("Procarboxypeptidase", "MRGLLVLSVLLGAVFGKEDFVGHQVLRISVADEAQVQKVKELEDLEHLQLDFWRGPAHPG"
    "SPIDVRVPFPSIQAVKIFLESHGISYETMIEDVQSLLDEEQEQMFAFRSRARSTDTFNYATYHTLEEIYDFLDLLVAENPHLVSKIQIGNTYEG"
    "RPIYVLKFSTGGSKRPAIWIDTGIHSREWVTQASGVWFAKKITQDYGQDAAFTAILDTLDIFLEIVTNPDGFAFTHSTNRMWRKTRSHTAGSLC"
    "IGVDPNRNWDAGFGLSGASSNPCSETYHGKFANSEVEVKSIVDFVKDHGNIKAFISIHSYSQLLMYPYGYKTEPVPDQDELDQLSKAAVTALAS"
    "LYGTKFNYGSIIKAIYQASGSTIDWTYSQGIKYSFTFELRDTGRYGFLLPASQIIPTAKETWLALLTIMEHTLNHPY"),
    "P04054": ("Prophospholipase", "MKLLVLAVLLTVAAADSGISPRAVWQFRKMIKCVIPGSDPFLEYNNYGCYCGLGGSGTPVDEL"
    "DKCCQTHDNCYDQAKKLDSCKFLLDNPYTHTYSYSCSGSAITCSSKNKECEAFICNCDRNAAICFSKAPYNKAHKNLDTKKYCQS"),
    "Q9UNI1": ("Proelastase", "MLVLYGHSTQDLPETNARVVGGTEAGRNSWPSQISLQYRSGGSRYHTCGGTLIRQNWVMTAAHCVDYQ"
    "KTFRVVAGDHNLSQNDGTEQYVSVQKIVVHPYWNSDNVAAGYDIALLRLAQSVTLNSYVQLGVLPQEGAILANNSPCYITGWGKTKTNGQLAQT"
    "LQQAYLPSVDYAICSSSSYWGSTVKNTMVCAGGDGVRSGCQGDSGGPLHCLVNGKYSVHGVTSFVSSRGCNVSRKPTVFTQVSAYISWINNVIASN"),
    "P35030": ("Mesotrypsinogen", "MCGPDDRCPARWPGPGRAVKCGKGLAAARPGRVERGGAQRGGAGLELHPLLGGRTWRAARDADG"
    "CEALGTVAVPFDDDDKIVGGYTCEENSLPYQVSLNSGSHFCGGSLISEQWVVSAAHCYKTRIQVRLGEHNIKVLEGNEQFINAAKIIRHPKYNR"
    "DTLDNDIMLIKLSSPAVINARVSTISLPTTPPAAGTECLISGWGNTLSFGADYPDELKCLDAPVLTQAECKASYPGKITNSMFCVGFLEGGKDS"
    "CQRDSGGPVVCNGQLQGVVSWGHGCAWKNRPGVYTKVYNYVDWIKDTIAANS")
}

# dumping data to frontend
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    uniprotkb = data["uniprotkb_id"].upper()
    damaged = data["damaged_sequence"].upper()
    
    if uniprotkb not in proenzymes:
        return jsonify({"error": "Uniprot ID not found"}), 404

    identified, WTsequence = proenzymes[uniprotkb]

# analyze the changes in WT sequence and damaged sequence
    changes = []
    max_len = max(len(WTsequence), len(damaged))
    for i in range(max_len):
        characters_WT = WTsequence[i] if i < len(WTsequence) else "-"
        characters_damage = damaged[i] if i < len(damaged) else "-"
        
        if characters_WT != characters_damage:
            changes.append({
                "position": i + 1,
                "from": characters_WT,
                "to": characters_damage
})

# find the amino acid percentage
    analysed_WT = ProteinAnalysis(WTsequence)
    analysed_damage = ProteinAnalysis(damaged)
    WT_percents = analysed_WT.get_amino_acids_percent()
    damage_percents = analysed_damage.get_amino_acids_percent()

# math by absolute value
    total_diff = 0
    for aa in WT_percents:
        total_diff += abs(WT_percents[aa] - damage_percents.get(aa, 0))
    damaged_percent = max(0, (1 - total_diff) * 100)


# return data collection to frontend
    return jsonify({
        "identified_enzyme": identified,
        "changes_in_sequence": changes,
        "damaged_percent": damaged_percent
})

# code going to PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
