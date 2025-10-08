"""
Report generation for profiling, cleaning, and validation results
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from tabulate import tabulate
import logging

from src.profiler import DatasetProfile, ColumnProfile
from src.cleaner import CleaningReport
from src.validator import ValidationReport, ValidationLevel

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports in various formats"""
    
    def __init__(self, use_rich: bool = True):
        """
        Args:
            use_rich: Use rich library for colored terminal output
        """
        self.console = Console() if use_rich else None
    
    def generate_profile_report(self, profile: DatasetProfile, output_path: str = None) -> str:
        """
        Generate data profiling report
        
        Args:
            profile: DatasetProfile from profiler
            output_path: Optional path to save report
            
        Returns:
            Report as string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DATA QUALITY PROFILE REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Dataset overview
        report_lines.append("DATASET OVERVIEW")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Rows:           {profile.total_rows:,}")
        report_lines.append(f"Total Columns:        {profile.total_columns}")
        report_lines.append(f"Duplicate Rows:       {profile.duplicate_rows:,}")
        report_lines.append(f"Memory Usage:         {profile.memory_usage_mb:.2f} MB")
        report_lines.append(f"Quality Score:        {profile.overall_quality_score}/100")
        report_lines.append("")
        
        # Issues summary
        if profile.issues_summary:
            report_lines.append("ISSUES SUMMARY")
            report_lines.append("-" * 80)
            for issue_type, count in profile.issues_summary.items():
                if count > 0:
                    report_lines.append(f"  • {issue_type.replace('_', ' ').title()}: {count}")
            report_lines.append("")
        
        # Column details
        report_lines.append("COLUMN DETAILS")
        report_lines.append("-" * 80)
        
        for col_profile in profile.column_profiles:
            report_lines.append(f"\n📊 {col_profile.name}")
            report_lines.append(f"   Type: {col_profile.inferred_type} (dtype: {col_profile.dtype})")
            report_lines.append(f"   Completeness: {100 - col_profile.null_percentage:.1f}%")
            report_lines.append(f"   Unique Values: {col_profile.unique_count:,} ({col_profile.unique_percentage:.1f}%)")
            
            # Show sample values
            if col_profile.sample_values:
                samples = ', '.join([str(v) for v in col_profile.sample_values[:3]])
                report_lines.append(f"   Sample: {samples}")
            
            # Show type-specific stats
            if col_profile.numeric_stats:
                stats = col_profile.numeric_stats
                report_lines.append(f"   Range: {stats.get('min', 'N/A')} to {stats.get('max', 'N/A')}")
                report_lines.append(f"   Mean: {stats.get('mean', 'N/A'):.2f}, Median: {stats.get('median', 'N/A'):.2f}")
                if 'outlier_count' in stats:
                    report_lines.append(f"   Outliers: {stats['outlier_count']}")
            
            elif col_profile.text_stats:
                stats = col_profile.text_stats
                report_lines.append(f"   Length: {stats.get('min_length', 0)} to {stats.get('max_length', 0)} chars")
            
            # Show issues
            if col_profile.issues:
                report_lines.append(f"   ⚠️  Issues:")
                for issue in col_profile.issues:
                    report_lines.append(f"      - {issue}")
        
        report_text = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            Path(output_path).write_text(report_text)
            logger.info(f"Profile report saved to {output_path}")
        
        return report_text
    
    def print_profile_report(self, profile: DatasetProfile) -> None:
        """Print profile report to console with rich formatting"""
        
        if not self.console:
            print(self.generate_profile_report(profile))
            return
        
        # Header
        self.console.print(Panel.fit(
            "[bold cyan]DATA QUALITY PROFILE REPORT[/bold cyan]",
            border_style="cyan"
        ))
        
        # Overview table
        overview_table = Table(title="Dataset Overview", box=box.ROUNDED)
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="white")
        
        overview_table.add_row("Total Rows", f"{profile.total_rows:,}")
        overview_table.add_row("Total Columns", str(profile.total_columns))
        overview_table.add_row("Duplicate Rows", f"{profile.duplicate_rows:,}")
        overview_table.add_row("Memory Usage", f"{profile.memory_usage_mb:.2f} MB")
        
        # Color code quality score
        score = profile.overall_quality_score
        if score >= 80:
            score_color = "green"
        elif score >= 60:
            score_color = "yellow"
        else:
            score_color = "red"
        overview_table.add_row("Quality Score", f"[{score_color}]{score}/100[/{score_color}]")
        
        self.console.print(overview_table)
        self.console.print()
        
        # Issues summary
        if any(profile.issues_summary.values()):
            issues_table = Table(title="Issues Found", box=box.ROUNDED)
            issues_table.add_column("Issue Type", style="yellow")
            issues_table.add_column("Count", justify="right", style="red")
            
            for issue_type, count in profile.issues_summary.items():
                if count > 0:
                    issues_table.add_row(
                        issue_type.replace('_', ' ').title(),
                        str(count)
                    )
            
            self.console.print(issues_table)
            self.console.print()
        
        # Column summary table
        col_table = Table(title="Column Summary", box=box.ROUNDED)
        col_table.add_column("Column", style="cyan")
        col_table.add_column("Type", style="magenta")
        col_table.add_column("Nulls", justify="right")
        col_table.add_column("Unique", justify="right")
        col_table.add_column("Issues", style="yellow")
        
        for col in profile.column_profiles:
            null_color = "red" if col.null_percentage > 50 else "yellow" if col.null_percentage > 10 else "green"
            
            col_table.add_row(
                col.name,
                col.inferred_type,
                f"[{null_color}]{col.null_percentage:.1f}%[/{null_color}]",
                f"{col.unique_count:,}",
                str(len(col.issues))
            )
        
        self.console.print(col_table)
    
    def generate_cleaning_report(self, report: CleaningReport, output_path: str = None) -> str:
        """Generate cleaning operations report"""
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DATA CLEANING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Rows Before:          {report.rows_before:,}")
        report_lines.append(f"Rows After:           {report.rows_after:,}")
        report_lines.append(f"Rows Removed:         {report.rows_removed:,}")
        report_lines.append(f"Cells Modified:       {report.cells_modified:,}")
        report_lines.append(f"Columns Modified:     {len(report.columns_modified)}")
        report_lines.append("")
        
        report_lines.append("OPERATIONS PERFORMED")
        report_lines.append("-" * 80)
        for i, operation in enumerate(report.operations_performed, 1):
            report_lines.append(f"{i}. {operation}")
        
        if report.columns_modified:
            report_lines.append("")
            report_lines.append("MODIFIED COLUMNS")
            report_lines.append("-" * 80)
            for col in sorted(report.columns_modified):
                report_lines.append(f"  • {col}")
        
        report_text = "\n".join(report_lines)
        
        if output_path:
            Path(output_path).write_text(report_text)
            logger.info(f"Cleaning report saved to {output_path}")
        
        return report_text
    
    def print_cleaning_report(self, report: CleaningReport) -> None:
        """Print cleaning report to console"""
        
        if not self.console:
            print(self.generate_cleaning_report(report))
            return
        
        self.console.print(Panel.fit(
            "[bold green]DATA CLEANING REPORT[/bold green]",
            border_style="green"
        ))
        
        # Summary
        summary_table = Table(title="Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Rows Before", f"{report.rows_before:,}")
        summary_table.add_row("Rows After", f"{report.rows_after:,}")
        summary_table.add_row("Rows Removed", f"[red]{report.rows_removed:,}[/red]")
        summary_table.add_row("Cells Modified", f"[yellow]{report.cells_modified:,}[/yellow]")
        summary_table.add_row("Columns Modified", str(len(report.columns_modified)))
        
        self.console.print(summary_table)
        self.console.print()
        
        # Operations
        self.console.print("[bold]Operations Performed:[/bold]")
        for i, op in enumerate(report.operations_performed, 1):
            self.console.print(f"  {i}. {op}")
    
    def generate_validation_report(self, report: ValidationReport, output_path: str = None) -> str:
        """Generate validation report"""
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DATA VALIDATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall status
        status = "✅ PASSED" if report.passed else "❌ FAILED"
        report_lines.append(f"Status: {status}")
        report_lines.append(f"Total Issues: {report.total_issues}")
        report_lines.append(f"  - Errors: {len(report.errors)}")
        report_lines.append(f"  - Warnings: {len(report.warnings)}")
        report_lines.append(f"  - Info: {len(report.info)}")
        report_lines.append(f"Schema Compliant: {'Yes' if report.schema_compliant else 'No'}")
        report_lines.append("")
        
        # Errors
        if report.errors:
            report_lines.append("ERRORS")
            report_lines.append("-" * 80)
            for issue in report.errors:
                col_prefix = f"[{issue.column}] " if issue.column else ""
                report_lines.append(f"  ❌ {col_prefix}{issue.message}")
                if issue.sample_values:
                    report_lines.append(f"     Samples: {issue.sample_values}")
            report_lines.append("")
        
        # Warnings
        if report.warnings:
            report_lines.append("WARNINGS")
            report_lines.append("-" * 80)
            for issue in report.warnings:
                col_prefix = f"[{issue.column}] " if issue.column else ""
                report_lines.append(f"  ⚠️  {col_prefix}{issue.message}")
            report_lines.append("")
        
        # Info
        if report.info:
            report_lines.append("INFORMATION")
            report_lines.append("-" * 80)
            for issue in report.info:
                col_prefix = f"[{issue.column}] " if issue.column else ""
                report_lines.append(f"  ℹ️  {col_prefix}{issue.message}")
        
        report_text = "\n".join(report_lines)
        
        if output_path:
            Path(output_path).write_text(report_text)
            logger.info(f"Validation report saved to {output_path}")
        
        return report_text
    
    def print_validation_report(self, report: ValidationReport) -> None:
        """Print validation report to console"""
        
        if not self.console:
            print(self.generate_validation_report(report))
            return
        
        # Header with status
        if report.passed:
            header = Panel.fit(
                "[bold green]✅ VALIDATION PASSED[/bold green]",
                border_style="green"
            )
        else:
            header = Panel.fit(
                "[bold red]❌ VALIDATION FAILED[/bold red]",
                border_style="red"
            )
        
        self.console.print(header)
        
        # Summary
        summary_table = Table(title="Summary", box=box.ROUNDED)
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Count", justify="right")
        
        summary_table.add_row("Errors", f"[red]{len(report.errors)}[/red]")
        summary_table.add_row("Warnings", f"[yellow]{len(report.warnings)}[/yellow]")
        summary_table.add_row("Info", f"[blue]{len(report.info)}[/blue]")
        
        self.console.print(summary_table)
        self.console.print()
        
        # Show issues
        if report.errors:
            self.console.print("[bold red]Errors:[/bold red]")
            for issue in report.errors:
                col_str = f"[{issue.column}] " if issue.column else ""
                self.console.print(f"  ❌ {col_str}{issue.message}")
            self.console.print()
        
        if report.warnings:
            self.console.print("[bold yellow]Warnings:[/bold yellow]")
            for issue in report.warnings:
                col_str = f"[{issue.column}] " if issue.column else ""
                self.console.print(f"  ⚠️  {col_str}{issue.message}")
            self.console.print()
    
    def export_json_report(self, profile: DatasetProfile, cleaning: CleaningReport, 
                          validation: ValidationReport, output_path: str) -> None:
        """Export complete report as JSON"""
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "profile": {
                "total_rows": profile.total_rows,
                "total_columns": profile.total_columns,
                "quality_score": profile.overall_quality_score,
                "duplicate_rows": profile.duplicate_rows,
                "memory_mb": profile.memory_usage_mb,
                "issues_summary": profile.issues_summary,
                "columns": [
                    {
                        "name": col.name,
                        "type": col.inferred_type,
                        "dtype": col.dtype,
                        "null_percentage": col.null_percentage,
                        "unique_count": col.unique_count,
                        "issues": col.issues
                    }
                    for col in profile.column_profiles
                ]
            },
            "cleaning": {
                "rows_before": cleaning.rows_before,
                "rows_after": cleaning.rows_after,
                "rows_removed": cleaning.rows_removed,
                "cells_modified": cleaning.cells_modified,
                "operations": cleaning.operations_performed,
                "columns_modified": cleaning.columns_modified
            },
            "validation": {
                "passed": validation.passed,
                "total_issues": validation.total_issues,
                "errors": [
                    {"column": i.column, "message": i.message}
                    for i in validation.errors
                ],
                "warnings": [
                    {"column": i.column, "message": i.message}
                    for i in validation.warnings
                ]
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"JSON report exported to {output_path}")