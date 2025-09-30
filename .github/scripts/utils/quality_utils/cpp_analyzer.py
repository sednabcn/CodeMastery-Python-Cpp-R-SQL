#!/usr/bin/env python3
"""
C++ Quality Analyzer - Single File Version
Analyzes individual C++ files for quality and best practices.
Compatible with CI/CD workflows that process files one at a time.
"""

import argparse
import json
import sys
import re
from pathlib import Path
from typing import Dict, List


class CppFileAnalyzer:
    """Analyzes a single C++ file for quality metrics."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filename = self.filepath.name
        self.score = 100
        self.issues = []
        self.warnings = []
        self.info = []
        self.is_header = self.filepath.suffix in ['.h', '.hpp', '.hxx']
        
    def analyze(self) -> Dict:
        """Run all analysis checks on the C++ file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Run all checks
            self._check_complexity(content)
            self._check_code_metrics(lines)
            self._check_best_practices(content)
            self._check_performance(content)
            self._check_modern_cpp(content)
            self._check_memory_safety(content)
            
            return self._generate_report()
            
        except Exception as e:
            return {
                'error': str(e),
                'filepath': str(self.filepath),
                'score': 0
            }
    
    def _check_complexity(self, content: str):
        """Analyze cyclomatic complexity."""
        # Count decision points
        decision_points = (
            content.count('if') +
            content.count('for') +
            content.count('while') +
            content.count('case') +
            content.count('&&') +
            content.count('||') +
            content.count('?')
        )
        
        # Count functions
        function_matches = re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*(?:const\s*)?{', content)
        num_functions = len(function_matches)
        
        if num_functions > 0:
            avg_complexity = decision_points / num_functions
            
            if avg_complexity > 10:
                self.score -= 20
                self.issues.append({
                    'type': 'HIGH_COMPLEXITY',
                    'severity': 'high',
                    'message': f'Average complexity {avg_complexity:.1f} is very high (>10)',
                    'penalty': -20,
                    'suggestion': 'Break down complex functions into smaller ones'
                })
            elif avg_complexity > 5:
                self.score -= 10
                self.warnings.append({
                    'type': 'MODERATE_COMPLEXITY',
                    'severity': 'medium',
                    'message': f'Average complexity {avg_complexity:.1f} is above ideal (>5)',
                    'penalty': -10,
                    'suggestion': 'Consider refactoring complex functions'
                })
    
    def _check_code_metrics(self, lines: List[str]):
        """Check documentation and comment ratios."""
        total_lines = len(lines)
        comment_lines = 0
        blank_lines = 0
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('//'):
                comment_lines += 1
            elif '/*' in stripped and '*/' in stripped:
                comment_lines += 1
            elif '/*' in stripped:
                comment_lines += 1
                in_multiline_comment = True
            elif '*/' in stripped:
                comment_lines += 1
                in_multiline_comment = False
            elif in_multiline_comment:
                comment_lines += 1
        
        code_lines = total_lines - comment_lines - blank_lines
        
        if total_lines > 0:
            comment_ratio = comment_lines / total_lines
            
            if comment_ratio < 0.1:
                self.score -= 15
                self.warnings.append({
                    'type': 'LOW_COMMENTS',
                    'severity': 'medium',
                    'message': f'Comment ratio {comment_ratio:.1%} is very low (<10%)',
                    'penalty': -15,
                    'suggestion': 'Add comments to explain complex logic'
                })
            elif comment_ratio < 0.2:
                self.score -= 5
                self.info.append({
                    'type': 'MODERATE_COMMENTS',
                    'severity': 'low',
                    'message': f'Comment ratio {comment_ratio:.1%} could be improved'
                })
    
    def _check_best_practices(self, content: str):
        """Check C++ best practices."""
        # Raw pointers with new
        if re.search(r'\bnew\s+\w+', content):
            self.score -= 10
            self.warnings.append({
                'type': 'RAW_NEW',
                'severity': 'medium',
                'message': 'Using raw new operator',
                'penalty': -10,
                'suggestion': 'Prefer smart pointers (unique_ptr, shared_ptr)'
            })
        
        # Manual delete
        if re.search(r'\bdelete\b', content):
            self.score -= 10
            self.warnings.append({
                'type': 'MANUAL_DELETE',
                'severity': 'medium',
                'message': 'Manual delete found',
                'penalty': -10,
                'suggestion': 'Use RAII and smart pointers instead'
            })
        
        # C-style casts
        c_cast_matches = re.findall(r'\([a-zA-Z_]\w*\s*\*?\s*\)\s*[a-zA-Z_]', content)
        if c_cast_matches:
            self.score -= 8
            self.info.append({
                'type': 'C_STYLE_CAST',
                'severity': 'low',
                'message': f'C-style cast(s) found: {len(c_cast_matches)} occurrence(s)',
                'suggestion': 'Use static_cast, dynamic_cast, const_cast, or reinterpret_cast'
            })
        
        # using namespace std in headers
        if self.is_header and 'using namespace std' in content:
            self.score -= 20
            self.issues.append({
                'type': 'USING_NAMESPACE_HEADER',
                'severity': 'high',
                'message': 'using namespace std in header file',
                'penalty': -20,
                'suggestion': 'Never use "using namespace" in headers'
            })
        
        # Missing virtual destructor
        has_virtual = 'virtual' in content
        has_virtual_destructor = re.search(r'virtual\s+~\w+', content)
        class_definitions = re.findall(r'class\s+\w+', content)
        
        if has_virtual and not has_virtual_destructor and class_definitions:
            self.score -= 15
            self.warnings.append({
                'type': 'MISSING_VIRTUAL_DESTRUCTOR',
                'severity': 'high',
                'message': 'Class with virtual methods missing virtual destructor',
                'penalty': -15,
                'suggestion': 'Add virtual destructor to base classes with virtual methods'
            })
        
        # NULL instead of nullptr
        if re.search(r'\bNULL\b', content):
            self.score -= 5
            self.info.append({
                'type': 'NULL_MACRO',
                'severity': 'low',
                'message': 'Using NULL macro',
	        'suggestion': 'Consider using vector::at() for bounds checking'
            })
        
        # Uninitialized pointers
        pointer_declarations = re.findall(r'\b\w+\s*\*\s*\w+\s*;', content)
        if pointer_declarations:
            self.warnings.append({
                'type': 'POINTER_DECLARATION',
                'severity': 'medium',
                'message': f'{len(pointer_declarations)} pointer declaration(s) found',
                'suggestion': 'Initialize pointers (nullptr) or use smart pointers'
            })
    
    def _generate_report(self) -> Dict:
        """Generate the analysis report."""
        self.score = max(0, self.score)
        
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
            'filepath': str(self.filepath),
            'filename': self.filename,
            'file_type': 'header' if self.is_header else 'source',
            'overall_score': self.score,
            'grade': grade,
            'issues': self.issues,
            'warnings': self.warnings,
            'info': self.info,
            'summary': {
                'critical_issues': len([i for i in self.issues if i.get('severity') == 'critical']),
                'high_issues': len([i for i in self.issues if i.get('severity') == 'high']),
                'medium_issues': len([i for i in self.warnings if i.get('severity') == 'medium']),
                'low_issues': len(self.info),
            }
        }


def format_text_report(report: Dict) -> str:
    """Format the report as human-readable text."""
    output = []
    output.append("=" * 70)
    output.append("C++ QUALITY ANALYSIS REPORT")
    output.append("=" * 70)
    output.append(f"File: {report['filename']} ({report['file_type']})")
    output.append(f"Score: {report['overall_score']}/100 (Grade: {report['grade']})")
    output.append("-" * 70)
    
    summary = report['summary']
    output.append("Summary:")
    output.append(f"  Critical Issues: {summary['critical_issues']}")
    output.append(f"  High Issues: {summary['high_issues']}")
    output.append(f"  Medium Issues: {summary['medium_issues']}")
    output.append(f"  Low Issues: {summary['low_issues']}")
    output.append("-" * 70)
    
    if report['issues']:
        output.append("\nISSUES:")
        for issue in report['issues']:
            output.append(f"\n  [{issue['severity'].upper()}] {issue['type']}")
            if 'line' in issue:
                output.append(f"  Line: {issue['line']}")
            output.append(f"  Problem: {issue['message']}")
            if 'penalty' in issue:
                output.append(f"  Penalty: {issue['penalty']} points")
            if 'suggestion' in issue:
                output.append(f"  Suggestion: {issue['suggestion']}")
    
    if report['warnings']:
        output.append("\nWARNINGS:")
        for warning in report['warnings']:
            output.append(f"\n  [{warning.get('severity', 'medium').upper()}] {warning['type']}")
            if 'line' in warning:
                output.append(f"  Line: {warning['line']}")
            output.append(f"  Problem: {warning['message']}")
            if 'penalty' in warning:
                output.append(f"  Penalty: {warning['penalty']} points")
            if 'suggestion' in warning:
                output.append(f"  Suggestion: {warning['suggestion']}")
    
    if report['info']:
        output.append("\nINFO:")
        for info in report['info'][:5]:  # Show first 5 info items
            output.append(f"\n  {info['type']}")
            output.append(f"  {info['message']}")
            if 'suggestion' in info:
                output.append(f"  Suggestion: {info['suggestion']}")
    
    if not report['issues'] and not report['warnings']:
        output.append("\nNo critical issues found! Good C++ quality!")
    
    output.append("\n" + "=" * 70)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Analyze C++ file quality')
    parser.add_argument('filepath', help='Path to C++ file to analyze')
    parser.add_argument('--output-json', help='Output JSON report to file')
    parser.add_argument('--output-text', help='Output text report to file')
    
    args = parser.parse_args()
    
    if not Path(args.filepath).exists():
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    analyzer = CppFileAnalyzer(args.filepath)
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
          
