#!/usr/bin/env python
"""
Quick test script to verify the AI Data Cleanser installation
Run this after installing to make sure everything works
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.utils.connectors import DataConnector
        from src.profiler import DataProfiler
        from src.cleaner import DataCleaner
        from src.validator import DataValidator
        from src.utils.reporters import ReportGenerator
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_sample_data_exists():
    """Test that sample data file exists"""
    print("\nChecking sample data...")
    
    sample_file = Path("data/sample/messy_sales_data.csv")
    
    if sample_file.exists():
        print(f"✅ Sample data found: {sample_file}")
        return True
    else:
        print(f"❌ Sample data not found: {sample_file}")
        return False


def test_basic_workflow():
    """Test the basic cleaning workflow"""
    print("\nTesting basic workflow...")
    
    try:
        from src.utils.connectors import DataConnector
        from src.profiler import DataProfiler
        from src.cleaner import DataCleaner
        
        # Load sample data
        df = DataConnector.read_file("data/sample/messy_sales_data.csv")
        print(f"  ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Profile
        profiler = DataProfiler()
        profile = profiler.profile_dataset(df)
        print(f"  ✅ Profiled data - Quality Score: {profile.overall_quality_score}/100")
        
        # Clean
        cleaner = DataCleaner()
        df_clean, report = cleaner.clean(df)
        print(f"  ✅ Cleaned data - {report.rows_before} -> {report.rows_after} rows")
        print(f"  ✅ Modified {len(report.columns_modified)} columns")
        
        # Save to output
        output_dir = Path("data/output")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "test_clean.csv"
        DataConnector.write_file(df_clean, str(output_file))
        print(f"  ✅ Saved cleaned data to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_available():
    """Test that CLI command is available"""
    print("\nTesting CLI availability...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["cleanser", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ CLI command works: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ CLI command failed with code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ 'cleanser' command not found")
        print("   Run: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Error testing CLI: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Data Cleanser - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Sample Data", test_sample_data_exists),
        ("Basic Workflow", test_basic_workflow),
        ("CLI Command", test_cli_available),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for (name, _), result in zip(tests, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Installation successful!")
        print("\nNext steps:")
        print("  1. Run the demo: cleanser demo")
        print("  2. Try cleaning your own data: cleanser clean your_file.csv")
        print("  3. Read QUICKSTART.md for more examples")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Make sure you're in the project root directory")
        print("  2. Activate virtual environment: source venv/bin/activate")
        print("  3. Install dependencies: pip install -r requirements.txt")
        print("  4. Install package: pip install -e .")
        return 1


if __name__ == "__main__":
    sys.exit(main())