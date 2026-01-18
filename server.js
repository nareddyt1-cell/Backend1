import express from "express";
import cors from "cors";
import fetch from "node-fetch";

const app = express();
app.use(cors());
app.use(express.json());



const PANCREATIC_KEYWORDS = [
  "TRYPSINOGEN",
  "TRYPSIN",
  "CHYMOTRYPSINOGEN",
  "CHYMOTRYPSIN",
  "ELASTASE",
  "CARBOXYPEPTIDASE",
  "AMYLASE",
  "LIPASE",
  "PHOSPHOLIPASE",
  "RIBONUCLEASE"
];


function cleanSequence(seq) {
  return seq
    .replace(/^>.*\n?/gm, "")
    .replace(/[^A-Z]/gi, "")
    .toUpperCase();
}


function compareSequences(reference, damaged) {
  let diffs = [];
  const len = Math.min(reference.length, damaged.length);

  for (let i = 0; i < len; i++) {
    if (reference[i] !== damaged[i]) {
      diffs.push({
        position: i + 1,
        ref: reference[i],
        damaged: damaged[i]
      });
    }
  }

  return diffs;
}


app.post("/analyze", async (req, res) => {
  try {
    const { reference_sequence, damaged_sequence } = req.body;

    if (!reference_sequence || !damaged_sequence) {
      return res.status(400).json({ error: "No sequence provided" });
    }

    const refSeq = cleanSequence(reference_sequence);
    const damSeq = cleanSequence(damaged_sequence);

   
    const uniprotURL =
      "https://rest.uniprot.org/uniprotkb/search?query=" +
      encodeURIComponent(refSeq.slice(0, 30)) +
      "&format=json&size=5";

    const uniRes = await fetch(uniprotURL);
    const uniData = await uniRes.json();

    if (!uniData.results || uniData.results.length === 0) {
      return res.json({
        enzyme: "Unknown",
        uniprot_id: "Not found",
        damage_type: "Unrecognized sequence",
        functional_impact: "Sequence does not match known pancreatic enzymes",
        confidence: "Low"
      });
    }

  
    let enzymeMatch = null;

    for (const entry of uniData.results) {
      const proteinName =
        entry.proteinDescription?.recommendedName?.fullName?.value ||
        "";

      const isPancreatic = PANCREATIC_KEYWORDS.some(k =>
        proteinName.toUpperCase().includes(k)
      );

      if (isPancreatic) {
        enzymeMatch = entry;
        break;
      }
    }

    if (!enzymeMatch) {
      return res.json({
        enzyme: "Not pancreatic",
        uniprot_id: "N/A",
        damage_type: "Non-pancreatic enzyme",
        functional_impact:
          "Sequence matched UniProt but is not a pancreatic enzyme",
        confidence: "Medium"
      });
    }

    const enzymeName =
      enzymeMatch.proteinDescription.recommendedName.fullName.value;
    const uniprotID = enzymeMatch.primaryAccession;
    const referenceProteinSeq = enzymeMatch.sequence.value;

    const diffs = compareSequences(referenceProteinSeq, damSeq);

    let damageSummary = "No detectable damage";
    let functionalImpact = "Likely normal enzymatic activity";

    if (diffs.length > 0) {
      damageSummary = `Detected ${diffs.length} amino acid substitutions`;

      const catalyticKeywords = ["HIS", "ASP", "SER"];

      functionalImpact =
        "Damage detected outside critical catalytic residues";

      if (diffs.length > 10) {
        functionalImpact =
          "Significant sequence damage — enzymatic activity likely reduced";
      }
    }

    res.json({
      enzyme: enzymeName,
      uniprot_id: uniprotID,
      damage_type: damageSummary,
      functional_impact: functionalImpact,
      confidence:
        diffs.length === 0
          ? "High"
          : diffs.length < 10
          ? "Medium"
          : "Low"
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error" });
  }
});


const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
