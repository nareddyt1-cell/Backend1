import express from "express";
import cors from "cors";

const app = express();


app.use(cors({
  origin: "*",
  methods: ["POST", "GET"],
  allowedHeaders: ["Content-Type"]
}));

app.use(express.json());


const pancreaticEnzymes = [
  {
    name: "Trypsinogen",
    uniprot: "P07477",
    signature: "IVGGY",
    description: "Serine protease precursor"
  },
  {
    name: "Chymotrypsinogen",
    uniprot: "P17538",
    signature: "CGGSI",
    description: "Digestive protease precursor"
  },
  {
    name: "Elastase",
    uniprot: "P08246",
    signature: "IVGGY",
    description: "Elastic fiber digestion"
  }
];


app.post("/analyze", (req, res) => {
  const { reference_sequence, damaged_sequence } = req.body;

  if (!reference_sequence || !damaged_sequence) {
    return res.status(400).json({
      error: "Both reference and damaged sequences are required"
    });
  }

  const ref = reference_sequence.replace(/\s+/g, "").toUpperCase();
  const dmg = damaged_sequence.replace(/\s+/g, "").toUpperCase();

  let enzymeMatch = null;

  for (const enzyme of pancreaticEnzymes) {
    if (ref.includes(enzyme.signature)) {
      enzymeMatch = enzyme;
      break;
    }
  }

  if (!enzymeMatch) {
    return res.json({
      enzyme_name: "Unknown pancreatic enzyme",
      uniprot_id: "N/A",
      damaged_region: "Unable to determine",
      functional_impact: "Sequence does not match known pancreatic enzymes",
      confidence: "Low"
    });
  }

  let diffCount = 0;
  const len = Math.min(ref.length, dmg.length);
  for (let i = 0; i < len; i++) {
    if (ref[i] !== dmg[i]) diffCount++;
  }

  const impact =
    diffCount === 0
      ? "No functional damage detected"
      : diffCount > 10
      ? "Severe functional impairment likely"
      : "Partial loss of enzymatic activity likely";

  res.json({
    enzyme_name: enzymeMatch.name,
    uniprot_id: enzymeMatch.uniprot,
    damaged_region: diffCount > 0 ? "Catalytic / structural region affected" : "None",
    functional_impact: impact,
    confidence: diffCount > 0 ? "High" : "Very High"
  });
});


const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
