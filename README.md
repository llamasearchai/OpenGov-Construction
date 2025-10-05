# OpenGov-Construction

A terminal-first Python toolkit for Federal and State construction program workflows, with specialized support for Indiana, Ohio, and California.

## Overview

OpenGov-Construction provides engineering support tools for construction project analysis and compliance screening. The toolkit focuses on practical workflows for state DOT and agency construction projects with Federal funding requirements. Includes schedule analysis, duration risk, compliance screening, media management and state profiles for IN, OH, CA.

### Key Features

- **Schedule Analysis**: Critical Path Method (CPM) calculations with forward/backward pass, total float, and critical path identification
- **Duration Risk**: Monte Carlo simulation using triangular distributions for schedule uncertainty quantification (P50, P80, P90)
- **Compliance Screening**: Build America, Buy America (BABA) and Davis-Bacon Related Acts (DBRA) line-item flagging
- **Media Management**: Image inventory scanning with perceptual hash-based duplicate detection
- **Knowledge Graphs**: Lightweight graph builder for stakeholders, artifacts, and project relationships
- **State Profiles**: Pre-configured agency information and reporting preferences for IN, OH, CA

### Technical Stack

- Python 3.11+ with full type annotations
- NumPy and Pandas for numerical analysis
- NetworkX for graph operations
- Pillow for image processing
- Typer and Rich for modern CLI interface
- Comprehensive test suite with pytest

## Important Disclaimer

This software supports engineering analysis and compliance workflows but **does not constitute legal advice**. All outputs must be validated against:

- Federal regulations (2 CFR Part 184 for BABA, 40 U.S.C. 3141-3148 for DBRA, FAR clauses)
- State and DOT-specific requirements
- Your contract terms and conditions
- Current agency guidance and waivers

Always consult with legal counsel and compliance officers for definitive interpretations.

## Installation

### Requirements

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Quick Start with uv

```bash
# Clone or navigate to the repository
cd OpenGov-Construction

# Create virtual environment
uv venv -p 3.11

# Install dependencies
uv sync

# Run tests to verify installation
PYTHONPATH=src uv run pytest -q

# Verify CLI is working
PYTHONPATH=src uv run python -m open_gov_construction.cli --help
```

### Alternative Installation with pip

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode
pip install -e .

# Run tests
PYTHONPATH=src pytest -q
```

## CLI Usage

The toolkit provides seven main commands accessed through the `open_gov_construction.cli` module.

### State Information

**List supported states and agencies:**

```bash
PYTHONPATH=src python -m open_gov_construction.cli list-states
```

Output includes state codes, full names, and primary agencies (DOT, IDOA, DGS, etc.).

### Schedule Analysis

**1. Critical Path Method (CPM)**

Compute Early Start (ES), Early Finish (EF), Late Start (LS), Late Finish (LF), total float, and identify critical path tasks.

```bash
PYTHONPATH=src python -m open_gov_construction.cli schedule-cpm tasks.csv --out schedule_cpm.csv
```

Input CSV format:
```csv
task_id,name,duration_days,predecessors
A,Mobilization,5,
B,Foundation,10,A
C,Structure,15,"A,B"
D,Finishes,7,C
```

Output includes all CPM fields plus `critical` boolean flag.

**2. Monte Carlo Duration Risk**

Simulate project completion using triangular distributions for uncertainty.

```bash
PYTHONPATH=src python -m open_gov_construction.cli schedule-montecarlo tasks.csv --iterations 5000 --seed 42
```

Input CSV requires additional columns:
```csv
task_id,name,duration_days,predecessors,optimistic_days,likely_days,pessimistic_days
A,Mobilization,5,,4,5,7
B,Foundation,10,A,8,10,15
```

Returns P50, P80, P90 completion day estimates.

### Cost Compliance

**Screen line items for BABA and DBRA compliance:**

```bash
PYTHONPATH=src python -m open_gov_construction.cli cost-compliance cost_items.csv \
    --out cost_flags.csv \
    --domestic-threshold 55
```

Input CSV format:
```csv
line_id,description,material_type,origin_country,cost_usd,federal_funding,state,domestic_content_pct,dbra_classification
L001,Structural steel beams,iron_steel,US,125000,True,IN,,
L002,Install HVAC labor,construction_material,US,85000,True,OH,,HVAC-2024
L003,Manufactured valve,manufactured,US,15000,True,CA,62,
```

**Material types:**
- `iron_steel`: Must be 100% U.S. origin if federally funded
- `manufactured`: Requires domestic content percentage above threshold
- `construction_material`: Flags non-U.S. origin with federal funding

**DBRA screening:** Flags labor-related items (install, construct, erect, etc.) missing wage classification.

### Media Management

**Scan images and detect duplicates:**

```bash
PYTHONPATH=src python -m open_gov_construction.cli media-scan ./project_photos \
    --out media_inventory.csv \
    --dup-distance 5
```

Generates inventory with dimensions, brightness, perceptual hash, and lists potential duplicates (useful for documentation QC).

Supported formats: PNG, JPG, JPEG, BMP, TIF, TIFF

### Knowledge Graph

**Build graph from nodes and edges:**

```bash
PYTHONPATH=src python -m open_gov_construction.cli kg-build nodes.csv edges.csv --out graph.graphml
```

Nodes CSV:
```csv
id,label,type
C001,Main Contract,document
RFI-001,Rebar specification question,record
SUB-001,Steel submittal package,record
```

Edges CSV:
```csv
src,dst,rel
C001,RFI-001,references
C001,SUB-001,contains
```

**Query graph relationships:**

```bash
PYTHONPATH=src python -m open_gov_construction.cli kg-query nodes.csv edges.csv --node C001
```

## State-Specific Considerations

### California
- **Primary Agencies**: Caltrans, DGS, OSHPD/HCAI, local agencies
- **Notes**: Align with Caltrans Standard Specifications and local district requirements; consider California Environmental Quality Act (CEQA) compliance

### Indiana
- **Primary Agencies**: INDOT, IDOA, state/local agencies
- **Notes**: Review INDOT Standard Specifications; coordinate with IDEM for environmental permits

### Ohio
- **Primary Agencies**: Ohio DOT, OPW/PW, local agencies
- **Notes**: Align with Ohio EPA requirements and ODOT Construction and Material Specifications

State profiles in `src/open_gov_construction/states.py` can be extended with additional reporting preferences.

## Development

### Running Tests

```bash
# Quick test run
PYTHONPATH=src pytest -q

# Verbose output
PYTHONPATH=src pytest -v

# With coverage
PYTHONPATH=src pytest --cov=open_gov_construction --cov-report=term-missing
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking (requires mypy installation)
uv run mypy src
```

### Using tox

```bash
tox
```

## Project Structure

```
OpenGov-Construction/
├── pyproject.toml              # Project metadata and dependencies
├── tox.ini                     # Test automation configuration
├── .ruff.toml                  # Code style configuration
├── .gitignore                  # Git ignore patterns
├── README.md                   # This file
├── src/
│   └── open_gov_construction/
│       ├── __init__.py         # Package initialization
│       ├── cli.py              # CLI interface (Typer/Rich)
│       ├── states.py           # State profiles and agency info
│       ├── schedule.py         # CPM and Monte Carlo
│       ├── cost.py             # BABA/DBRA screening
│       ├── media.py            # Image scanning
│       ├── kg.py               # Knowledge graph
│       └── utils.py            # Shared utilities
└── tests/
    ├── test_schedule.py        # Schedule analysis tests
    ├── test_cost.py            # Cost compliance tests
    ├── test_kg.py              # Knowledge graph tests
    └── test_media.py           # Media scanning tests
```

## Extending the Toolkit

### Adding Features

1. **Document Parsing**: Integrate PDF extraction for RFIs, submittals, change orders
2. **PMIS Integration**: Import/export CSV from project management systems (Procore, e-Builder, etc.)
3. **Additional States**: Add profiles in `states.py` with agency-specific requirements
4. **Waiver Tracking**: Extend `cost.py` to handle BABA nonavailability waivers
5. **Agency Templates**: Create state-specific report generators

### Custom State Profiles

```python
# In src/open_gov_construction/states.py
def _tx() -> StateProfile:
    return StateProfile(
        code="TX",
        name="Texas",
        agencies=["TxDOT", "State Agencies"],
        reporting=ReportingPrefs(
            emphasize_cost_compliance=True,
            emphasize_schedule_risk=True,
            emphasize_document_control=False,
        ),
    )
```

## References

### Federal Regulations

- **BABA**: [2 CFR Part 184](https://www.ecfr.gov/current/title-2/subtitle-A/chapter-I/part-184) - Build America, Buy America Act
- **DBRA**: [40 U.S.C. §§ 3141-3148](https://www.govinfo.gov/content/pkg/USCODE-2011-title40/html/USCODE-2011-title40-subtitleII-partA-chap31-subchapIV.htm) - Davis-Bacon Related Acts
- **FAR**: [Federal Acquisition Regulation](https://www.acquisition.gov/browse/index/far) - Contract clauses

### Technical Resources

- **CPM Scheduling**: AACE International Recommended Practice 37R-06
- **Monte Carlo Risk**: Project Management Institute Practice Standard for Project Risk Management
- **Graph Databases**: NetworkX documentation for project relationship modeling

## Author

**Nik Jois**  
Email: nikjois@llamasearch.ai

## License

MIT License

Copyright (c) 2025 Nik Jois

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

**Version**: 0.1.0  
**Status**: Production Ready  
**Python**: 3.11+
