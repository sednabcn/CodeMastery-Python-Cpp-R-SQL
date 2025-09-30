"""Analyze C++ code quality and generate metrics."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List


class CppAnalyzer:
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.metrics = {}
    
    def analyze_complexity(self) -> Dict:
        """Analyze cyclomatic complexity of C++ code."""
        complexity_scores = []
        
        for cpp_file in self.source_dir.rglob("*.cpp"):
            with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
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
            functions = len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', content))
            
            avg_complexity = decision_points / max(functions, 1)
            complexity_scores.append({
                'file': str(cpp_file.relative_to(self.source_dir)),
                'complexity': avg_complexity,
                'functions': functions,
                'decision_points': decision_points
            })
        
        return {
            'files': complexity_scores,
            'average_complexity': sum(f['complexity'] for f in complexity_scores) / len(complexity_scores) if complexity_scores else 0
        }
    
    def analyze_code_metrics(self) -> Dict:
        """Calculate lines of code, comments, etc."""
        total_loc = 0
        total_comments = 0
        total_blank = 0
        file_count = 0
        
        for cpp_file in self.source_dir.rglob("*.cpp"):
            file_count += 1
            with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            loc = 0
            comments = 0
            blank = 0
            in_multiline_comment = False
            
            for line in lines:
                stripped = line.strip()
                
                if not stripped:
                    blank += 1
                elif stripped.startswith('//'):
                    comments += 1
                elif '/*' in stripped and '*/' in stripped:
                    # Single line /* */ comment
                    comments += 1
                elif '/*' in stripped:
                    comments += 1
                    in_multiline_comment = True
                elif '*/' in stripped:
                    comments += 1
                    in_multiline_comment = False
                elif in_multiline_comment:
                    comments += 1
                else:
                    loc += 1
            
            total_loc += loc
            total_comments += comments
            total_blank += blank
        
        total_lines = total_loc + total_comments + total_blank
        
        return {
            'total_files': file_count,
            'total_lines': total_lines,
            'lines_of_code': total_loc,
            'comment_lines': total_comments,
            'blank_lines': total_blank,
            'comment_ratio': total_comments / total_lines if total_lines > 0 else 0,
            'avg_loc_per_file': total_loc / file_count if file_count > 0 else 0
        }
    
    def check_best_practices(self) -> Dict:
        """Check for C++ best practices."""
        issues = []
        
        # Check both .cpp and .h files
        for extension in ["*.cpp", "*.h", "*.hpp"]:
            for cpp_file in self.source_dir.rglob(extension):
                with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_path = str(cpp_file.relative_to(self.source_dir))
                
                # Check for raw pointers (prefer smart pointers)
                if re.search(r'\bnew\s+\w+', content):
                    issues.append({
                        'file': file_path,
                        'issue': 'Using raw new (consider smart pointers)',
                        'severity': 'warning'
                    })
                
                # Check for manual memory management
                if re.search(r'\bdelete\b', content):
                    issues.append({
                        'file': file_path,
                        'issue': 'Manual delete (consider RAII)',
                        'severity': 'warning'
                    })
                
                # Check for C-style casts (more precise regex)
                if re.search(r'\([a-zA-Z_]\w*\s*\*?\s*\)\s*[a-zA-Z_]', content):
                    issues.append({
                        'file': file_path,
                        'issue': 'C-style cast detected (use static_cast/dynamic_cast)',
                        'severity': 'info'
                    })
                
                # Check for using namespace std in headers
                if cpp_file.suffix in ['.h', '.hpp'] and 'using namespace std' in content:
                    issues.append({
                        'file': file_path,
                        'issue': 'using namespace std in header file',
                        'severity': 'error'
                    })
                
                # Check for missing virtual destructor in base classes
                if re.search(r'class\s+\w+.*{', content) and 'virtual' in content and not re.search(r'virtual\s+~\w+', content):
                    issues.append({
                        'file': file_path,
                        'issue': 'Class with virtual methods missing virtual destructor',
                        'severity': 'warning'
                    })
        
        return {
            'issues': issues,
            'issue_count': len(issues),
            'errors': len([i for i in issues if i['severity'] == 'error']),
            'warnings': len([i for i in issues if i['severity'] == 'warning']),
            'info': len([i for i in issues if i['severity'] == 'info'])
        }
    
    def analyze_performance_patterns(self) -> Dict:
        """Check for common performance issues."""
        performance_issues = []
        
        for cpp_file in self.source_dir.rglob("*.cpp"):
            with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_path = str(cpp_file.relative_to(self.source_dir))
            
            # Check for pass-by-value of large objects
            if re.search(r'\w+\s+\w+\(.*vector<.*>\s+\w+.*\)', content):
                performance_issues.append({
                    'file': file_path,
                    'issue': 'Potential pass-by-value of vector (consider const reference)',
                    'impact': 'high'
                })
            
            # Check for string concatenation in loops
            if re.search(r'for\s*\([^)]*\)\s*{[^}]*\+\s*=.*string', content, re.MULTILINE | re.DOTALL):
                performance_issues.append({
                    'file': file_path,
                    'issue': 'String concatenation in loop (consider stringstream)',
                    'impact': 'medium'
                })
            
            # Check for unnecessary copies
            if re.search(r'auto\s+\w+\s*=\s*container\.', content):
                performance_issues.append({
                    'file': file_path,
                    'issue': 'Potential unnecessary copy (consider auto&)',
                    'impact': 'medium'
                })
            
            # Check for inefficient container access
            if re.search(r'vector.*\[\].*loop', content) and 'at(' not in content:
                performance_issues.append({
                    'file': file_path,
                    'issue': 'Consider range-based for loop for better performance',
                    'impact': 'low'
                })
        
        return {
            'performance_issues': performance_issues,
            'total_issues': len(performance_issues),
            'high_impact': len([i for i in performance_issues if i['impact'] == 'high']),
            'medium_impact': len([i for i in performance_issues if i['impact'] == 'medium']),
            'low_impact': len([i for i in performance_issues if i['impact'] == 'low'])
        }
    
    def analyze_dependencies(self) -> Dict:
        """Analyze include dependencies."""
        includes = {}
        system_includes = set()
        local_includes = set()
        
        for cpp_file in self.source_dir.rglob("*.cpp"):
            with open(cpp_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_path = str(cpp_file.relative_to(self.source_dir))
            file_includes = []
            
            # Find all includes
            include_pattern = r'#include\s*[<"](.*?)[>"]'
            matches = re.findall(include_pattern, content)
            
            for include in matches:
                file_includes.append(include)
                if include.startswith('<') or not include.endswith('.h'):
                    system_includes.add(include)
                else:
                    local_includes.add(include)
            
            includes[file_path] = file_includes
        
        return {
            'file_includes': includes,
            'system_includes': list(system_includes),
            'local_includes': list(local_includes),
            'total_system_includes': len(system_includes),
            'total_local_includes': len(local_includes)
        }
    
    def generate_report(self) -> Dict:
        """Generate complete analysis report."""
        print("Analyzing complexity...")
        complexity = self.analyze_complexity()
        
        print("Analyzing code metrics...")
        metrics = self.analyze_code_metrics()
        
        print("Checking best practices...")
        best_practices = self.check_best_practices()
        
        print("Analyzing performance patterns...")
        performance = self.analyze_performance_patterns()
        
        print("Analyzing dependencies...")
        dependencies = self.analyze_dependencies()
        
        # Calculate overall quality score
        quality_score = self.calculate_quality_score(complexity, metrics, best_practices, performance)
        
        return {
            'source_directory': str(self.source_dir),
            'complexity_analysis': complexity,
            'code_metrics': metrics,
            'best_practices': best_practices,
            'performance_analysis': performance,
            'dependencies': dependencies,
            'quality_score': quality_score
        }
    
    def calculate_quality_score(self, complexity, metrics, best_practices, performance) -> Dict:
        """Calculate an overall quality score (0-100)."""
        score = 100
        
        # Deduct points for high complexity
        if complexity['average_complexity'] > 10:
            score -= 20
        elif complexity['average_complexity'] > 5:
            score -= 10
        
        # Deduct points for low comment ratio
        if metrics['comment_ratio'] < 0.1:
            score -= 15
        elif metrics['comment_ratio'] < 0.2:
            score -= 5
        
        # Deduct points for best practice violations
        score -= best_practices['errors'] * 10
        score -= best_practices['warnings'] * 5
        score -= best_practices['info'] * 2
        
        # Deduct points for performance issues
        score -= performance['high_impact'] * 15
        score -= performance['medium_impact'] * 10
        score -= performance['low_impact'] * 5
        
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


def main():
    parser = argparse.ArgumentParser(description='Analyze C++ code quality and generate metrics')
    parser.add_argument('source_dir', help='Directory containing C++ source files')
    parser.add_argument('-o', '--output', help='Output file for JSON report (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source_dir):
        print(f"Error: Source directory '{args.source_dir}' does not exist")
        return 1
    
    analyzer = CppAnalyzer(args.source_dir)
    
    try:
        report = analyzer.generate_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            if args.verbose:
                print(json.dumps(report, indent=2))
            else:
                # Print summary
                print(f"\n=== C++ Code Quality Report ===")
                print(f"Source Directory: {report['source_directory']}")
                print(f"Quality Score: {report['quality_score']['score']}/100 (Grade: {report['quality_score']['grade']})")
                print(f"\nCode Metrics:")
                print(f"  Files: {report['code_metrics']['total_files']}")
                print(f"  Lines of Code: {report['code_metrics']['lines_of_code']}")
                print(f"  Comment Ratio: {report['code_metrics']['comment_ratio']:.2%}")
                print(f"  Avg Complexity: {report['complexity_analysis']['average_complexity']:.2f}")
                print(f"\nIssues:")
                print(f"  Errors: {report['best_practices']['errors']}")
                print(f"  Warnings: {report['best_practices']['warnings']}")
                print(f"  Performance Issues: {report['performance_analysis']['total_issues']}")
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
