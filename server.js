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

function identifyPancreaticEnzyme(sequence) {
  const seq = sequence.toUpperCase().replace(/[^A-Z]/g, "");

  // Trypsinogen recognition
  const hasTrypsinMotif =
    seq.includes("DDDDK") || // activation peptide
    (seq.includes("HIS") && seq.includes("ASP") && seq.includes("SER"));

  if (hasTrypsinMotif && seq.length >= 220 && seq.length <= 280) {
    return {
      name: "Trypsinogen",
      gene: "PRSS1",
      uniprot: "P07477",
      function: "Pancreatic serine protease precursor that activates digestive enzymes"
    };
  }

  // Chymotrypsinogen
  if (seq.length >= 240 && seq.length <= 260 && seq.includes("CGG")) {
    return {
      name: "Chymotrypsinogen",
      gene: "CTRB1",
      uniprot: "P17538",
      function: "Digestive protease precursor"
    };
  }

  // Elastase
  if (seq.length >= 245 && seq.length <= 270 && seq.includes("GNSGG")) {
    return {
      name: "Pancreatic Elastase",
      gene: "CELA3A",
      uniprot: "P08861",
      function: "Elastin-degrading protease"
    };
  }

  return null;
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

const enzyme = identifyPancreaticEnzyme(reference_sequence);

if (!enzyme) {
  return res.status(400).json({
    error: "Sequence does not match known pancreatic enzymes"
  });
}


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
