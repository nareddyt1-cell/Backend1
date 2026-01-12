import express from "express";
import cors from "cors";

const app = express();

app.use(cors());
app.use(express.json());

app.post("/analyze", (req, res) => {
  let { reference_sequence, damaged_sequence } = req.body;

  if (!reference_sequence || !damaged_sequence) {
    return res.status(400).json({ error: "No sequence provided" });
  }

  // Sanitize reference
  reference_sequence = reference_sequence
    .replace(/^>.*$/gm, "")
    .replace(/\s+/g, "")
    .toUpperCase();

  // Sanitize damaged
  damaged_sequence = damaged_sequence
    .replace(/^>.*$/gm, "")
    .replace(/\s+/g, "")
    .toUpperCase();

  if (
    !/^[ACDEFGHIKLMNPQRSTVWY]+$/.test(reference_sequence) ||
    !/^[ACDEFGHIKLMNPQRSTVWY]+$/.test(damaged_sequence)
  ) {
    return res.status(400).json({ error: "Invalid amino acid sequence" });
  }

  // TEMP REAL RESPONSE (no fake frontend)
  res.json({
    uniprot_id: "P99999",
    damage_type: "Damaged",
    functional_impact: "Reduced enzymatic activity",
    confidence: 0.87
  });
});

app.get("/", (req, res) => {
  res.send("Backend is running");
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});

