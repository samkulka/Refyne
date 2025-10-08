#!/usr/bin/env python3
"""
Quick test - doesn't require CLI to be installed
Just run: python3 quick_test.py
"""

print("🧹 Refyne Data Cleanser - Quick Test\n")

# Test imports
print("1. Testing imports...")
try:
    from src.utils.connectors import DataConnector
    from src.profiler import DataProfiler
    from src.cleaner import DataCleaner
    from src.validator import DataValidator
    from src.utils.reporters import ReportGenerator
    print("   ✅ All modules imported successfully\n")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    print("   Make sure you're in the project root directory!")
    exit(1)

# Test with sample data
print("2. Loading sample data...")
try:
    df = DataConnector.read_file("data/sample/messy_sales_data.csv")
    print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns\n")
except Exception as e:
    print(f"   ❌ Failed to load data: {e}")
    exit(1)

# Profile
print("3. Profiling data quality...")
profiler = DataProfiler()
profile = profiler.profile_dataset(df)
print(f"   ✅ Quality Score: {profile.overall_quality_score}/100")
print(f"   ✅ Found {profile.duplicate_rows} duplicate rows")
print(f"   ✅ Found {sum(len(c.issues) for c in profile.column_profiles)} issues\n")

# Clean
print("4. Cleaning data...")
cleaner = DataCleaner(aggressive=False)
df_clean, report = cleaner.clean(df)
print(f"   ✅ {report.rows_before} → {report.rows_after} rows")
print(f"   ✅ {len(report.operations_performed)} operations performed")
print(f"   ✅ {report.cells_modified} cells modified\n")

print("5. Operations performed:")
for i, op in enumerate(report.operations_performed[:5], 1):
    print(f"   {i}. {op}")
if len(report.operations_performed) > 5:
    print(f"   ... and {len(report.operations_performed) - 5} more\n")

# Validate
print("\n6. Validating cleaned data...")
validator = DataValidator()
validation = validator.validate(df_clean)
print(f"   {'✅ PASSED' if validation.passed else '❌ FAILED'}")
print(f"   Errors: {len(validation.errors)}, Warnings: {len(validation.warnings)}\n")

# Save
print("7. Saving cleaned data...")
import os
os.makedirs("data/output", exist_ok=True)
DataConnector.write_file(df_clean, "data/output/quick_test_clean.csv")
print("   ✅ Saved to data/output/quick_test_clean.csv\n")

print("=" * 60)
print("🎉 SUCCESS! Everything is working!")
print("=" * 60)
print("\nNext steps:")
print("  1. Use the wrapper: ./run_cleanser.sh demo")
print("  2. Or run directly: python3 -m src.main demo")
