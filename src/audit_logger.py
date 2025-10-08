"""
Audit logging system for compliance
Tracks all data transformations for regulatory requirements
"""
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class AuditLogEntry:
    """Single audit log entry"""
    timestamp: str
    file_id: str
    operation: str
    user_id: Optional[str]
    input_hash: str
    output_hash: str
    rows_before: int
    rows_after: int
    columns_modified: List[str]
    transformation_details: Dict[str, Any]
    compliance_flags: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """Audit logging system for compliance tracking"""
    
    def __init__(self, log_dir: str = "storage/audit_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_transformation(self,
                          file_id: str,
                          operation: str,
                          input_df,
                          output_df,
                          transformation_details: Dict[str, Any],
                          user_id: Optional[str] = None,
                          compliance_flags: Optional[List[str]] = None) -> AuditLogEntry:
        """
        Log a data transformation
        
        Args:
            file_id: Unique file identifier
            operation: Type of operation (clean, validate, etc.)
            input_df: Input DataFrame
            output_df: Output DataFrame
            transformation_details: Details of what changed
            user_id: User who performed the operation
            compliance_flags: Compliance-related flags (PII_DETECTED, etc.)
            
        Returns:
            AuditLogEntry
        """
        # Create audit entry
        entry = AuditLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            file_id=file_id,
            operation=operation,
            user_id=user_id or "system",
            input_hash=self._hash_dataframe(input_df),
            output_hash=self._hash_dataframe(output_df),
            rows_before=len(input_df),
            rows_after=len(output_df),
            columns_modified=transformation_details.get('columns_modified', []),
            transformation_details=transformation_details,
            compliance_flags=compliance_flags or []
        )
        
        # Write to file
        self._write_log(entry)
        
        return entry
    
    def get_audit_trail(self, file_id: str) -> List[AuditLogEntry]:
        """
        Get complete audit trail for a file
        
        Args:
            file_id: File identifier
            
        Returns:
            List of audit log entries
        """
        log_file = os.path.join(self.log_dir, f"{file_id}_audit.jsonl")
        
        if not os.path.exists(log_file):
            return []
        
        entries = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    entry_dict = json.loads(line)
                    entries.append(AuditLogEntry(**entry_dict))
        
        return entries
    
    def generate_compliance_report(self, file_id: str) -> Dict[str, Any]:
        """
        Generate compliance report for a file
        
        Args:
            file_id: File identifier
            
        Returns:
            Compliance report dictionary
        """
        trail = self.get_audit_trail(file_id)
        
        if not trail:
            return {"error": "No audit trail found"}
        
        # Analyze trail
        all_operations = [entry.operation for entry in trail]
        all_flags = []
        for entry in trail:
            all_flags.extend(entry.compliance_flags)
        
        total_rows_removed = sum(
            entry.rows_before - entry.rows_after 
            for entry in trail
        )
        
        # Get all modifications
        all_modifications = []
        for entry in trail:
            all_modifications.extend(entry.transformation_details.get('operations_performed', []))
        
        report = {
            "file_id": file_id,
            "report_generated_at": datetime.utcnow().isoformat(),
            "total_transformations": len(trail),
            "operations_performed": list(set(all_operations)),
            "compliance_flags": list(set(all_flags)),
            "data_lineage": {
                "original_rows": trail[0].rows_before if trail else 0,
                "final_rows": trail[-1].rows_after if trail else 0,
                "total_rows_removed": total_rows_removed,
                "columns_modified": list(set([
                    col for entry in trail 
                    for col in entry.columns_modified
                ]))
            },
            "all_modifications": all_modifications,
            "audit_trail": [entry.to_dict() for entry in trail],
            "compliance_status": self._assess_compliance(trail)
        }
        
        return report
    
    def export_compliance_report(self, file_id: str, format: str = 'json') -> str:
        """
        Export compliance report to file
        
        Args:
            file_id: File identifier
            format: Export format (json, pdf)
            
        Returns:
            Path to exported file
        """
        report = self.generate_compliance_report(file_id)
        
        output_dir = "storage/compliance_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        if format == 'json':
            output_path = os.path.join(output_dir, f"{file_id}_compliance_report.json")
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'html':
            output_path = os.path.join(output_dir, f"{file_id}_compliance_report.html")
            html = self._generate_html_report(report)
            with open(output_path, 'w') as f:
                f.write(html)
        
        return output_path
    
    def _hash_dataframe(self, df) -> str:
        """Generate hash of DataFrame for integrity verification"""
        # Create hash from shape and sample values
        hash_string = f"{df.shape}_{df.columns.tolist()}"
        
        # Add sample of data
        if len(df) > 0:
            hash_string += str(df.head(5).values.tolist())
        
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    def _write_log(self, entry: AuditLogEntry):
        """Write log entry to file (append-only)"""
        log_file = os.path.join(self.log_dir, f"{entry.file_id}_audit.jsonl")
        
        with open(log_file, 'a') as f:
            f.write(entry.to_json() + '\n')
    
    def _assess_compliance(self, trail: List[AuditLogEntry]) -> Dict[str, Any]:
        """Assess compliance status"""
        flags = []
        for entry in trail:
            flags.extend(entry.compliance_flags)
        
        has_pii = 'PII_DETECTED' in flags
        pii_masked = 'PII_MASKED' in flags
        
        status = {
            "gdpr_compliant": pii_masked if has_pii else True,
            "sox_compliant": len(trail) > 0,  # Has audit trail
            "audit_trail_complete": len(trail) > 0,
            "data_lineage_tracked": True,
            "pii_handled_correctly": pii_masked if has_pii else True
        }
        
        return status
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML compliance report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Report - {report['file_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
        .status {{ padding: 5px 10px; border-radius: 3px; }}
        .pass {{ background: #d4edda; color: #155724; }}
        .fail {{ background: #f8d7da; color: #721c24; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #f0f0f0; }}
    </style>
</head>
<body>
    <h1>Data Cleaning Compliance Report</h1>
    <div class="section">
        <h2>File Information</h2>
        <p><strong>File ID:</strong> {report['file_id']}</p>
        <p><strong>Report Generated:</strong> {report['report_generated_at']}</p>
        <p><strong>Total Transformations:</strong> {report['total_transformations']}</p>
    </div>
    
    <div class="section">
        <h2>Compliance Status</h2>
        <table>
            <tr>
                <th>Requirement</th>
                <th>Status</th>
            </tr>
            {"".join([
                f'<tr><td>{k.replace("_", " ").title()}</td><td class="status {"pass" if v else "fail"}">{" PASS" if v else "FAIL"}</td></tr>'
                for k, v in report['compliance_status'].items()
            ])}
        </table>
    </div>
    
    <div class="section">
        <h2>Data Lineage</h2>
        <p><strong>Original Rows:</strong> {report['data_lineage']['original_rows']}</p>
        <p><strong>Final Rows:</strong> {report['data_lineage']['final_rows']}</p>
        <p><strong>Rows Removed:</strong> {report['data_lineage']['total_rows_removed']}</p>
        <p><strong>Columns Modified:</strong> {len(report['data_lineage']['columns_modified'])}</p>
    </div>
    
    <div class="section">
        <h2>Modifications Performed</h2>
        <ul>
            {"".join([f"<li>{mod}</li>" for mod in report['all_modifications']])}
        </ul>
    </div>
</body>
</html>
"""
        return html
