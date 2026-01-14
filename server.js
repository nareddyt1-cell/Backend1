import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));


const PANCREATIC_ENZYMES = [
  { name: "Trypsin-1", uniprot: "P07477", lengthRange: [245, 255], catalytic: [57,102,195] },
  { name: "Trypsin-2", uniprot: "P07478", lengthRange: [245, 255], catalytic: [57,102,195] },
  { name: "Chymotrypsin-B", uniprot: "P17538", lengthRange: [240, 250], catalytic: [57,102,195] },
  { name: "Chymotrypsin-C", uniprot: "Q6X4W1", lengthRange: [240, 250], catalytic: [57,102,195] },
  { name: "Elastase-1", uniprot: "P08246", lengthRange: [210, 225], catalytic: [57,102,195] },
  { name: "Elastase-2", uniprot: "P08217", lengthRange: [210, 225], catalytic: [57,102,195] },
  { name: "Carboxypeptidase A1", uniprot: "P15085", lengthRange: [400, 420], catalytic: [] },
  { name: "Carboxypeptidase A2", uniprot: "P15086", lengthRange: [400, 420], catalytic: [] },
  { name: "Carboxypeptidase B1", uniprot: "P10619", lengthRange: [400, 420], catalytic: [] },
  { name: "Pancreatic Lipase", uniprot: "P16233", lengthRange: [430, 460], catalytic: [153,177,264] },
  { name: "Phospholipase A2", uniprot: "P04054", lengthRange: [120, 135], catalytic: [48,49] },
  { name: "Pancreatic Amylase", uniprot: "P04745", lengthRange: [490, 520], catalytic: [] },
  { name: "Ribonuclease A", uniprot: "P07998", lengthRange: [120, 130], catalytic: [12,41,119] },
  { name: "Deoxyribonuclease I", uniprot: "P24855", lengthRange: [250, 280], catalytic: [] }
];


const clean = s => s.toUpperCase().replace(/[^ACDEFGHIKLMNPQRSTVWY]/g,"");

function identifyEnzyme(seq) {
  return PANCREATIC_ENZYMES.find(e =>
    seq.length >= e.lengthRange[0] &&
    seq.length <= e.lengthRange[1]
  );
}

function diff(ref, dam) {
  const diffs = [];
  for (let i=0;i<Math.max(ref.length, dam.length);i++) {
    if (ref[i] !== dam[i]) diffs.push(i+1);
  }
  return diffs;
}


app.post("/analyze", (req,res)=>{
  const { reference_sequence, damaged_sequence } = req.body;
  if (!reference_sequence || !damaged_sequence)
    return res.status(400).json({ error:"Sequences required" });

  const ref = clean(reference_sequence);
  const dam = clean(damaged_sequence);

  const enzyme = identifyEnzyme(ref);
  if (!enzyme)
    return res.status(400).json({ error:"Not a known pancreatic enzyme" });

  const diffs = diff(ref,dam);
  const catalyticHits = enzyme.catalytic.filter(p=>diffs.includes(p));

  res.json({
    enzyme: enzyme.name,
    uniprot_id: enzyme.uniprot,
    total_differences: diffs.length,
    catalytic_damage: catalyticHits.length > 0,
    damaged_positions: diffs.slice(0,30),
    interpretation:
      catalyticHits.length
        ? "Catalytic residue damage — loss of enzymatic activity likely"
        : diffs.length
        ? "Non-catalytic damage — partial functional impairment possible"
        : "No damage detected"
  });
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, ()=>console.log("Pancreatic enzyme backend running"));
