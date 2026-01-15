import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());



const PANCREATIC_ENZYMES = [
  {
    name: "Trypsinogen",
    gene: "PRSS1",
    uniprot: "P07477",
    lengthRange: [230, 270],
    activeSiteMotifs: ["IVGGY", "HIS", "ASP", "SER"],
    zymogenActivation: "DDDDK",
    function:
      "Inactive precursor of trypsin, a key serine protease for protein digestion"
  },
  {
    name: "Chymotrypsinogen",
    gene: "CTRB1",
    uniprot: "P17538",
    lengthRange: [245, 270],
    activeSiteMotifs: ["IVGGY", "HIS", "ASP", "SER"],
    function:
      "Inactive precursor of chymotrypsin, involved in protein digestion"
  },
  {
    name: "Elastase",
    gene: "CELA3A",
    uniprot: "P08246",
    lengthRange: [240, 270],
    activeSiteMotifs: ["IVGGY", "HIS", "ASP", "SER"],
    function:
      "Pancreatic elastase that digests elastin and other proteins"
  },
  {
    name: "Carboxypeptidase A1",
    gene: "CPA1",
    uniprot: "P15085",
    lengthRange: [400, 430],
    activeSiteMotifs: ["HIS", "GLU", "TYR"],
    function:
      "Exopeptidase that removes C-terminal amino acids"
  },
  {
    name: "Carboxypeptidase B1",
    gene: "CPB1",
    uniprot: "P16870",
    lengthRange: [400, 430],
    activeSiteMotifs: ["HIS", "GLU", "TYR"],
    function:
      "C-terminal basic amino acid digestion"
  },
  {
    name: "Pancreatic Lipase",
    gene: "PNLIP",
    uniprot: "P16233",
    lengthRange: [440, 470],
    activeSiteMotifs: ["GHSMGG"],
    function:
      "Digests dietary triglycerides"
  },
  {
    name: "Colipase",
    gene: "CLPS",
    uniprot: "P12111",
    lengthRange: [90, 110],
    activeSiteMotifs: ["CYS"],
    function:
      "Cofactor for pancreatic lipase"
  },
  {
    name: "Pancreatic Amylase",
    gene: "AMY2A",
    uniprot: "P04745",
    lengthRange: [490, 520],
    activeSiteMotifs: ["DVVLD", "HIS"],
    function:
      "Breaks down starch into sugars"
  },
  {
    name: "Phospholipase A2",
    gene: "PLA2G1B",
    uniprot: "P04054",
    lengthRange: [120, 145],
    activeSiteMotifs: ["HIS", "ASP"],
    function:
      "Hydrolyzes phospholipids"
  }
];



function cleanSequence(seq) {
  return seq
    .replace(/^>.*\n?/g, "")
    .replace(/[^A-Z]/gi, "")
    .toUpperCase();
}



function identifyEnzyme(sequence) {
  const length = sequence.length;

  for (const enzyme of PANCREATIC_ENZYMES) {
    if (
      length >= enzyme.lengthRange[0] &&
      length <= enzyme.lengthRange[1]
    ) {
      let motifHits = 0;
      for (const motif of enzyme.activeSiteMotifs) {
        if (sequence.includes(motif)) motifHits++;
      }

      if (motifHits >= Math.max(1, enzyme.activeSiteMotifs.length - 1)) {
        return enzyme;
      }
    }
  }
  return null;
}



function analyzeDamage(sequence, enzyme) {
  const missingMotifs = enzyme.activeSiteMotifs.filter(
    motif => !sequence.includes(motif)
  );

  if (missingMotifs.length === 0) {
    return {
      classification: "No detectable damage",
      impact:
        "Active site motifs are intact; enzymatic function likely preserved",
      confidence: "0.95"
    };
  }

  return {
    classification: "Damaged active site",
    impact:
      "Missing critical residues: " +
      missingMotifs.join(", ") +
      ". Catalytic activity likely impaired.",
    confidence: "0.90"
  };
}



app.post("/analyze", (req, res) => {
  const rawSequence = req.body.sequence;

  if (!rawSequence) {
    return res.status(400).json({ error: "No sequence provided" });
  }

  const sequence = cleanSequence(rawSequence);
  const enzyme = identifyEnzyme(sequence);

  if (!enzyme) {
    return res.json({
      uniprot_id: "Unknown",
      enzyme: "Not a pancreatic enzyme",
      damage_type: "Unknown",
      functional_impact: "Sequence does not match known pancreatic enzymes",
      confidence: "0.10"
    });
  }

  const damage = analyzeDamage(sequence, enzyme);

  res.json({
    enzyme: enzyme.name,
    gene: enzyme.gene,
    uniprot_id: enzyme.uniprot,
    damage_type: damage.classification,
    functional_impact: damage.impact,
    confidence: damage.confidence,
    preview:
      "Identified pancreatic enzyme: " +
      enzyme.name +
      " (" +
      enzyme.gene +
      ")"
  });
});



const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Pancreatic enzyme backend running on port ${PORT}`);
});
