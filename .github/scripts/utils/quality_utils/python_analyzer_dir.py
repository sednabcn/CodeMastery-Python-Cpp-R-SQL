"""Analyze Python code quality and generate comprehensive metrics."""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
import subprocess


class PythonAnalyzer:
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.metrics = {}
        self.python_files = list(self.source_dir.rglob("*.py"))
    
    def analyze_complexity(self) -> Dict:
        """Analyze cyclomatic complexity of Python code using AST."""
        complexity_scores = []
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                analyzer = ComplexityAnalyzer()
                analyzer.visit(tree)
                
                file_complexity = analyzer.get_complexity()
                complexity_scores.append({
                    'file': str(py_file.relative_to(self.source_dir)),
                    'complexity': file_complexity['total_complexity'],
                    'functions': len(file_complexity['functions']),
                    'classes': len(file_complexity['classes']),
                    'max_function_complexity': max([f['complexity'] for f in file_complexity['functions']], default=0),
                    'function_details': file_complexity['functions'][:5]  # Top 5 most complex functions
                })
                
            except (SyntaxError, UnicodeDecodeError) as e:
                complexity_scores.append({
                    'file': str(py_file.relative_to(self.source_dir)),
                    'error': str(e),
                    'complexity': 0,
                    'functions': 0,
                    'classes': 0
                })
        
        valid_scores = [f for f in complexity_scores if 'error' not in f]
        avg_complexity = sum(f['complexity'] for f in valid_scores) / len(valid_scores) if valid_scores else 0
        
        return {
            'files': complexity_scores,
            'average_complexity': avg_complexity,
            'total_functions': sum(f['functions'] for f in valid_scores),
            'total_classes': sum(f['classes'] for f in valid_scores),
            'high_complexity_files': [f for f in valid_scores if f['complexity'] > 20]
        }
    
    def analyze_code_metrics(self) -> Dict:
        """Calculate lines of code, imports, docstrings, etc."""
        total_loc = 0
        total_comments = 0
        total_blank = 0
        total_docstrings = 0
        total_imports = 0
        file_count = 0
        
        for py_file in self.python_files:
            file_count += 1
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    content = ''.join(lines)
                
                # Parse AST for more accurate metrics
                tree = ast.parse(content)
                
                loc, comments, blank, docstrings, imports = self._count_lines(lines, tree)
                
                total_loc += loc
                total_comments += comments
                total_blank += blank
                total_docstrings += docstrings
                total_imports += imports
                
            except (SyntaxError, UnicodeDecodeError):
                file_count -= 1  # Don't count unparseable files
                continue
        
        total_lines = total_loc + total_comments + total_blank
        
        return {
            'total_files': file_count,
            'total_lines': total_lines,
            'lines_of_code': total_loc,
            'comment_lines': total_comments,
            'blank_lines': total_blank,
            'docstring_lines': total_docstrings,
            'import_statements': total_imports,
            'comment_ratio': total_comments / total_lines if total_lines > 0 else 0,
            'docstring_ratio': total_docstrings / total_lines if total_lines > 0 else 0,
            'avg_loc_per_file': total_loc / file_count if file_count > 0 else 0
        }
    
    def _count_lines(self, lines: List[str], tree: ast.AST) -> tuple:
        """Count different types of lines using both text analysis and AST."""
        loc = 0
        comments = 0
        blank = 0
        docstrings = 0
        imports = 0
        
        in_multiline_string = False
        quote_type = None
        
        # Get docstring line numbers from AST
        docstring_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (ast.get_docstring(node) and hasattr(node, 'body') and 
                    node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant)):
                    start_line = node.body[0].lineno
                    end_line = getattr(node.body[0], 'end_lineno', start_line)
                    if end_line:
                        docstring_lines.update(range(start_line, end_line + 1))
        
        # Count imports from AST
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
        
        # Count line types
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if not stripped:
                blank += 1
            elif i in docstring_lines:
                docstrings += 1
            elif stripped.startswith('#'):
                comments += 1
            elif '"""' in stripped or "'''" in stripped:
                if not in_multiline_string:
                    # Check if it's a single-line triple quote
                    triple_count = stripped.count('"""') + stripped.count("'''")
                    if triple_count >= 2:
                        # Single line docstring/comment
                        if i in docstring_lines:
                            docstrings += 1
                        else:
                            comments += 1
                    else:
                        in_multiline_string = True
                        quote_type = '"""' if '"""' in stripped else "'''"
                        if i in docstring_lines:
                            docstrings += 1
                        else:
                            comments += 1
                else:
                    if quote_type in stripped:
                        in_multiline_string = False
                    if i in docstring_lines:
                        docstrings += 1
                    else:
                        comments += 1
            elif in_multiline_string:
                if i in docstring_lines:
                    docstrings += 1
                else:
                    comments += 1
            else:
                loc += 1
        
        return loc, comments, blank, docstrings, imports
    
    def check_pep8_style(self) -> Dict:
        """Check PEP 8 style compliance."""
        style_issues = []
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    content = ''.join(lines)
                
                file_path = str(py_file.relative_to(self.source_dir))
                
                # Check line length (PEP 8: max 79 characters)
                for i, line in enumerate(lines, 1):
                    if len(line.rstrip()) > 79:
                        style_issues.append({
                            'file': file_path,
                            'line': i,
                            'issue': f'Line too long ({len(line.rstrip())} > 79 characters)',
                            'severity': 'warning'
                        })
                
                # Check for wildcard imports
                if re.search(r'from .* import \*', content):
                    style_issues.append({
                        'file': file_path,
                        'issue': 'Wildcard import found (avoid from module import *)',
                        'severity': 'warning'
                    })
                
                # Check for unused imports (basic check)
                imports = re.findall(r'^(?:from .+ )?import (.+)', content, re.MULTILINE)
                for import_line in imports:
                    imported_names = [name.strip() for name in import_line.split(',')]
                    for name in imported_names:
                        if ' as ' in name:
                            name = name.split(' as ')[1].strip()
                        name = name.split('.')[0]  # Handle module.submodule
                        if name and not re.search(rf'\b{re.escape(name)}\b', content.split('\n', 1)[1]):
                            style_issues.append({
                                'file': file_path,
                                'issue': f'Potentially unused import: {name}',
                                'severity': 'info'
                            })
                
                # Check function/class naming conventions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('_'):
                            style_issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'issue': f'Function name "{node.name}" should be snake_case',
                                'severity': 'info'
                            })
                    elif isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            style_issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'issue': f'Class name "{node.name}" should be PascalCase',
                                'severity': 'info'
                            })
                
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return {
            'style_issues': style_issues,
            'total_issues': len(style_issues),
            'warnings': len([i for i in style_issues if i['severity'] == 'warning']),
            'info': len([i for i in style_issues if i['severity'] == 'info'])
        }
    
    def check_best_practices(self) -> Dict:
        """Check Python best practices and potential issues."""
        issues = []
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_path = str(py_file.relative_to(self.source_dir))
                tree = ast.parse(content)
                
                # Check for bare except clauses
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        issues.append({
                            'file': file_path,
                            'line': node.lineno,
                            'issue': 'Bare except clause (specify exception type)',
                            'severity': 'warning'
                        })
                
                # Check for mutable default arguments
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for default in node.args.defaults:
                            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                                issues.append({
                                    'file': file_path,
                                    'line': node.lineno,
                                    'issue': f'Mutable default argument in function "{node.name}"',
                                    'severity': 'error'
                                })
                
                # Check for global variables (excluding constants)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Global):
                        for name in node.names:
                            if not name.isupper():
                                issues.append({
                                    'file': file_path,
                                    'line': node.lineno,
                                    'issue': f'Global variable "{name}" (consider alternatives)',
                                    'severity': 'warning'
                                })
                
                # Check for missing docstrings in public functions/classes
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if not node.name.startswith('_') and not ast.get_docstring(node):
                            issues.append({
                                'file': file_path,
                                'line': node.lineno,
                                'issue': f'Missing docstring in {type(node).__name__.lower().replace("def", "")} "{node.name}"',
                                'severity': 'info'
                            })
                
                # Check for TODO/FIXME comments
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(r'#.*\b(TODO|FIXME|XXX)\b', line, re.IGNORECASE):
                        issues.append({
                            'file': file_path,
                            'line': i,
                            'issue': 'TODO/FIXME comment found',
                            'severity': 'info'
                        })
                
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return {
            'issues': issues,
            'total_issues': len(issues),
            'errors': len([i for i in issues if i['severity'] == 'error']),
            'warnings': len([i for i in issues if i['severity'] == 'warning']),
            'info': len([i for i in issues if i['severity'] == 'info'])
        }
    
    def analyze_performance_patterns(self) -> Dict:
        """Check for common performance issues in Python."""
        performance_issues = []
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_path = str(py_file.relative_to(self.source_dir))
                tree = ast.parse(content)
                
                # Check for string concatenation in loops
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        for child in ast.walk(node):
                            if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                                if isinstance(child.target, ast.Name):
                                    performance_issues.append({
                                        'file': file_path,
                                        'line': child.lineno,
                                        'issue': 'String concatenation in loop (consider join() or f-strings)',
                                        'impact': 'high'
                                    })
                
                # Check for inefficient list operations
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Check for list.append() in loops when list comprehension could be used
                    if re.search(r'for .+ in .+:\s*\n\s*\w+\.append\(', '\n'.join(lines[max(0, i-2):i+2])):
                        performance_issues.append({
                            'file': file_path,
                            'line': i,
                            'issue': 'Consider using list comprehension instead of append in loop',
                            'impact': 'medium'
                        })
                
                # Check for repeated computation
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        # Look for function calls that could be moved outside the loop
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                                if isinstance(child.func.attr, str) and child.func.attr in ['len', 'max', 'min']:
                                    performance_issues.append({
                                        'file': file_path,
                                        'line': getattr(child, 'lineno', 0),
                                        'issue': f'Repeated {child.func.attr}() call in loop (consider caching)',
                                        'impact': 'medium'
                                    })
                
                # Check for inefficient membership testing
                if re.search(r'\bin\s+\[.*\]', content):
                    performance_issues.append({
                        'file': file_path,
                        'issue': 'Membership test on list (consider using set)',
                        'impact': 'medium'
                    })
                
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return {
            'performance_issues': performance_issues,
            'total_issues': len(performance_issues),
            'high_impact': len([i for i in performance_issues if i['impact'] == 'high']),
            'medium_impact': len([i for i in performance_issues if i['impact'] == 'medium']),
            'low_impact': len([i for i in performance_issues if i['impact'] == 'low'])
        }
    
    def analyze_dependencies(self) -> Dict:
        """Analyze import dependencies and detect potential issues."""
        imports = {}
        stdlib_imports = set()
        third_party_imports = set()
        local_imports = set()
        circular_dependencies = []
        
        # Common Python standard library modules
        stdlib_modules = {
            'os', 'sys', 'json', 're', 'math', 'random', 'datetime', 'time',
            'pathlib', 'collections', 'itertools', 'functools', 'typing',
            'unittest', 'logging', 'argparse', 'subprocess', 'threading',
            'multiprocessing', 'asyncio', 'ast', 'inspect', 'pickle', 'csv'
        }
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                file_path = str(py_file.relative_to(self.source_dir))
                file_imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split('.')[0]
                            file_imports.append(module)
                            
                            if module in stdlib_modules:
                                stdlib_imports.add(module)
                            elif '.' in alias.name or module.startswith('.'):
                                local_imports.add(module)
                            else:
                                third_party_imports.add(module)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split('.')[0]
                            file_imports.append(module)
                            
                            if module in stdlib_modules:
                                stdlib_imports.add(module)
                            elif node.level > 0 or module.startswith('.'):
                                local_imports.add(module)
                            else:
                                third_party_imports.add(module)
                
                imports[file_path] = list(set(file_imports))
                
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return {
            'file_imports': imports,
            'stdlib_imports': sorted(list(stdlib_imports)),
            'third_party_imports': sorted(list(third_party_imports)),
            'local_imports': sorted(list(local_imports)),
            'total_stdlib': len(stdlib_imports),
            'total_third_party': len(third_party_imports),
            'total_local': len(local_imports),
            'circular_dependencies': circular_dependencies
        }
    
    def analyze_security_issues(self) -> Dict:
        """Check for potential security issues."""
        security_issues = []
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_path = str(py_file.relative_to(self.source_dir))
                
                # Check for eval() usage
                if 'eval(' in content:
                    security_issues.append({
                        'file': file_path,
                        'issue': 'Use of eval() function (security risk)',
                        'severity': 'high'
                    })
                
                # Check for exec() usage
                if 'exec(' in content:
                    security_issues.append({
                        'file': file_path,
                        'issue': 'Use of exec() function (security risk)',
                        'severity': 'high'
                    })
                
                # Check for shell=True in subprocess
                if re.search(r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', content):
                    security_issues.append({
                        'file': file_path,
                        'issue': 'subprocess with shell=True (command injection risk)',
                        'severity': 'medium'
                    })
                
                # Check for hardcoded passwords/secrets
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(r'(password|secret|key|token)\s*=\s*["\'](?!.*\{|\$)', line, re.IGNORECASE):
                        security_issues.append({
                            'file': file_path,
                            'line': i,
                            'issue': 'Potential hardcoded secret',
                            'severity': 'medium'
                        })
                
                # Check for SQL string formatting
                if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*%.*', content, re.IGNORECASE):
                    security_issues.append({
                        'file': file_path,
                        'issue': 'Potential SQL injection vulnerability (use parameterized queries)',
                        'severity': 'high'
                    })
                
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return {
            'security_issues': security_issues,
            'total_issues': len(security_issues),
            'high_severity': len([i for i in security_issues if i['severity'] == 'high']),
            'medium_severity': len([i for i in security_issues if i['severity'] == 'medium']),
            'low_severity': len([i for i in security_issues if i['severity'] == 'low'])
        }
    
    def calculate_quality_score(self, complexity, metrics, style, best_practices, performance, security) -> Dict:
        """Calculate an overall quality score (0-100)."""
        score = 100
        
        # Deduct points for high complexity
        if complexity['average_complexity'] > 15:
            score -= 25
        elif complexity['average_complexity'] > 10:
            score -= 15
        elif complexity['average_complexity'] > 5:
            score -= 5
        
        # Deduct points for low documentation
        if metrics['docstring_ratio'] < 0.1:
            score -= 20
        elif metrics['docstring_ratio'] < 0.2:
            score -= 10
        
        if metrics['comment_ratio'] < 0.05:
            score -= 10
        
        # Deduct points for style issues
        score -= min(style['warnings'] * 2, 20)
        score -= min(style['info'] * 1, 10)
        
        # Deduct points for best practice violations
        score -= best_practices['errors'] * 15
        score -= best_practices['warnings'] * 8
        score -= best_practices['info'] * 2
        
        # Deduct points for performance issues
        score -= performance['high_impact'] * 20
        score -= performance['medium_impact'] * 10
        score -= performance['low_impact'] * 5
        
        # Deduct points for security issues
        score -= security['high_severity'] * 25
        score -= security['medium_severity'] * 15
        score -= security['low_severity'] * 5
        
        score = max(0, score)  # Ensure score doesn't go below 0
        
        # Determine grade
        if score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'
        elif score >= 70:
            grade = 'C'
        elif score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'score': score,
            'grade': grade,
            'max_score': 100
        }
    
    def generate_report(self) -> Dict:
        """Generate complete analysis report."""
        if not self.python_files:
            return {
                'error': 'No Python files found in the specified directory',
                'source_directory': str(self.source_dir)
            }
        
        print("Analyzing complexity...")
        complexity = self.analyze_complexity()
        
        print("Analyzing code metrics...")
        metrics = self.analyze_code_metrics()
        
        print("Checking PEP 8 style...")
        style = self.check_pep8_style()
        
        print("Checking best practices...")
        best_practices = self.check_best_practices()
        
        print("Analyzing performance patterns...")
        performance = self.analyze_performance_patterns()
        
        print("Analyzing dependencies...")
        dependencies = self.analyze_dependencies()
        
        print("Checking security issues...")
        security = self.analyze_security_issues()
        
        # Calculate overall quality score
        quality_score = self.calculate_quality_score(
            complexity, metrics, style, best_practices, performance, security
        )
        
        return {
            'source_directory': str(self.source_dir),
            'complexity_analysis': complexity,
            'code_metrics': metrics,
            'pep8_style': style,
            'best_practices': best_practices,
            'performance_analysis': performance,
            'dependencies': dependencies,
            'security_analysis': security,
            'quality_score': quality_score
        }


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.functions = []
        self.classes = []
        self.current_function = None
        self.current_class = None
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
    
    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.classes.append(node.name)
        self.generic_visit(node)
        self.current_class = None
    
    def visit_If(self, node):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
        self.generic_visit(node)
    
    def visit_Assert(self, node):
        self.complexity += 1
        if self.current_function:
            self.function_complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        if isinstance(node.op, (ast.And, ast.Or)):
            self.complexity += len(node.values) - 1
            if self.current_function:
                self.function_complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def get_complexity(self):
        return {
            'total_complexity': self.complexity,
            'functions': sorted(self.functions, key=lambda x: x['complexity'], reverse=True),
            'classes': self.classes
        }


def main():
    parser = argparse.ArgumentParser(description='Analyze Python code quality and generate metrics')
    parser.add_argument('source_dir', help='Directory containing Python source files')
    parser.add_argument('-o', '--output', help='Output file for JSON report (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--include-tests', action='store_true', help='Include test files in analysis')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"Error: Source directory '{args.source_dir}' does not exist")
        return 1
    
    analyzer = PythonAnalyzer(args.source_dir)
    
    # Filter out test files if not explicitly included
    if not args.include_tests:
        analyzer.python_files = [
            f for f in analyzer.python_files 
            if not any(part.startswith('test_') or part == 'tests' for part in f.parts)
        ]
    
    try:
        report = analyzer.generate_report()
        
        if 'error' in report:
            print(f"Error: {report['error']}")
            return 1
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            if args.verbose:
                print(json.dumps(report, indent=2))
            else:
                # Print summary
                print(f"\n=== Python Code Quality Report ===")
                print(f"Source Directory: {report['source_directory']}")
                print(f"Quality Score: {report['quality_score']['score']}/100 (Grade: {report['quality_score']['grade']})")
                
                print(f"\nCode Metrics:")
                print(f"  Files: {report['code_metrics']['total_files']}")
                print(f"  Lines of Code: {report['code_metrics']['lines_of_code']}")
                print(f"  Comment Ratio: {report['code_metrics']['comment_ratio']:.2%}")
                print(f"  Docstring Ratio: {report['code_metrics']['docstring_ratio']:.2%}")
                print(f"  Avg Complexity: {report['complexity_analysis']['average_complexity']:.2f}")
                print(f"  Functions: {report['complexity_analysis']['total_functions']}")
                print(f"  Classes: {report['complexity_analysis']['total_classes']}")
                
                print(f"\nIssues:")
                print(f"  Style Warnings: {report['pep8_style']['warnings']}")
                print(f"  Best Practice Errors: {report['best_practices']['errors']}")
                print(f"  Best Practice Warnings: {report['best_practices']['warnings']}")
                print(f"  Performance Issues: {report['performance_analysis']['total_issues']}")
                print(f"  Security Issues: {report['security_analysis']['total_issues']}")
                
                print(f"\nDependencies:")
                print(f"  Standard Library: {report['dependencies']['total_stdlib']}")
                print(f"  Third Party: {report['dependencies']['total_third_party']}")
                print(f"  Local: {report['dependencies']['total_local']}")
                
                # Show top issues if any
                if report['complexity_analysis']['high_complexity_files']:
                    print(f"\nHigh Complexity Files:")
                    for file_info in report['complexity_analysis']['high_complexity_files'][:3]:
                        print(f"  {file_info['file']}: {file_info['complexity']:.1f}")
                
                if report['security_analysis']['high_severity'] > 0:
                    print(f"\n⚠️  High severity security issues found!")
                
                if report['performance_analysis']['high_impact'] > 0:
                    print(f"⚠️  High impact performance issues found!")
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
