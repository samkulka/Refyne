"""
AI Data Cleanser - Main CLI Entry Point
"""
import click
import logging
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys

from src.utils.connectors import DataConnector
from src.profiler import DataProfiler
from src.cleaner import DataCleaner
from src.validator import DataValidator
from src.utils.reporters import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    AI Data Cleanser - Automatically clean, validate, and transform messy data
    
    Transform your messy business data into AI-ready datasets with one command.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: input_clean.csv)')
@click.option('--aggressive', '-a', is_flag=True, help='Apply aggressive cleaning (remove high-null columns)')
@click.option('--report-only', '-r', is_flag=True, help='Generate report only, do not clean data')
@click.option('--export-schema', type=click.Path(), help='Export inferred schema to YAML file')
@click.option('--validate-schema', type=click.Path(exists=True), help='Validate against existing schema YAML')
@click.option('--export-json', type=click.Path(), help='Export complete report as JSON')
@click.option('--no-progress', is_flag=True, help='Disable progress indicators')
def clean(input_file, output, aggressive, report_only, export_schema, validate_schema, export_json, no_progress):
    """
    Clean and validate a data file
    
    Examples:
    
        # Basic cleaning
        cleanser clean data.csv
        
        # Aggressive mode (removes high-null columns)
        cleanser clean data.csv --aggressive
        
        # Just generate a report, don't clean
        cleanser clean data.csv --report-only
        
        # Export schema
        cleanser clean data.csv --export-schema schema.yaml
        
        # Validate against schema
        cleanser clean data.csv --validate-schema schema.yaml
    """
    try:
        console.print(f"\n[bold cyan]AI Data Cleanser v0.1.0[/bold cyan]\n")
        
        # Determine output path
        if not output and not report_only:
            input_path = Path(input_file)
            output = str(input_path.parent / f"{input_path.stem}_clean{input_path.suffix}")
        
        # Initialize components
        reporter = ReportGenerator(use_rich=not no_progress)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=no_progress or report_only
        ) as progress:
            
            # Step 1: Load data
            task1 = progress.add_task("[cyan]Loading data...", total=None)
            df = DataConnector.read_file(input_file)
            progress.update(task1, completed=True)
            console.print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns\n")
            
            # Step 2: Profile data
            task2 = progress.add_task("[cyan]Profiling data quality...", total=None)
            profiler = DataProfiler()
            profile = profiler.profile_dataset(df)
            progress.update(task2, completed=True)
            
            # Print profile report
            console.print()
            reporter.print_profile_report(profile)
            console.print()
            
            # If report-only mode, stop here
            if report_only:
                console.print("[bold green]Report generated successfully![/bold green]")
                return
            
            # Step 3: Clean data
            task3 = progress.add_task("[cyan]Cleaning data...", total=None)
            cleaner = DataCleaner(aggressive=aggressive)
            df_clean, cleaning_report = cleaner.clean(df)
            progress.update(task3, completed=True)
            
            # Print cleaning report
            console.print()
            reporter.print_cleaning_report(cleaning_report)
            console.print()
            
            # Step 4: Validate cleaned data
            task4 = progress.add_task("[cyan]Validating cleaned data...", total=None)
            validator = DataValidator(strict=False)
            
            # Load schema if provided
            schema = None
            if validate_schema:
                schema = DataValidator.load_schema(validate_schema)
                console.print(f"📋 Loaded schema from {validate_schema}")
            
            validation_report = validator.validate(df_clean, schema=schema)
            progress.update(task4, completed=True)
            
            # Print validation report
            console.print()
            reporter.print_validation_report(validation_report)
            console.print()
            
            # Step 5: Export schema if requested
            if export_schema:
                task5 = progress.add_task("[cyan]Exporting schema...", total=None)
                inferred_schema = DataValidator.create_schema_from_df(df_clean)
                DataValidator.save_schema(inferred_schema, export_schema)
                progress.update(task5, completed=True)
                console.print(f"✅ Schema exported to {export_schema}\n")
            
            # Step 6: Save cleaned data
            task6 = progress.add_task(f"[cyan]Saving cleaned data to {output}...", total=None)
            DataConnector.write_file(df_clean, output)
            progress.update(task6, completed=True)
            
            console.print(f"\n✅ [bold green]Cleaned data saved to {output}[/bold green]")
            
            # Step 7: Export JSON report if requested
            if export_json:
                reporter.export_json_report(profile, cleaning_report, validation_report, export_json)
                console.print(f"✅ JSON report exported to {export_json}")
            
            # Final summary
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"  • Input rows: {len(df):,}")
            console.print(f"  • Output rows: {len(df_clean):,}")
            console.print(f"  • Quality score: {profile.overall_quality_score}/100")
            console.print(f"  • Validation: {'✅ PASSED' if validation_report.passed else '❌ FAILED'}")
            console.print()
            
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error during cleaning process")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def profile(input_file):
    """
    Generate a detailed data quality profile report
    
    Example:
        cleanser profile data.csv
    """
    try:
        console.print(f"\n[bold cyan]Data Quality Profiler[/bold cyan]\n")
        
        # Load data
        console.print(f"Loading {input_file}...")
        df = DataConnector.read_file(input_file)
        console.print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns\n")
        
        # Profile
        console.print("Analyzing data quality...")
        profiler = DataProfiler()
        profile = profiler.profile_dataset(df)
        
        # Generate and print report
        reporter = ReportGenerator(use_rich=True)
        console.print()
        reporter.print_profile_report(profile)
        
        # Save text report
        report_path = Path(input_file).parent / f"{Path(input_file).stem}_profile.txt"
        report_text = reporter.generate_profile_report(profile, str(report_path))
        console.print(f"\n✅ Detailed report saved to {report_path}")
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error during profiling")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), default='schema.yaml', help='Output schema file path')
def infer_schema(input_file, output):
    """
    Infer and export a data schema from a clean dataset
    
    Example:
        cleanser infer-schema clean_data.csv --output my_schema.yaml
    """
    try:
        console.print(f"\n[bold cyan]Schema Inference[/bold cyan]\n")
        
        # Load data
        console.print(f"Loading {input_file}...")
        df = DataConnector.read_file(input_file)
        console.print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns\n")
        
        # Infer schema
        console.print("Inferring schema...")
        schema = DataValidator.create_schema_from_df(df, nullable=True)
        
        # Save schema
        DataValidator.save_schema(schema, output)
        console.print(f"✅ Schema saved to {output}")
        
        # Print schema summary
        console.print(f"\n[bold]Schema Summary:[/bold]")
        console.print(f"  • Columns: {len(schema.columns)}")
        console.print(f"  • Strict mode: {schema.strict}")
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error during schema inference")
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('schema_file', type=click.Path(exists=True))
def validate(input_file, schema_file):
    """
    Validate a dataset against a schema
    
    Example:
        cleanser validate data.csv schema.yaml
    """
    try:
        console.print(f"\n[bold cyan]Data Validation[/bold cyan]\n")
        
        # Load data
        console.print(f"Loading {input_file}...")
        df = DataConnector.read_file(input_file)
        console.print(f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns\n")
        
        # Load schema
        console.print(f"Loading schema from {schema_file}...")
        schema = DataValidator.load_schema(schema_file)
        console.print(f"✅ Schema loaded\n")
        
        # Validate
        console.print("Validating data...")
        validator = DataValidator(strict=False)
        report = validator.validate(df, schema=schema)
        
        # Print report
        reporter = ReportGenerator(use_rich=True)
        console.print()
        reporter.print_validation_report(report)
        
        # Exit with error code if validation failed
        if not report.passed:
            sys.exit(1)
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error during validation")
        sys.exit(1)


@cli.command()
def demo():
    """
    Run a demo with the sample messy dataset
    """
    try:
        console.print(f"\n[bold cyan]AI Data Cleanser - Demo Mode[/bold cyan]\n")
        
        # Find sample data
        sample_file = Path("data/sample/messy_sales_data.csv")
        
        if not sample_file.exists():
            console.print("[bold red]Error:[/bold red] Sample data file not found")
            console.print(f"Expected location: {sample_file}")
            sys.exit(1)
        
        console.print(f"Running demo with sample dataset: {sample_file}\n")
        
        # Run the cleaning process
        from click.testing import CliRunner
        runner = CliRunner()
        
        result = runner.invoke(clean, [
            str(sample_file),
            '--output', 'data/output/demo_clean.csv',
            '--export-json', 'data/output/demo_report.json'
        ])
        
        if result.exit_code == 0:
            console.print("\n[bold green]Demo completed successfully![/bold green]")
            console.print("\nCheck the output folder for:")
            console.print("  • data/output/demo_clean.csv - Cleaned data")
            console.print("  • data/output/demo_report.json - Full report")
        else:
            console.print(f"\n[bold red]Demo failed:[/bold red] {result.output}")
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Error during demo")
        sys.exit(1)


if __name__ == '__main__':
    cli()