import express from "express";
import cors from "cors";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

function cleanSequence(seq) {
  return seq
    .toUpperCase()
    .replace(/[^ACDEFGHIKLMNPQRSTVWY]/g, "");
}

function analyzeSequences(reference, damaged) {
  let differences = 0;
  const length = Math.max(reference.length, damaged.length);

  for (let i = 0; i < length; i++) {
    if (reference[i] !== damaged[i]) differences++;
  }

  let damageType = "No detected damage";
  let impact = "Enzymatic function likely preserved";
  let confidence = "0.95";

  if (differences > 0 && differences < 5) {
    damageType = "Minor damage";
    impact = "Minimal functional impact expected";
    confidence = "0.80";
  } else if (differences >= 5 && differences < 20) {
    damageType = "Moderate damage";
    impact = "Partial reduction in enzymatic activity likely";
    confidence = "0.65";
  } else if (differences >= 20) {
    damageType = "Severe damage";
    impact = "Enzymatic activity likely lost";
    confidence = "0.40";
  }

  return {
    uniprot_id: "P00740 (example)", // placeholder until real UniProt mapping
    damage_type: damageType,
    functional_impact: impact,
    confidence
  };
}

app.post("/analyze", (req, res) => {
  const { reference_sequence, damaged_sequence } = req.body;

  if (!reference_sequence || !damaged_sequence) {
    return res.status(400).json({ error: "Missing sequences" });
  }

  const ref = cleanSequence(reference_sequence);
  const dmg = cleanSequence(damaged_sequence);

  const result = analyzeSequences(ref, dmg);
  res.json(result);
});

app.get("/", (req, res) => {
  res.send("Enzyme analysis backend running");
});

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
