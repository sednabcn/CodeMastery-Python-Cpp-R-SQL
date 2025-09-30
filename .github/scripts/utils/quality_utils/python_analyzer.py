#!/usr/bin/env python3
"""
Python Quality Analyzer - Single File Version
Analyzes individual Python files for quality and best practices.
Compatible with CI/CD workflows that process files one at a time.
"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List
import re


class PythonFileAnalyzer:
    """Analyzes a single Python file for quality metrics."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filename = self.filepath.name
        self.score = 100
        self.issues = []
        self.warnings = []
        self.info = []
        
    def analyze(self) -> Dict:
        """Run all analysis checks on the Python file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Parse AST
            try:
                tree = ast.parse(content, filename=str(self.filepath))
            except SyntaxError as e:
                return {
                    'error': f'Syntax error: {str(e)}',
                    'filepath': str(self.filepath),
                    'score': 0
                }
            
            # Run all checks
            self._check_complexity(tree)
            self._check_code_metrics(lines, tree)
            self._check_pep8_style(lines, tree)
            self._check_best_practices(tree, content)
            self._check_performance(tree, content)
            self._check_security(content, lines)
            
            return self._generate_report()
            
        except Exception as e:
            return {
                'error': str(e),
                'filepath': str(self.filepath),
                'score': 0
            }
    
    def _check_complexity(self, tree: ast.AST):
        """Analyze cyclomatic complexity."""
        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)
        complexity_data = analyzer.get_complexity()
        
        avg_complexity = complexity_data['total_complexity'] / max(len(complexity_data['functions']), 1)
        
        if avg_complexity > 15:
            self.score -= 25
            self.issues.append({
                'type': 'HIGH_COMPLEXITY',
                'severity': 'high',
                'message': f'Average complexity {avg_complexity:.1f} is very high (>15)',
                'penalty': -25,
                'suggestion': 'Break down complex functions into smaller ones'
            })
        elif avg_complexity > 10:
            self.score -= 15
            self.warnings.append({
                'type': 'MODERATE_COMPLEXITY',
                'severity': 'medium',
                'message': f'Average complexity {avg_complexity:.1f} is high (>10)',
                'penalty': -15,
                'suggestion': 'Consider refactoring complex functions'
            })
        elif avg_complexity > 5:
            self.score -= 5
            self.info.append({
                'type': 'MILD_COMPLEXITY',
                'severity': 'low',
                'message': f'Average complexity {avg_complexity:.1f} is above ideal (<5)',
                'penalty': -5
            })
        
        # Check for individual highly complex functions
        for func in complexity_data['functions']:
            if func['complexity'] > 20:
                self.issues.append({
                    'type': 'COMPLEX_FUNCTION',
                    'severity': 'high',
                    'line': func['line'],
                    'message': f"Function '{func['name']}' has complexity {func['complexity']} (>20)",
                    'suggestion': 'Break this function into smaller functions'
                })
    
    def _check_code_metrics(self, lines: List[str], tree: ast.AST):
        """Check documentation and comment ratios."""
        total_lines = len(lines)
        docstring_lines = self._count_docstrings(tree)
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        blank_lines = sum(1 for line in lines if not line.strip())
        code_lines = total_lines - comment_lines - blank_lines - docstring_lines
        
        if total_lines > 0:
            docstring_ratio = docstring_lines / total_lines
            comment_ratio = comment_lines / total_lines
            
            if docstring_ratio < 0.1:
                self.score -= 20
                self.issues.append({
                    'type': 'LOW_DOCUMENTATION',
                    'severity': 'high',
                    'message': f'Docstring ratio {docstring_ratio:.1%} is very low (<10%)',
                    'penalty': -20,
                    'suggestion': 'Add docstrings to functions and classes'
                })
            elif docstring_ratio < 0.2:
                self.score -= 10
                self.warnings.append({
                    'type': 'MODERATE_DOCUMENTATION',
                    'severity': 'medium',
                    'message': f'Docstring ratio {docstring_ratio:.1%} could be improved',
                    'penalty': -10
                })
            
            if comment_ratio < 0.05:
                self.score -= 10
                self.warnings.append({
                    'type': 'LOW_COMMENTS',
                    'severity': 'medium',
                    'message': f'Comment ratio {comment_ratio:.1%} is very low (<5%)',
                    'penalty': -10,
                    'suggestion': 'Add comments to explain complex logic'
                })
    
    def _count_docstrings(self, tree: ast.AST) -> int:
        """Count docstring lines in the AST."""
        docstring_count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstring_count += len(docstring.split('\n'))
        return docstring_count
    
    def _check_pep8_style(self, lines: List[str], tree: ast.AST):
        """Check PEP 8 style compliance."""
        # Line length
        long_lines = [(i+1, len(line.rstrip())) for i, line in enumerate(lines) if len(line.rstrip()) > 79]
        if long_lines:
            penalty = min(len(long_lines) * 2, 20)
            self.score -= penalty
            self.warnings.append({
                'type': 'LONG_LINES',
                'severity': 'medium',
                'message': f'{len(long_lines)} lines exceed 79 characters',
                'penalty': -penalty,
                'examples': [f'Line {line}: {length} chars' for line, length in long_lines[:3]]
            })
        
        # Naming conventions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
                    self.info.append({
                        'type': 'NAMING_CONVENTION',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': f"Function '{node.name}' should use snake_case"
                    })
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.info.append({
                        'type': 'NAMING_CONVENTION',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': f"Class '{node.name}' should use PascalCase"
                    })
    
    def _check_best_practices(self, tree: ast.AST, content: str):
        """Check Python best practices."""
        # Bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                self.score -= 8
                self.warnings.append({
                    'type': 'BARE_EXCEPT',
                    'severity': 'medium',
                    'line': node.lineno,
                    'message': 'Bare except clause catches all exceptions',
                    'penalty': -8,
                    'suggestion': 'Specify exception type(s) to catch'
                })
        
        # Mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        self.score -= 15
                        self.issues.append({
                            'type': 'MUTABLE_DEFAULT',
                            'severity': 'high',
                            'line': node.lineno,
                            'message': f"Mutable default argument in '{node.name}'",
                            'penalty': -15,
                            'suggestion': 'Use None as default and initialize inside function'
                        })
        
        # Global variables (non-constants)
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                for name in node.names:
                    if not name.isupper():
                        self.score -= 8
                        self.warnings.append({
                            'type': 'GLOBAL_VARIABLE',
                            'severity': 'medium',
                            'line': node.lineno,
                            'message': f"Global variable '{name}' (avoid if possible)",
                            'penalty': -8
                        })
        
        # Missing docstrings in public functions/classes
        missing_docstrings = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    missing_docstrings += 1
                    self.info.append({
                        'type': 'MISSING_DOCSTRING',
                        'severity': 'low',
                        'line': node.lineno,
                        'message': f"Missing docstring in '{node.name}'"
                    })
        
        if missing_docstrings > 0:
            penalty = min(missing_docstrings * 2, 15)
            self.score -= penalty
        
        # Wildcard imports
        if re.search(r'from .* import \*', content):
            self.score -= 10
            self.warnings.append({
                'type': 'WILDCARD_IMPORT',
                'severity': 'medium',
                'message': 'Wildcard import found (from module import *)',
                'penalty': -10,
                'suggestion': 'Import specific names instead'
            })
    
    def _check_performance(self, tree: ast.AST, content: str):
        """Check for performance issues."""
        # String concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        self.score -= 20
                        self.issues.append({
                            'type': 'STRING_CONCAT_LOOP',
                            'severity': 'high',
                            'line': child.lineno,
                            'message': 'String concatenation in loop (slow)',
                            'penalty': -20,
                            'suggestion': 'Use join() or list accumulation instead'
                        })
        
        # Inefficient membership testing
        if re.search(r'\bin\s+\[', content):
            self.score -= 10
            self.warnings.append({
                'type': 'LIST_MEMBERSHIP',
                'severity': 'medium',
                'message': 'Membership test on list (O(n) complexity)',
                'penalty': -10,
                'suggestion': 'Use set for membership testing'
            })
    
    def _check_security(self, content: str, lines: List[str]):
        """Check for security issues."""
        # eval() usage
        if 'eval(' in content:
            self.score -= 25
            self.issues.append({
                'type': 'EVAL_USAGE',
                'severity': 'critical',
                'message': 'Use of eval() function (major security risk)',
                'penalty': -25,
                'suggestion': 'Use ast.literal_eval() or safer alternatives'
            })
        
        # exec() usage
        if 'exec(' in content:
            self.score -= 25
            self.issues.append({
                'type': 'EXEC_USAGE',
                'severity': 'critical',
                'message': 'Use of exec() function (major security risk)',
                'penalty': -25,
                'suggestion': 'Avoid exec() or use safer alternatives'
            })
        
        # shell=True in subprocess
        if re.search(r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', content):
            self.score -= 15
            self.issues.append({
                'type': 'SHELL_INJECTION',
                'severity': 'high',
                'message': 'subprocess with shell=True (command injection risk)',
                'penalty': -15,
                'suggestion': 'Avoid shell=True or sanitize inputs'
            })
        
        # Hardcoded secrets
        for i, line in enumerate(lines, 1):
            if re.search(r'(password|secret|key|token|api_key)\s*=\s*["\'][^"\'{}$]+["\']', line, re.IGNORECASE):
                self.score -= 15
                self.issues.append({
                    'type': 'HARDCODED_SECRET',
                    'severity': 'high',
                    'line': i,
                    'message': 'Potential hardcoded secret detected',
                    'penalty': -15,
                    'suggestion': 'Use environment variables or secret management'
                })
        
        # SQL injection risk
        if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*%', content, re.IGNORECASE):
            self.score -= 20
            self.issues.append({
                'type': 'SQL_INJECTION',
                'severity': 'high',
                'message': 'Potential SQL injection (string formatting)',
                'penalty': -20,
                'suggestion': 'Use parameterized queries'
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


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""
    
    def __init__(self):
        self.complexity = 1
        self.functions = []
        self.current_function = None
        self.function_complexity = 1
    
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.function_complexity = 1
        self.generic_visit(node)
        self.functions.append({
            'name': node.name,
            'complexity': self.function_complexity,
            'line': node.lineno
        })
        self.current_function = None
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
    
    def _increment_complexity(self):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
    
    def visit_If(self, node):
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_For(self, node):
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_While(self, node):
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_With(self, node):
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        if isinstance(node.op, (ast.And, ast.Or)):
            increment = len(node.values) - 1
            self.complexity += increment
            if self.current_function:
                self.function_complexity += increment
        self.generic_visit(node)
    
    def get_complexity(self):
        return {
            'total_complexity': self.complexity,
            'functions': self.functions
        }


def format_text_report(report: Dict) -> str:
    """Format the report as human-readable text."""
    output = []
    output.append("=" * 70)
    output.append("PYTHON QUALITY ANALYSIS REPORT")
    output.append("=" * 70)
    output.append(f"File: {report['filename']}")
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
        output.append("\n🔴 ISSUES:")
        for issue in report['issues']:
            output.append(f"\n  [{issue['severity'].upper()}] {issue['type']}")
            if 'line' in issue:
                output.append(f"  Line: {issue['line']}")
            output.append(f"  Problem: {issue['message']}")
            if 'penalty' in issue:
                output.append(f"  Penalty: {issue['penalty']} points")
            if 'suggestion' in issue:
                output.append(f"  💡 {issue['suggestion']}")
    
    if report['warnings']:
        output.append("\n⚠️  WARNINGS:")
        for warning in report['warnings']:
            output.append(f"\n  [{warning.get('severity', 'medium').upper()}] {warning['type']}")
            if 'line' in warning:
                output.append(f"  Line: {warning['line']}")
            output.append(f"  Problem: {warning['message']}")
            if 'penalty' in warning:
                output.append(f"  Penalty: {warning['penalty']} points")
            if 'suggestion' in warning:
                output.append(f"  💡 {warning['suggestion']}")
    
    if not report['issues'] and not report['warnings']:
        output.append("\n✅ No critical issues found! Good Python quality!")
    
    output.append("\n" + "=" * 70)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Analyze Python file quality')
    parser.add_argument('filepath', help='Path to Python file to analyze')
    parser.add_argument('--output-json', help='Output JSON report to file')
    parser.add_argument('--output-text', help='Output text report to file')
    
    args = parser.parse_args()
    
    if not Path(args.filepath).exists():
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    analyzer = PythonFileAnalyzer(args.filepath)
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
