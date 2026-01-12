import express from "express";
import cors from "cors";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({ status: "API is running" });
});

app.post("/analyze", (req, res) => {
  const { sequence } = req.body;

  if (!sequence) {
    return res.status(400).json({ error: "No sequence provided" });
  }

  res.json({
    uniprot_id: "P99999",
    damage_type: "Damaged",
    functional_impact: "Reduced enzymatic activity",
    confidence: 0.87
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
