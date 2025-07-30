# Diplomacy Wizard Study Assets

This repository contains assets and tools for a study on AI assistance in the game of Diplomacy. The study investigates how different types of AI suggestions and friction mechanisms affect player decision-making in strategic board games.

## Project Overview

The Diplomacy Wizard Study examines the impact of AI assistance on human players in the classic strategy game Diplomacy. The study uses various AI models (including Cicero and LR5) to generate move suggestions and investigates how different presentation methods and friction mechanisms affect player performance and decision-making.

## Repository Structure

### Core Components

- **`dipnet/`** - Main study data and scenarios
  - `data/` - JSON files containing game states and AI suggestions
  - `svgs/` - Visual representations of game boards
  - `html/` - Formatted suggestion displays
  - `mp4/` - Game history videos
  - `participant/` - Individual participant data

- **`rank_by_experts/`** - Expert ranking and evaluation tools
  - `rank_center/` - FastAPI application for expert evaluations
  - `sortings/` - Sorting and ranking algorithms

- **`generate_questions/`** - Question generation for study scenarios
  - `generate_title.py` - Creates HTML question templates

- **`treatments_assignment/`** - Study treatment design and assignment
  - `treatments_scenarios.py` - Generates treatment combinations
  - `treatments.csv` - Treatment assignments for participants

- **`from_reddit/`** - Reddit-based scenario collection
  - Contains real Diplomacy game scenarios from Reddit
  - Includes data processing scripts

- **`random-dip/`** - Randomly generated Diplomacy scenarios

### Utility Scripts

- **`make-table.py`** - Converts JSON data to HTML tables for the study questions
- **`get_textual_suggestions.py`** - Extracts move suggestions from JSON files
- **`open-a-random-svg.py`** - Utility to open random SVG files for test
- **`constants.py`** - Game constants (POWERS list)

## 1st Study Design

### Treatment Variables

The study investigates three main factors:

1. **Suggestion Type (TYPE)**
   - `null` - No suggestions
   - `sugg-TB` - Text-based suggestions
   - `sugg-TKT` - Text-based with key terms
   - `sugg-VB` - Visual-based suggestions
   - `sugg-VKT` - Visual-based with key terms

### Scenarios

| ID                  | Turn | Depth | Type | Summary                                                                                                                                                                                                                  | Stance                                                                                                                                         |
|---------------------|------|-------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| 46_F1903M_ITALY     | 8    | E     | E-C  | Attacking Austria's units in TRI supported by neighbors' units. Attacking Turkey's units in EAS without support (bad suggestion?)                                                                                         | AUSTRIA: -1<br>TURKEY: -1<br>RUSSIA: 1                                                                                                         |
| 88_S1902M_AUSTRIA   | 4    | E     | E-N  | Attacking ITALY's army in TRI from BUD supported by SER. Doing the same thing on Russia's fleet on RUM                                                                                                                    | ITALY: 0<br>RUSSIA: 0<br>TURKEY: 0                                                                                                             |
| 45_F1908M_TURKEY    | 7    | E     | E-A  | Trying to get SEV from ITALY and push ITALY's fleet back from CON                                                                                                                                                         | ITALY: 1                                                                                                                                       |
| 69_S1904M_ITALY     | 10   | M     | M-C  | Attacking Austria's GRE with AEG supported by ION fleets. Forming a wall against Austria and taking SER which doesn't include Austria's forces                                                                            | AUSTRIA: -1<br>RUSSIA: -1<br>TURKEY: 1<br>FRANCE: 1                                                                                           |
| 81_F1905M_FRANCE    | 15   | M     | M-N  | Taking unoccupied states of FRANCE and ITALY and fighting with FRANCE and England on MAO and KIE                                                                                                                           | ITALY: 0<br>FRANCE: 0<br>GERMANY: 0<br>ENGLAND: 0                                                                                              |
| 69_S1905M_GERMANY   | 15   | M     | M-A  | Attacking last state of England (LON) with YOR supported by NTH fleets. Trying to make north safe from Russia and expand west against France                                                                              | ENGLAND: 1<br>FRANCE: 1<br>RUSSIA: 1<br>ITALY: -1                                                                                              |
| 69_S1910M_ITALY     | 23   | H     | H-C  | Taking the last state of Turkey (ANK). Forming a wall against Russia and France. Taking SPA and trying to push back France. Tried to take RUM with choked force in UKR (may be a deal with Russia to support vs France) | TURKEY: -1<br>RUSSIA: 1<br>FRANCE: -1                                                                                                          |
| 62_F1906M_GERMANY   | 17   | H     | H-N  | Moving LVN to STP to bounce Turkey. Same against Russia in PRU. MUN vs ITALY's TYR. Capturing seas around England, either to support France or eliminate England                                                          | TURKEY: 0<br>GERMANY: 0<br>ITALY: 0<br>ENGLAND: 0<br>FRANCE: 0                                                                                 |
| 23_S1909M_TURKEY    | 17   | H     | H-A  | Trying to take unoccupied TUN from France, and VEN from Italy (milder). Supporting Russia's war against France                                                                                                            | FRANCE: 1<br>ITALY: -1<br>RUSSIA: -1                                                                                                           |


## 2nd Study Design [Think-aloud]

### Treatment Variables

The study investigates three main factors:

1. **Suggestion Type (TYPE)**
   - `null` - No suggestions
   - `sugg-TB` - Text-based suggestions
   - `sugg-TKT` - Text-based with key terms
   - `sugg-VB` - Visual-based suggestions
   - `sugg-VKT` - Visual-based with key terms

2. **Side (SIDE)**
   - `null` - No side information
   - `side-self` - Suggestions for the player
   - `side-other` - Suggestions for other players
   - `both` - Both self and other suggestions

3. **Friction (FRICTION)**
   - `null` - No friction
   - `YCO` - You can only (restriction)
   - `ROO` - Read only (restriction)
   - `ERO` - Early reveal only

### Scenarios

The study uses 4 main scenarios:
- Q1: 31_S1906M_ITALY
- Q2: 32_S1905M_ENGLAND  
- Q3: 62_F1906M_GERMANY
- Q4: 78_F1904M_AUSTRIA

### Treatment Assignment

The `treatments.csv` file contains participant assignments with columns:
- `participant_id`
- `scenario1-4` - Scenario order for each participant
- `type1-4` - Suggestion type for each scenario
- `side1-4` - Side information for each scenario
- `friction1-4` - Friction mechanism for each scenario


### Data Process: Generating Questions

To generate a question for a specific scenario:

```bash
cd generate_questions
python generate_title.py Q1  # Generates question for scenario Q1
```

### Data Process: Processing Data

To extract suggestions from JSON files:

```bash
python get_textual_suggestions.py path/to/data.json --best
```

## Data Format

### Game State JSON Structure

```json
{
  "alterations": {
    "GERMANY": [
      ["A BER", "A BER - KIE", 0.85],
      ["F KIE", "F KIE - BAL", 0.72]
    ],
    "FRANCE": [...]
  }
}
```

## Getting Started

### Prerequisites

- Python 3.7+
- Required packages: `fastapi`, `uvicorn`, `sqlalchemy`, `jinja2`, `python-multipart`, `pandas`, `beautifulsoup4`

### Installation

```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart pandas beautifulsoup4
```

### Evaluation: Running the Expert Ranking System

1. Navigate to the ranking center:
```bash
cd rank_by_experts/rank_center
```

2. Initialize the database (first time only):
```bash
python init_db.py
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

## Contributing

This repository is part of a research study. For questions about the study design or data, please contact the research team.

## License

This project is for research purposes. Please respect the study protocol and data privacy requirements.
