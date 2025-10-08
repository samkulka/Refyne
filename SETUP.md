# Setup Guide

Complete setup instructions for AI Data Cleanser.

## Prerequisites

- **Python 3.9 or higher** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **git** (optional, for cloning)

Check your Python version:
```bash
python --version
# or
python3 --version
```

## Installation Methods

### Method 1: Standard Setup (Recommended)

```bash
# 1. Navigate to project directory
cd ai-data-cleanser

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install package in editable mode
pip install -e .

# 6. Verify installation
cleanser --version
```

### Method 2: Development Setup

If you plan to modify the code:

```bash
# Follow steps 1-3 from Method 1, then:

# 4. Install with dev dependencies
pip install -e ".[dev]"

# 5. Install AI features (optional)
pip install -e ".[ai]"

# 6. Run tests to verify
pytest
```

### Method 3: Using the Automated Script

```bash
# Run the setup script we created earlier
python complete_setup.py

# Then:
cd ai-data-cleanser
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Verify Installation

Run the test script:

```bash
python test_installation.py
```

You should see:
```
AI Data Cleanser - Installation Test
====================================
Testing imports...
✅ All core modules imported successfully

Checking sample data...
✅ Sample data found: data/sample/messy_sales_data.csv

Testing basic workflow...
  ✅ Loaded 15 rows, 9 columns
  ✅ Profiled data - Quality Score: 68.5/100
  ✅ Cleaned data - 15 -> 14 rows
  ✅ Modified 9 columns
  ✅ Saved cleaned data to data/output/test_clean.csv

Testing CLI availability...
✅ CLI command works: AI Data Cleanser, version 0.1.0

🎉 All tests passed! Installation successful!
```

## Directory Structure After Setup

```
ai-data-cleanser/
├── venv/                    # Virtual environment (created)
├── data/
│   ├── sample/
│   │   └── messy_sales_data.csv
│   ├── input/               # Put your files here
│   └── output/              # Cleaned files go here
├── src/
│   ├── main.py
│   ├── profiler.py
│   ├── cleaner.py
│   ├── validator.py
│   ├── semantic.py
│   └── utils/
├── tests/
├── requirements.txt
├── setup.py
├── README.md
├── QUICKSTART.md
└── cleanser.log            # Created after first run
```

## Configuration

### Optional: Environment Variables

For AI-powered features, set your OpenAI API key:

```bash
# On macOS/Linux (add to ~/.bashrc or ~/.zshrc for persistence)
export OPENAI_API_KEY="your-api-key-here"

# On Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# On Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

### Optional: Logging Configuration

By default, logs are written to `cleanser.log`. To customize:

```python
# Edit src/main.py, line ~15
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detail
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanser.log'),  # Change filename
        logging.StreamHandler()  # Remove to disable console logging
    ]
)
```

## Troubleshooting

### Issue: "Command 'cleanser' not found"

**Solution:**
```bash
# Make sure you installed the package
pip install -e .

# Verify it's in your PATH
which cleanser  # macOS/Linux
where cleanser  # Windows

# If still not found, try using python -m instead:
python -m src.main --help
```

### Issue: "No module named 'src'"

**Solution:**
```bash
# Make sure you're in the project root directory
cd ai-data-cleanser

# Then run your command
cleanser clean data.csv
```

### Issue: ImportError for packages

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific missing package
pip install pandas  # for example
```

### Issue: Permission denied on macOS/Linux

**Solution:**
```bash
# Make scripts executable
chmod +x test_installation.py

# Or run with python
python test_installation.py
```

### Issue: Virtual environment not activating

**Solution:**
```bash
# On Windows, you might need to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
venv\Scripts\activate
```

### Issue: Old Python version

**Solution:**
```bash
# Check version
python --version

# If < 3.9, install newer Python from python.org
# Then create venv with specific version:
python3.9 -m venv venv
# or
python3.11 -m venv venv
```

## Uninstallation

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove virtual environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# 3. Optionally remove the entire project
cd ..
rm -rf ai-data-cleanser
```

## Updating

```bash
# Pull latest changes (if using git)
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt

# Reinstall package
pip install -e .
```

## Next Steps

After successful installation:

1. ✅ Run the demo: `cleanser demo`
2. ✅ Read [QUICKSTART.md](QUICKSTART.md) for usage examples
3. ✅ Try with your own data
4. ✅ Explore the [README.md](README.md) for all features

## Support

If you encounter issues not covered here:

1. Check the [README.md](README.md) troubleshooting section
2. Review `cleanser.log` for error details
3. Run with verbose mode: `cleanser clean data.csv --help`
4. Open an issue on GitHub with:
   - Python version (`python --version`)
   - OS information
   - Complete error message
   - Steps to reproduce

---

**Happy data cleaning! 🧹**