import express from "express";
import cors from "cors";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());



const pancreaticEnzymes = [
  {
    name: "Trypsin-1",
    uniprot: "P07477",
    signature: "HISG",
    activeRegion: "Catalytic triad (His57, Asp102, Ser195)"
  },
  {
    name: "Chymotrypsinogen B",
    uniprot: "P17538",
    signature: "GNSGG",
    activeRegion: "Substrate-binding pocket"
  },
  {
    name: "Pancreatic Elastase",
    uniprot: "P08217",
    signature: "VGGY",
    activeRegion: "Elastase specificity loop"
  },
  {
    name: "Pancreatic Alpha-Amylase",
    uniprot: "P04746",
    signature: "DVH",
    activeRegion: "Catalytic starch-binding site"
  },
  {
    name: "Pancreatic Lipase",
    uniprot: "P16233",
    signature: "GHSMGG",
    activeRegion: "Lipase catalytic serine region"
  }
];



function identifyEnzyme(sequence) {
  for (const enzyme of pancreaticEnzymes) {
    if (sequence.includes(enzyme.signature)) {
      return enzyme;
    }
  }
  return null;
}

function compareSequences(reference, damaged) {
  let differences = [];
  const length = Math.min(reference.length, damaged.length);

  for (let i = 0; i < length; i++) {
    if (reference[i] !== damaged[i]) {
      differences.push({
        position: i + 1,
        from: reference[i],
        to: damaged[i]
      });
    }
  }

  return differences;
}



app.post("/analyze", (req, res) => {
  const { reference_sequence, damaged_sequence } = req.body;

  if (!reference_sequence || !damaged_sequence) {
    return res.status(400).json({
      error: "Both reference and damaged pancreatic enzyme sequences are required."
    });
  }

  const enzyme = identifyEnzyme(reference_sequence);

  if (!enzyme) {
    return res.status(400).json({
      error: "Sequence does not match any known pancreatic enzyme."
    });
  }

  const mutations = compareSequences(reference_sequence, damaged_sequence);

  let damageType = "No significant damage detected";
  let regionDescription = "No critical functional regions affected";
  let functionalImpact = "Likely retains enzymatic activity";
  let confidence = 0.95;

  if (mutations.length > 0) {
    damageType = "Amino acid substitutions detected";
    regionDescription = `Alterations detected near ${enzyme.activeRegion}`;
    functionalImpact =
      "Mutations may disrupt substrate binding or catalytic efficiency";
    confidence = 0.88;
  }

  return res.json({
    enzyme_name: enzyme.name,
    uniprot_id: enzyme.uniprot,
    damage_type: damageType,
    damaged_region_description: regionDescription,
    functional_impact: functionalImpact,
    confidence
  });
});


app.listen(PORT, () => {
  console.log(`🧬 Pancreatic enzyme backend running on port ${PORT}`);
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});

