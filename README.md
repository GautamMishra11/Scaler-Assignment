# Asana Simulation: Seed Data Generator

Generate realistic, high-quality seed data for an Asana-like project management RL environment.

## Overview

This project creates a SQLite database simulating a B2B SaaS company's Asana workspace with 5,000-10,000 employees. The generated data includes:

- **Organizations & Teams**: Realistic org structures with proper hierarchies
- **Users**: Names from census data, appropriate role distributions
- **Projects**: Multiple types (sprints, campaigns, bug tracking) with realistic lifecycles
- **Tasks**: LLM-generated names and descriptions following real-world patterns
- **Comments & Activity**: Collaboration patterns matching actual usage
- **Custom Fields**: Project-specific metadata like priority, status, story points
- **Temporal Consistency**: All timestamps follow logical ordering and realistic patterns

## Features

 **Research-backed distributions** - Every metric cited from industry reports  
 **Real-world data sources** - Scraped from Y Combinator, GitHub, Asana templates  
 **LLM-enhanced content** - Natural task names and descriptions via Claude API  
**Edge cases included** - Overdue tasks, abandoned projects, unassigned work  
 **Temporal realism** - Activity patterns match working hours, sprints, holidays  
 **Full referential integrity** - Zero orphaned records, validated constraints  

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key (for LLM generation)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd asana-simulation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Generate Data

```bash
# Run the generator (takes ~30-45 minutes)
python src/main.py
```

The generated database will be at `output/asana_simulation.sqlite`.

## Project Structure

```
asana-simulation/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── schema.sql                         # Complete SQLite schema
├── .env.example                       # Environment template
├── documentation/
│   └── methodology.md                 # Detailed methodology document
├── src/
│   ├── main.py                        # Entry point
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── organizations.py           # Organization generator
│   │   ├── teams.py                   # Team & membership generator
│   │   ├── users.py                   # User generator
│   │   ├── projects.py                # Project & section generator
│   │   ├── tasks.py                   # Task generator (uses LLM)
│   │   ├── comments.py                # Comment generator
│   │   ├── custom_fields.py           # Custom field generator
│   │   └── stories.py                 # Activity story generator
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── yc_companies.py            # Y Combinator company scraper
│   │   ├── github_tasks.py            # GitHub issue pattern scraper
│   │   └── asana_templates.py         # Asana template scraper
│   ├── models/
│   │   ├── __init__.py
│   │   └── entities.py                # Data classes for entities
│   └── utils/
│       ├── __init__.py
│       ├── database.py                # Database connection manager
│       ├── logger.py                  # Logging configuration
│       ├── llm.py                     # LLM API wrapper
│       ├── dates.py                   # Date/time utilities
│       └── names.py                   # Name generation utilities
├── prompts/
│   ├── task_names.txt                 # LLM prompts for task generation
│   ├── task_descriptions.txt          # Description prompts
│   └── comments.txt                   # Comment prompts
└── output/
    └── asana_simulation.sqlite        # Generated database
```

## Configuration

Edit `src/main.py` to adjust generation parameters:

```python
class Config:
    # Organization size
    MIN_EMPLOYEES = 5000
    MAX_EMPLOYEES = 10000
    
    # Historical data range
    MONTHS_OF_HISTORY = 6
    
    # Scaling factors
    PROJECTS_PER_TEAM = 6
    TASKS_PER_USER = 12
    
    # LLM settings
    LLM_MODEL = "claude-sonnet-4-20250514"
    LLM_TEMPERATURE = 0.7
```

## Data Quality Metrics

The generator produces approximately:

| Entity | Count | Notes |
|--------|-------|-------|
| Organizations | 1 | Single company simulation |
| Teams | 60-100 | Reflects realistic dept structure |
| Users | 5,000-10,000 | Per assignment requirements |
| Projects | 400-800 | ~6 projects per team |
| Tasks | 60,000-120,000 | ~12 tasks per user |
| Comments | 18,000-36,000 | ~30% of tasks have comments |
| Stories | 150,000-300,000 | Full audit trail |
| Custom Fields | 200-400 | Avg 3-5 per project |

## Validation

The generator runs automatic validation checks:

1. **Orphaned records**: Ensures no dangling foreign keys
2. **Temporal consistency**: `created_at < completed_at < NOW()`
3. **Referential integrity**: All FKs resolve
4. **Completion rates**: Match research benchmarks (sprint: ~75%, ongoing: ~45%)
5. **Workload distribution**: No user has >30 active tasks

## LLM Prompt Examples

### Task Name Generation

```
Generate a realistic software engineering task name for a Backend Platform team 
at a B2B SaaS company in the Developer Tools industry.

Format: "[Component] - [Action] - [Detail]"

Examples:
- "API Gateway - Implement - Rate limiting for enterprise tier"
- "Database - Optimize - Query performance for analytics dashboard"
- "Auth Service - Debug - OAuth callback timeout issues"

Generate one task name following this pattern:
```

### Comment Generation

```
Generate a realistic project management comment for the task 
"{task_name}" in project "{project_name}".

Comment types: status update, question, blocker, feedback, or praise.
Length: 1-3 sentences.
Tone: Professional but casual.

Comment:
```

## Data Sources

### Scraped Sources
- **Company names**: Y Combinator Top Companies directory
- **User names**: US Census Bureau name frequency data (1990-2010)
- **Project names**: Asana public template gallery
- **Task patterns**: GitHub issues from top 100 SaaS repositories
- **Job titles**: LinkedIn standardized taxonomy

### Research Citations
- **Task completion rates**: Asana "Anatomy of Work Index 2023-2024"
- **Sprint duration**: State of Agile Report 2024
- **Team sizes**: LinkedIn Workforce Report, Dunbar's number research
- **Cycle times**: DevOps Research and Assessment (DORA) metrics
- **Activity patterns**: GitHub Pulse data, workplace collaboration research

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Add your API key to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### "Schema file not found"
Ensure `schema.sql` is in the project root.

### Generation is slow
- Normal runtime: 30-45 minutes for full dataset
- LLM calls are rate-limited and batched for efficiency
- Reduce `TASKS_PER_USER` in Config for faster testing

### Database is large
- Expected size: 50-150 MB
- To reduce: Lower `MAX_EMPLOYEES` or `TASKS_PER_USER`

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Generators
1. Create generator class in `src/generators/`
2. Inherit from `BaseGenerator`
3. Implement `generate()` method
4. Add to main.py execution flow

### Modifying Distributions
Edit methodology in generator classes. All distributions should be:
- Cited from research
- Documented in methodology.md
- Validated with statistical tests

## License

MIT License - See LICENSE file for details.

## Citation

If you use this dataset generator in your research, please cite:

```bibtex
@software{asana_simulation_2026,
  title={Asana Simulation: High-Quality Seed Data for RL Environments},
  author={Gautam Mishra},
  year={2026},
  url={https://github.com/GautamMishra11/Scaler-Assignment}
}
```

## Support

For questions or issues:
- Open a GitHub issue
- Email: misheard.gautam626@gmail.com

---

