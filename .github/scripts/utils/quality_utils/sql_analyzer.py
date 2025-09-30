#!/usr/bin/env python3
"""
SQL Quality Analyzer
Analyzes SQL query files for best practices and quality issues.
Based on the SQL best practices guide.
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import sqlparse


class SQLQualityAnalyzer:
    """Analyzes SQL queries for quality and best practices."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = Path(filepath).name
        self.score = 100
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
    def analyze(self) -> Dict:
        """Run all analysis checks on the SQL file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse SQL statements
            statements = sqlparse.parse(content)
            
            for idx, statement in enumerate(statements):
                if statement.get_type() != 'UNKNOWN':
                    self._analyze_statement(statement, idx + 1)
            
            return self._generate_report()
            
        except Exception as e:
            return {
                'error': str(e),
                'filepath': self.filepath,
                'score': 0
            }
    
    def _analyze_statement(self, statement, statement_num: int):
        """Analyze a single SQL statement."""
        sql = str(statement).strip()
        sql_upper = sql.upper()
        
        # Skip comments and empty statements
        if not sql or sql.startswith('--') or statement.get_type() == 'UNKNOWN':
            return
        
        context = f"Statement #{statement_num}"
        
        # Check 1: SELECT * usage
        self._check_select_star(sql_upper, context)
        
        # Check 2: Missing WHERE clause
        self._check_missing_where(sql_upper, context)
        
        # Check 3: LIKE patterns with leading wildcards
        self._check_like_patterns(sql_upper, context)
        
        # Check 4: Functions on columns in WHERE clause
        self._check_functions_on_columns(sql_upper, context)
        
        # Check 5: Too many JOINs
        self._check_join_count(sql_upper, context)
        
        # Check 6: NOT IN with subquery
        self._check_not_in_subquery(sql_upper, context)
        
        # Check 7: Missing LIMIT clause
        self._check_missing_limit(sql_upper, context)
        
        # Check 8: Multiple OR conditions
        self._check_multiple_or(sql_upper, context)
        
        # Check 9: DISTINCT with SELECT *
        self._check_distinct_select_star(sql_upper, context)
        
        # Check 10: UNION instead of UNION ALL
        self._check_union_vs_union_all(sql_upper, context)
        
        # Check 11: ORDER BY without LIMIT
        self._check_order_by_without_limit(sql_upper, context)
        
        # Check 12: Trailing wildcard in LIKE
        self._check_trailing_wildcard(sql_upper, context)
    
    def _check_select_star(self, sql: str, context: str):
        """Check for SELECT * usage."""
        if re.search(r'SELECT\s+\*', sql):
            self.score -= 10
            self.issues.append({
                'type': 'SELECT_STAR',
                'severity': 'high',
                'context': context,
                'message': 'SELECT * returns all columns (unnecessary data)',
                'penalty': -10,
                'suggestion': 'Use explicit column names instead'
            })
    
    def _check_missing_where(self, sql: str, context: str):
        """Check for missing WHERE clause in SELECT/UPDATE/DELETE."""
        if re.search(r'(SELECT|UPDATE|DELETE)\s', sql):
            if 'WHERE' not in sql:
                # Exception: Allow if it has LIMIT or if it's a simple lookup
                if 'LIMIT' not in sql and 'JOIN' not in sql:
                    self.score -= 20
                    self.issues.append({
                        'type': 'MISSING_WHERE',
                        'severity': 'critical',
                        'context': context,
                        'message': 'Query without WHERE clause may return all rows',
                        'penalty': -20,
                        'suggestion': 'Add WHERE clause to filter results'
                    })
    
    def _check_like_patterns(self, sql: str, context: str):
        """Check for LIKE patterns with leading wildcards."""
        leading_wildcard = re.findall(r"LIKE\s+['\"]%[^'\"]+['\"]", sql)
        if leading_wildcard:
            self.score -= 15
            self.issues.append({
                'type': 'LEADING_WILDCARD',
                'severity': 'high',
                'context': context,
                'message': f'Leading wildcard in LIKE prevents index usage: {leading_wildcard[0]}',
                'penalty': -15,
                'suggestion': 'Use trailing wildcards (text%) or full-text search'
            })
    
    def _check_trailing_wildcard(self, sql: str, context: str):
        """Check for trailing wildcards (minor penalty)."""
        # Only trailing wildcard, not leading
        trailing_only = re.findall(r"LIKE\s+['\"]([^%][^'\"]*%)['\"]", sql)
        if trailing_only and not re.search(r"LIKE\s+['\"]%", sql):
            self.score -= 5
            self.warnings.append({
                'type': 'TRAILING_WILDCARD',
                'severity': 'low',
                'context': context,
                'message': f'Trailing wildcard may still scan many rows',
                'penalty': -5,
                'suggestion': 'Consider exact match if possible'
            })
    
    def _check_functions_on_columns(self, sql: str, context: str):
        """Check for functions applied to columns in WHERE clause."""
        # Common functions on columns in WHERE
        patterns = [
            r'WHERE\s+\w*\([^\)]*\.\w+\)',  # Function on column
            r'WHERE\s+(UPPER|LOWER|TRIM|SUBSTRING|DATE|YEAR|MONTH)\s*\(\w+\)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, sql):
                self.score -= 15
                self.issues.append({
                    'type': 'FUNCTION_ON_COLUMN',
                    'severity': 'high',
                    'context': context,
                    'message': 'Function on column in WHERE clause prevents index usage',
                    'penalty': -15,
                    'suggestion': 'Apply function to the comparison value instead, or use computed columns'
                })
                break
    
    def _check_join_count(self, sql: str, context: str):
        """Check for excessive JOINs."""
        join_count = len(re.findall(r'\bJOIN\b', sql))
        if join_count > 6:
            self.score -= 10
            self.issues.append({
                'type': 'TOO_MANY_JOINS',
                'severity': 'medium',
                'context': context,
                'message': f'Query has {join_count} JOINs (recommended: ≤6)',
                'penalty': -10,
                'suggestion': 'Consider breaking into multiple queries or using materialized views'
            })
    
    def _check_not_in_subquery(self, sql: str, context: str):
        """Check for NOT IN with subquery."""
        if re.search(r'NOT\s+IN\s*\(\s*SELECT', sql):
            self.score -= 10
            self.issues.append({
                'type': 'NOT_IN_SUBQUERY',
                'severity': 'medium',
                'context': context,
                'message': 'NOT IN with subquery is slow and has NULL issues',
                'penalty': -10,
                'suggestion': 'Use NOT EXISTS or LEFT JOIN with NULL check instead'
            })
    
    def _check_missing_limit(self, sql: str, context: str):
        """Check for missing LIMIT clause."""
        if 'SELECT' in sql and 'LIMIT' not in sql:
            # Don't penalize if it's a subquery or has TOP
            if 'TOP ' not in sql and not re.search(r'\)\s*$', sql.strip()):
                self.score -= 10
                self.warnings.append({
                    'type': 'MISSING_LIMIT',
                    'severity': 'medium',
                    'context': context,
                    'message': 'Query without LIMIT may return excessive rows',
                    'penalty': -10,
                    'suggestion': 'Add LIMIT clause to prevent large result sets'
                })
    
    def _check_multiple_or(self, sql: str, context: str):
        """Check for multiple OR conditions."""
        or_count = len(re.findall(r'\bOR\b', sql))
        if or_count > 3:
            self.score -= 10
            self.warnings.append({
                'type': 'MULTIPLE_OR',
                'severity': 'low',
                'context': context,
                'message': f'Query has {or_count} OR conditions',
                'penalty': -10,
                'suggestion': 'Consider using IN clause instead'
            })
    
    def _check_distinct_select_star(self, sql: str, context: str):
        """Check for DISTINCT with SELECT *."""
        if re.search(r'SELECT\s+DISTINCT\s+\*', sql):
            self.score -= 10
            self.issues.append({
                'type': 'DISTINCT_SELECT_STAR',
                'severity': 'medium',
                'context': context,
                'message': 'DISTINCT with SELECT * is expensive',
                'penalty': -10,
                'suggestion': 'Use DISTINCT only on specific columns or consider GROUP BY'
            })
    
    def _check_union_vs_union_all(self, sql: str, context: str):
        """Check for UNION instead of UNION ALL."""
        # Check if UNION is used but not UNION ALL
        if re.search(r'\bUNION\b(?!\s+ALL)', sql):
            self.score -= 5
            self.warnings.append({
                'type': 'UNION_WITHOUT_ALL',
                'severity': 'low',
                'context': context,
                'message': 'UNION adds DISTINCT operation overhead',
                'penalty': -5,
                'suggestion': 'Use UNION ALL if duplicates are acceptable'
            })
    
    def _check_order_by_without_limit(self, sql: str, context: str):
        """Check for ORDER BY without LIMIT."""
        if 'ORDER BY' in sql and 'LIMIT' not in sql:
            self.score -= 10
            self.warnings.append({
                'type': 'ORDER_BY_WITHOUT_LIMIT',
                'severity': 'medium',
                'context': context,
                'message': 'ORDER BY without LIMIT sorts entire result set',
                'penalty': -10,
                'suggestion': 'Add LIMIT clause to allow top-N optimization'
            })
    
    def _generate_report(self) -> Dict:
        """Generate the analysis report."""
        # Ensure score doesn't go below 0
        self.score = max(0, self.score)
        
        # Determine grade
        if self.score >= 90:
            grade = 'A'
        elif self.score >= 80:
            grade = 'B'
        elif self.score >= 70:
            grade = 'C'
        elif self.score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'filepath': self.filepath,
            'filename': self.filename,
            'overall_score': self.score,
            'grade': grade,
            'issues': self.issues,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'summary': {
                'critical_issues': len([i for i in self.issues if i.get('severity') == 'critical']),
                'high_issues': len([i for i in self.issues if i.get('severity') == 'high']),
                'medium_issues': len([i for i in self.issues if i.get('severity') == 'medium']),
                'warnings': len(self.warnings),
            }
        }


def format_text_report(report: Dict) -> str:
    """Format the report as human-readable text."""
    output = []
    output.append("=" * 70)
    output.append(f"SQL QUALITY ANALYSIS REPORT")
    output.append("=" * 70)
    output.append(f"File: {report['filename']}")
    output.append(f"Score: {report['overall_score']}/100 (Grade: {report['grade']})")
    output.append("-" * 70)
    
    summary = report['summary']
    output.append(f"Summary:")
    output.append(f"  Critical Issues: {summary['critical_issues']}")
    output.append(f"  High Issues: {summary['high_issues']}")
    output.append(f"  Medium Issues: {summary['medium_issues']}")
    output.append(f"  Warnings: {summary['warnings']}")
    output.append("-" * 70)
    
    if report['issues']:
        output.append("\n🔴 ISSUES:")
        for issue in report['issues']:
            output.append(f"\n  [{issue['severity'].upper()}] {issue['type']}")
            output.append(f"  Context: {issue['context']}")
            output.append(f"  Problem: {issue['message']}")
            output.append(f"  Penalty: {issue['penalty']} points")
            output.append(f"  💡 {issue['suggestion']}")
    
    if report['warnings']:
        output.append("\n⚠️  WARNINGS:")
        for warning in report['warnings']:
            output.append(f"\n  [{warning['severity'].upper()}] {warning['type']}")
            output.append(f"  Context: {warning['context']}")
            output.append(f"  Problem: {warning['message']}")
            output.append(f"  Penalty: {warning['penalty']} points")
            output.append(f"  💡 {warning['suggestion']}")
    
    if not report['issues'] and not report['warnings']:
        output.append("\n✅ No issues found! Excellent SQL quality!")
    
    output.append("\n" + "=" * 70)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Analyze SQL query quality')
    parser.add_argument('filepath', help='Path to SQL file to analyze')
    parser.add_argument('--output-json', help='Output JSON report to file')
    parser.add_argument('--output-text', help='Output text report to file')
    
    args = parser.parse_args()
    
    if not Path(args.filepath).exists():
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    analyzer = SQLQualityAnalyzer(args.filepath)
    report = analyzer.analyze()
    
    # Check for errors
    if 'error' in report:
        print(f"Error analyzing file: {report['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Output JSON report
    json_filename = args.output_json or f"{Path(args.filepath).stem}_quality_report.json"
    with open(json_filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"JSON report saved to: {json_filename}")
    
    # Output text report
    text_report = format_text_report(report)
    text_filename = args.output_text or f"{Path(args.filepath).stem}_quality_report.txt"
    with open(text_filename, 'w') as f:
        f.write(text_report)
    print(f"Text report saved to: {text_filename}")
    
    # Print to console
    print(text_report)
    
    # Exit with error code if score is too low
    if report['overall_score'] < 70:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
