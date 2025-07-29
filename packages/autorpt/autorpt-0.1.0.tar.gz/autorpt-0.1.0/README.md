# autorpt

[![image](https://img.shields.io/pypi/v/autorpt.svg)](https://pypi.python.org/pypi/autorpt)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Automated budget report generator for grant management with Excel input and Word output**

- Free software: MIT license
- Documentation: https://VRConservation.github.io/autorpt

## Features

- **Excel Budget Input**: Load budget data from `budget.xlsx` with columns for Task, Budgeted, Spent, and Remaining amounts
- **Automated Report Generation**: Creates professional Word documents with tables, charts, and formatted content
- **Customizable Content**: Use `content.md` to customize report sections (Summary, Deliverables Progress, Challenges, etc.)
- **Command Line Interface**: Run from terminal with options for input/output files
- **Python API**: Use programmatically in your own scripts
- **Visual Charts**: Automatically generates budget comparison charts
- **Professional Formatting**: Clean, business-ready Word document output

## Quick Start

### Installation
```bash
pip install autorpt
```

### Basic Usage

1. **Prepare your budget file**: Ensure `budget.xlsx` exists with columns:
   - `Task`: Description of budget items
   - `Budgeted`: Total budgeted amounts
   - `Spent`: Amount spent to date
   - `Remaining`: Remaining budget

2. **Generate report**:
   ```bash
   # Command line (uses budget.xlsx by default)
   autorpt
   
   # Or specify custom files
   autorpt --input my_budget.xlsx --output custom_report.docx
   ```

3. **Python API**:
   ```python
   import autorpt
   
   # Simple usage
   autorpt.generate_report()
   
   # Custom files
   autorpt.generate_report('my_budget.xlsx', 'my_report.docx')
   ```

### File Structure

Your project directory should contain:
```
your_project/
├── budget.xlsx          # Your budget data (required)
├── content.md           # Custom content sections (optional)
└── reports/             # Generated reports folder (auto-created)
```

### Customizing Content

Create a `content.md` file to customize report sections:

```markdown
# Summary
Your custom summary content here...

# Deliverables Progress
- Custom deliverable 1
- Custom deliverable 2

# Challenges
Current project challenges...

# Next Period Activities
Planned activities...
```

## Command Line Options

```bash
autorpt --help
autorpt --input budget.xlsx --output report.docx --verbose
```

- `--input, -i`: Input Excel file (default: budget.xlsx)
- `--output, -o`: Output Word document filename
- `--verbose, -v`: Enable verbose output

## Output

The package generates:
- Professional Word document in `reports/` folder
- Budget comparison charts
- Automatically formatted tables
- Summary statistics and key insights
