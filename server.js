import express from "express";
import cors from "cors";

const app = express();

app.use(cors());
app.use(express.json());


const pancreaticEnzymes = {
  TRYPSIN: {
    name: "Trypsin",
    catalyticRange: [41, 245],
    description: "Serine protease involved in protein digestion"
  },
  CHYMOTRYPSIN: {
    name: "Chymotrypsin",
    catalyticRange: [42, 245],
    description: "Digestive protease targeting aromatic residues"
  }
};

function detectEnzyme(sequence) {
  if (sequence.includes("HISG") && sequence.includes("ASP")) {
    return pancreaticEnzymes.TRYPSIN;
  }
  return pancreaticEnzymes.CHYMOTRYPSIN;
}

function compareSequences(ref, damaged) {
  let differences = [];
  const len = Math.max(ref.length, damaged.length);

  for (let i = 0; i < len; i++) {
    if (ref[i] !== damaged[i]) {
      differences.push(i + 1);
    }
  }

  return differences;
}

app.post("/analyze", (req, res) => {
  const { reference_sequence, damaged_sequence } = req.body;

  if (!reference_sequence || !damaged_sequence) {
    return res.status(400).json({ error: "No sequence provided" });
  }

  const enzyme = detectEnzyme(reference_sequence);
  const diffs = compareSequences(reference_sequence, damaged_sequence);

  const catalyticDamage = diffs.some(
    (pos) =>
      pos >= enzyme.catalyticRange[0] &&
      pos <= enzyme.catalyticRange[1]
  );

  res.json({
    enzyme_name: enzyme.name,
    enzyme_description: enzyme.description,
    damaged_positions: diffs,
    functional_impact: catalyticDamage
      ? "Catalytic region damaged — enzymatic activity likely reduced"
      : "No catalytic damage detected"
  });
});


const PORT = process.env.PORT || 10000;

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
