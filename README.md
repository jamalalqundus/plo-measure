# PLO-MEASURE: Ontology-Driven Framework for Learning Outcomes Alignment

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OWL](https://img.shields.io/badge/OWL-2-blue.svg)](https://www.w3.org/OWL/)
[![SPARQL](https://img.shields.io/badge/SPARQL-1.1-green.svg)](https://www.w3.org/TR/sparql11-query/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

## Overview

PLO-MEASURE is an ontology-driven framework for automating the alignment and measurement of Program Learning Outcomes (PLOs), Key Performance Indicators (KPIs), and Course Learning Outcomes (CLOs) in higher education. The framework uses OWL 2 DL, SWRL rules, and SPARQL queries to enable:

- Hierarchical modeling of learning outcomes (PLO → KPI → CLO → Assessment → Question)
- Automated permission inference using SWRL rules
- Dynamic achievement calculation with weighted aggregation
- Structural similarity-based recommendation for learning outcomes

## Key Results

| Method | F1 | Training Required |
|--------|-----|-------------------|
| Jaccard (structural) | 0.99 | No |
| Fine-tuned BERT | 0.81 | Yes |
| TF-IDF | 0.18 | No |

- **98.95% internal consistency** on expert-validated PLO-CLO mappings
- **37.9% recall** with transitive similarity (improved from 12.3%)
- **4.20/5** usefulness rating from pilot user study (n=30)

## Repository Structure
plo-measure/  
├── manuscript/ # LaTeX source for IJAIED paper<br>
├── figures/ # All figures and generation scripts<br>
├── evaluation/ # Evaluation code (TF-IDF, BERT, SWRL)<br>
├── data/ # Data generation and loading scripts<br>
└── docs/ # Ontology documentation<br>
└── ontology/ # Ontology files<br>

## Quick Start

### Prerequisites

- Python 3.10+
- Protégé 5.6+ (for ontology editing)
- Java 11+ (for Pellet reasoner)

### Installation

```bash
git clone https://github.com/jamalalqundus/plo-measure.git
cd plo-measure
pip install -r requirements.txt
```

### Running Evaluation

#### TF-IDF baseline
python evaluation/tfidf_baseline.py

#### Generate all figures
python figures/generate_figures.py

#### Generate synthetic data
python data/generate_synthetic_data.py

### Ontology Files

The ontology is available in two formats:

ontology/plo-measure-ontology.ttl (Turtle)
ontology/plo-measure-ontology.owl (OWL/XML)
Load in Protégé: File → Open → select .ttl or .owl file.

### Citation
If you use PLO-MEASURE in your research, please cite:
```bash
@article{ploAlQundus2026,
  title={PLO-MEASURE: An Ontology-Driven Framework for Learning Outcomes Alignment in Higher Education},
  author={Al Qundus J, Alshargabi B},
  journal={International Journal of Artificial Intelligence in Education},
  year={2026},
  publisher={Springer}
}
```
### License

MIT License - see [LICENSE](./LICENSE) file.