# 🚀 Quick Start Guide

Get up and running with AI Data Cleanser in 5 minutes!

## Step 1: Installation

```bash
# Navigate to the project directory
cd ai-data-cleanser

# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the CLI tool
pip install -e .
```

**Verify installation:**
```bash
cleanser --version
# Should output: AI Data Cleanser, version 0.1.0
```

## Step 2: Run the Demo

The easiest way to see it in action:

```bash
cleanser demo
```

This will:
1. ✅ Load the sample messy dataset
2. ✅ Profile the data quality
3. ✅ Clean and transform the data
4. ✅ Validate the results
5. ✅ Save cleaned data to `data/output/demo_clean.csv`
6. ✅ Export a JSON report to `data/output/demo_report.json`

## Step 3: Try With Your Own Data

### Option A: Basic Cleaning

```bash
cleanser clean your_data.csv
```

This will create `your_data_clean.csv` in the same directory.

### Option B: See What's Wrong First

```bash
cleanser profile your_data.csv
```

This shows you:
- Data quality score (0-100)
- Issues found in each column
- Null percentages
- Data type problems
- Outliers and duplicates

### Option C: Full Pipeline with Reports

```bash
cleanser clean your_data.csv \
  --output clean/sales_data.csv \
  --export-json reports/sales_report.json \
  --export-schema schemas/sales_schema.yaml
```

## Step 4: Understanding the Output

After cleaning, you'll see:

### Terminal Output
```
AI Data Cleanser v0.1.0

✅ Loaded 15 rows, 9 columns

┏━━━━━━━━━━━━━━━━━━━━━┓
┃ Dataset Overview    ┃
┗━━━━━━━━━━━━━━━━━━━━━┛
Total Rows: 15
Quality Score: 68.5/100
Duplicate Rows: 1

Operations Performed:
  1. Removed 1 duplicate rows
  2. Standardized 9 column names
  3. Filled 3 nulls in 'quantity'
  ...

✅ Cleaned data saved to output.csv
```

### Files Created

1. **Cleaned CSV** (`*_clean.csv`)
   - All issues fixed
   - Ready for analysis/ML

2. **JSON Report** (if `--export-json` used)
   - Complete quality profile
   - List of all transformations
   - Validation results

3. **Schema YAML** (if `--export-schema` used)
   - Data types for each column
   - Validation rules
   - Reusable for future datasets

## Common Use Cases

### Use Case 1: Sales Data from CRM

```bash
# Export from your CRM, get messy CSV
# Clean it:
cleanser clean crm_export.csv --aggressive

# The --aggressive flag will:
# - Remove columns that are >80% null
# - Cap outliers in numeric columns
# - Be more strict about invalid values
```

### Use Case 2: Recurring Data Pipeline

```bash
# First time: Create a schema from clean data
cleanser clean historical_data.csv --export-schema schema.yaml

# Future imports: Validate against schema
cleanser clean new_data.csv --validate-schema schema.yaml

# If validation fails, you'll see exactly what's wrong
```

### Use Case 3: Data Quality Audit

```bash
# Just want to see what's wrong? Don't clean yet:
cleanser clean messy_data.csv --report-only

# Review the report, then decide if you want to clean
```

### Use Case 4: Python Script Integration

```python
from src.utils.connectors import DataConnector
from src.cleaner import DataCleaner

# Load
df = DataConnector.read_file('input.csv')

# Clean
cleaner = DataCleaner()
df_clean, report = cleaner.clean(df)

# Check what was done
print(f"Fixed {report.cells_modified} cells")
print(f"Modified columns: {report.columns_modified}")

# Save
DataConnector.write_file(df_clean, 'output.csv')
```

## Tips & Tricks

### 🎯 When to use `--aggressive` mode
- You have many columns you don't need
- Outliers are likely errors (not real extreme values)
- You want maximum cleaning automation

### 🎯 When to use `--report-only`
- First time seeing the dataset
- Want to manually review issues before auto-fixing
- Need to justify cleaning decisions to stakeholders

### 🎯 When to use schemas
- Processing the same data format regularly
- Multiple people working with the data
- Want to catch schema drift early
- Building a data pipeline

### 🎯 Supported file formats
- ✅ CSV (`.csv`)
- ✅ Excel (`.xlsx`, `.xls`)
- ✅ JSON (`.json`)
- ✅ Parquet (`.parquet`)

## Troubleshooting

### "Command not found: cleanser"
```bash
# Make sure you installed it:
pip install -e .

# And activated the virtual environment:
source venv/bin/activate
```

### "No module named 'src'"
```bash
# Make sure you're in the project root directory:
cd ai-data-cleanser

# Then run commands
```

### "File not found" error
```bash
# Use absolute paths or check your working directory:
cleanser clean /full/path/to/data.csv

# Or use relative from project root:
cleanser clean data/input/myfile.csv
```

## Next Steps

1. ✅ Read the full [README.md](README.md) for all features
2. ✅ Check [docs/architecture.md](docs/architecture.md) to understand the internals
3. ✅ Explore the code in `src/` to customize behavior
4. ✅ Run tests: `pytest`
5. ✅ Star the repo if you find it useful! ⭐

## Getting Help

- 📖 Full documentation in `/docs`
- 🐛 Found a bug? Open an issue
- 💡 Have ideas? Start a discussion
- ❓ Questions? Check existing issues first

---

**Happy cleaning! 🧹✨**