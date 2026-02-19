from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import math
import os

# finding frontend
app = Flask(__name__, template_folder="templates")
CORS(app)

# dumping data to frontend
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    uniprotkb = data["uniprotkb_id"].upper()
    damaged = data["damaged_sequence"].upper()

# identifying the enzyme/sequence
if uniprotkb == "P07477":
    identified = "Trypsinogen"
    WTsequence = (
    "MNPLLILTFVAAALAAPFDDDDKIVGGYNCEENSVPYQVSLNSGYHFCGGSLINEQWVVSAGHCYKSRIQVRLGEHNIEVLEGNEQFINAAKIIRHPQYDRKTLNNDIMLIKLSSRAV"
    "INARVSTISLPTAPPATGTKCLISGWGNTASSGADYPDELQCLDAPVLSQAKCEASYPGKITSNMFCVGFLEGGKDSCQGDSGGPVVCNGQLQGVVSWGDGCAQKNKPGVYTKVYNYV"
    "KWIKNTIAANS"
)
    else
        if uniprotkb == "P17538":
            identified = "Chymotrypsinogen"
            WTsequence = (
    "MASLWLLSCFSLVGAAFGCGVPAIHPVLSGLSRIVNGEDAVPGSWPWQVSLQDKTGFHFCGGSLISEDWVVTAAHCGVRTSDVVVAGEFDQGSDEENIQVLKIAKVFKNPKFSILTVN"
    "NDITLLKLATPARFSQTVSAVCLPSADDDFPAGTLCATTGWGKTKYNANKTPDKLQQAALPLLSNAECKKSWGRRITDVMICAGASGVSSCMGDSGGPLVCQKDGAWTLVGIVSWGSD"
    "TCSTSSPGVYARVTKLIPWVQKILAAN"
)
            else
                if uniprotkb == "P15085":
                    identified = "Procarboxypeptidase"
                    WTsequence = (
    "MRGLLVLSVLLGAVFGKEDFVGHQVLRISVADEAQVQKVKELEDLEHLQLDFWRGPAHPGSPIDVRVPFPSIQAVKIFLESHGISYETMIEDVQSLLDEEQEQMFAFRSRARSTDTFN"
    "YATYHTLEEIYDFLDLLVAENPHLVSKIQIGNTYEGRPIYVLKFSTGGSKRPAIWIDTGIHSREWVTQASGVWFAKKITQDYGQDAAFTAILDTLDIFLEIVTNPDGFAFTHSTNRMW"
    "RKTRSHTAGSLCIGVDPNRNWDAGFGLSGASSNPCSETYHGKFANSEVEVKSIVDFVKDHGNIKAFISIHSYSQLLMYPYGYKTEPVPDQDELDQLSKAAVTALASLYGTKFNYGSII"
    "KAIYQASGSTIDWTYSQGIKYSFTFELRDTGRYGFLLPASQIIPTAKETWLALLTIMEHTLNHPY"
)
                    else
                        if uniprotkb == "P04054":
                            identified = "Prophospholipase"
                            WTsequence = (
    "MKLLVLAVLLTVAAADSGISPRAVWQFRKMIKCVIPGSDPFLEYNNYGCYCGLGGSGTPVDELDKCCQTHDNCYDQAKKLDSCKFLLDNPYTHTYSYSCSGSAITCSSKNKECEAFIC"
    "NCDRNAAICFSKAPYNKAHKNLDTKKYCQS"
)
                            else
                                if uniprotkb == "Q9UNI1":
                                    identified = "Proelastase"
                                    WTsequence = (
    "MLVLYGHSTQDLPETNARVVGGTEAGRNSWPSQISLQYRSGGSRYHTCGGTLIRQNWVMTAAHCVDYQKTFRVVAGDHNLSQNDGTEQYVSVQKIVVHPYWNSDNVAAGYDIALLRLA"
    "QSVTLNSYVQLGVLPQEGAILANNSPCYITGWGKTKTNGQLAQTLQQAYLPSVDYAICSSSSYWGSTVKNTMVCAGGDGVRSGCQGDSGGPLHCLVNGKYSVHGVTSFVSSRGCNVSR"
    "KPTVFTQVSAYISWINNVIASN"
)
                                    else
                                        if uniprotkb == "P35030":
                                            identified = "Mesotrypsinogen"
                                            WTsequence = (
    "MCGPDDRCPARWPGPGRAVKCGKGLAAARPGRVERGGAQRGGAGLELHPLLGGRTWRAARDADGCEALGTVAVPFDDDDKIVGGYTCEENSLPYQVSLNSGSHFCGGSLISEQWVVSA"
    "AHCYKTRIQVRLGEHNIKVLEGNEQFINAAKIIRHPKYNRDTLDNDIMLIKLSSPAVINARVSTISLPTTPPAAGTECLISGWGNTLSFGADYPDELKCLDAPVLTQAECKASYPGKI"
    "TNSMFCVGFLEGGKDSCQRDSGGPVVCNGQLQGVVSWGHGCAWKNRPGVYTKVYNYVDWIKDTIAANS"
)

# analyze the changes in WT sequence and damaged sequence
 changes = []
    for i, (a, b) in enumerate(zip(WTsequence, damaged)):
        if a != b:
            mutations.append({
                "position": i + 1,
                "from": a,
                "to": b
            })

# read the amino acid percentage
analysed_seq = ProteinAnalysis(WTsequence)
amino_acid_percent = analysed_seq.get_amino_acids_percent()

# math for percentage
length_WT_sequence = len(WTsequence)
damaged_percent = (length_WT_sequence - changes) * amino_acid_percent

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
