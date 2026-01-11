import express from "express";
import cors from "cors";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Enzyme analysis backend running");
});

app.post("/analyze", (req, res) => {
  const { sequence } = req.body;

  if (!sequence) {
    return res.status(400).json({ error: "No sequence provided" });
  }

  res.json({
    uniprot_id: "P69905",
    damage_type: "Moderate structural disruption",
    functional_impact: "Reduced catalytic efficiency",
    confidence: "0.78"
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
