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
    .replace(/^>.*$/gm, "")
    .replace(/[^A-Z]/gi, "")
    .toUpperCase();
}


function compareSequences(reference, damaged) {
  const diffs = [];
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
      encodeURIComponent(refSeq.slice(0, 25)) +
      "&format=json&size=10";

    const uniRes = await fetch(uniprotURL);
    const uniData = await uniRes.json();

    if (!uniData.results || uniData.results.length === 0) {
      return res.json({
        enzyme: "Unknown",
        uniprot_id: "Not found",
        damage_type: "Unrecognized sequence",
        functional_impact: "No UniProt match",
        confidence: "Low"
      });
    }

    let enzymeMatch = null;

    for (const entry of uniData.results) {
      const proteinName =
        entry.proteinDescription?.recommendedName?.fullName?.value || "";

      if (
        PANCREATIC_KEYWORDS.some(k =>
          proteinName.toUpperCase().includes(k)
        )
      ) {
        enzymeMatch = entry;
        break;
      }
    }

    if (!enzymeMatch) {
      return res.json({
        enzyme: "Not pancreatic",
        uniprot_id: "N/A",
        damage_type: "Non-pancreatic enzyme",
        functional_impact: "Sequence is not pancreatic",
        confidence: "Medium"
      });
    }

    const enzymeName =
      enzymeMatch.proteinDescription.recommendedName.fullName.value;
    const uniprotID = enzymeMatch.primaryAccession;
    const referenceProteinSeq = enzymeMatch.sequence.value;

    const diffs = compareSequences(referenceProteinSeq, damSeq);

    let damageSummary = "No detectable damage";
    let functionalImpact = "Normal enzymatic activity expected";

    if (diffs.length > 0 && diffs.length < 10) {
      damageSummary = `${diffs.length} substitutions detected`;
      functionalImpact = "Minor functional impact likely";
    } else if (diffs.length >= 10) {
      damageSummary = `${diffs.length} substitutions detected`;
      functionalImpact = "Severe functional impairment likely";
    }

    res.json({
      enzyme: enzymeName,
      uniprot_id: uniprotID,
      damage_type: damageSummary,
      functional_impact: functionalImpact,
      confidence:
        diffs.length === 0 ? "High" : diffs.length < 10 ? "Medium" : "Low"
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
