"""Extract metrics from executed Jupyter notebooks."""

import argparse
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import nbformat
from datetime import datetime


def extract_metrics_from_notebook(notebook_path: Path) -> Dict[str, Any]:
    """
    Extract metrics from notebook outputs.
    
    Looks for cells with outputs containing metrics like:
    - accuracy, precision, recall, f1
    - loss, train_loss, val_loss
    - Any numeric values labeled as metrics
    """
    metrics = {
        'file': str(notebook_path),
        'extracted_metrics': {},
        'training_history': [],
        'model_performance': {},
        'execution_info': {},
        'errors': []
    }
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract notebook metadata
        metrics['execution_info'] = extract_execution_info(nb)
        
        for cell_idx, cell in enumerate(nb.cells):
            if cell.cell_type != 'code':
                continue
            
            cell_metrics = {}
            
            # Check cell outputs
            for output in cell.get('outputs', []):
                if output.get('output_type') == 'stream':
                    text = ''.join(output.get('text', []))
                    cell_metrics.update(extract_metrics_from_text(text))
                
                elif output.get('output_type') == 'execute_result':
                    data = output.get('data', {})
                    if 'text/plain' in data:
                        text = ''.join(data['text/plain'])
                        cell_metrics.update(extract_metrics_from_text(text))
                
                elif output.get('output_type') == 'display_data':
                    data = output.get('data', {})
                    if 'text/plain' in data:
                        text = ''.join(data['text/plain'])
                        cell_metrics.update(extract_metrics_from_text(text))
                
                elif output.get('output_type') == 'error':
                    error_info = {
                        'cell': cell_idx,
                        'error_name': output.get('ename', 'Unknown'),
                        'error_value': output.get('evalue', ''),
                        'traceback': output.get('traceback', [])
                    }
                    metrics['errors'].append(error_info)
            
            # If we found metrics in this cell, store them
            if cell_metrics:
                metrics['extracted_metrics'][f'cell_{cell_idx}'] = cell_metrics
                
                # Categorize metrics
                categorize_metrics(cell_metrics, metrics)
        
        # Extract training history patterns
        metrics['training_history'] = extract_training_history(nb)
        
        # Extract model evaluation results
        metrics['model_performance'] = extract_model_performance(nb)
        
    except Exception as e:
        metrics['errors'].append({
            'type': 'notebook_parsing_error',
            'message': str(e)
        })
    
    return metrics


def extract_execution_info(nb: nbformat.NotebookNode) -> Dict[str, Any]:
    """Extract notebook execution information."""
    info = {
        'kernel_spec': nb.metadata.get('kernelspec', {}),
        'language_info': nb.metadata.get('language_info', {}),
        'total_cells': len(nb.cells),
        'code_cells': sum(1 for cell in nb.cells if cell.cell_type == 'code'),
        'markdown_cells': sum(1 for cell in nb.cells if cell.cell_type == 'markdown'),
        'executed_cells': 0,
        'execution_times': []
    }
    
    for cell in nb.cells:
        if cell.cell_type == 'code' and cell.get('execution_count'):
            info['executed_cells'] += 1
            
            # Extract execution timing if available
            metadata = cell.get('metadata', {})
            if 'execution' in metadata:
                exec_data = metadata['execution']
                if 'iopub.execute_input' in exec_data and 'iopub.status.idle' in exec_data:
                    try:
                        start_time = datetime.fromisoformat(exec_data['iopub.execute_input'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(exec_data['iopub.status.idle'].replace('Z', '+00:00'))
                        duration = (end_time - start_time).total_seconds()
                        info['execution_times'].append(duration)
                    except:
                        pass
    
    if info['execution_times']:
        info['avg_execution_time'] = sum(info['execution_times']) / len(info['execution_times'])
        info['total_execution_time'] = sum(info['execution_times'])
    
    return info


def extract_metrics_from_text(text: str) -> Dict[str, float]:
    """Extract numeric metrics from text output."""
    metrics = {}
    
    # Common metric patterns
    metric_patterns = [
        # Standard ML metrics
        r'(?:^|\s)(accuracy|acc)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(precision|prec)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(recall|rec)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(f1[\s_-]?score|f1)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(auc|roc[\s_-]?auc)[\s:=]+([0-9]*\.?[0-9]+)',
        
        # Loss metrics
        r'(?:^|\s)(loss|train[\s_-]?loss|training[\s_-]?loss)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(val[\s_-]?loss|validation[\s_-]?loss)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(test[\s_-]?loss)[\s:=]+([0-9]*\.?[0-9]+)',
        
        # Error metrics
        r'(?:^|\s)(mse|mean[\s_-]?squared[\s_-]?error)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(mae|mean[\s_-]?absolute[\s_-]?error)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(rmse|root[\s_-]?mean[\s_-]?squared[\s_-]?error)[\s:=]+([0-9]*\.?[0-9]+)',
        
        # R-squared and correlation
        r'(?:^|\s)(r2|r[\s_-]?squared)[\s:=]+([0-9]*\.?[0-9]+)',
        r'(?:^|\s)(correlation|corr)[\s:=]+([0-9]*\.?[0-9]+)',
        
        # Time metrics
        r'(?:^|\s)(epoch|step)[\s:=]+([0-9]+)',
        r'(?:^|\s)(time|duration|elapsed)[\s:=]+([0-9]*\.?[0-9]+)',
        
        # Custom metric pattern: "metric_name: value"
        r'([a-zA-Z_][a-zA-Z0-9_]*)[\s:=]+([0-9]*\.?[0-9]+)(?:\s|$)',
    ]
    
    for pattern in metric_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            metric_name = match[0].lower().replace(' ', '_').replace('-', '_')
            try:
                metric_value = float(match[1])
                metrics[metric_name] = metric_value
            except ValueError:
                continue
    
    # Extract metrics from sklearn classification reports
    classification_metrics = extract_classification_report_metrics(text)
    metrics.update(classification_metrics)
    
    # Extract metrics from pandas describe() output
    describe_metrics = extract_describe_metrics(text)
    metrics.update(describe_metrics)
    
    return metrics


def extract_classification_report_metrics(text: str) -> Dict[str, float]:
    """Extract metrics from sklearn classification report."""
    metrics = {}
    
    # Look for classification report pattern
    if 'precision' in text.lower() and 'recall' in text.lower() and 'f1-score' in text.lower():
        lines = text.split('\n')
        for line in lines:
            # Look for overall metrics (macro avg, weighted avg, etc.)
            if any(keyword in line.lower() for keyword in ['macro avg', 'weighted avg', 'micro avg']):
                parts = line.split()
                if len(parts) >= 5:
                    avg_type = parts[0] + '_' + parts[1]
                    try:
                        metrics[f'{avg_type}_precision'] = float(parts[2])
                        metrics[f'{avg_type}_recall'] = float(parts[3])
                        metrics[f'{avg_type}_f1_score'] = float(parts[4])
                    except (ValueError, IndexError):
                        continue
            
            # Look for accuracy
            elif 'accuracy' in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    try:
                        if 'accuracy' in part.lower() and i + 1 < len(parts):
                            metrics['accuracy'] = float(parts[i + 1])
                            break
                    except ValueError:
                        continue
    
    return metrics


def extract_describe_metrics(text: str) -> Dict[str, float]:
    """Extract metrics from pandas DataFrame.describe() output."""
    metrics = {}
    
    if 'count' in text.lower() and 'mean' in text.lower() and 'std' in text.lower():
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(stat in line.lower() for stat in ['count', 'mean', 'std', 'min', 'max']):
                parts = line.split()
                if len(parts) >= 2:
                    stat_name = parts[0].lower()
                    try:
                        stat_value = float(parts[1])
                        metrics[f'data_{stat_name}'] = stat_value
                    except (ValueError, IndexError):
                        continue
    
    return metrics


def categorize_metrics(cell_metrics: Dict[str, float], overall_metrics: Dict[str, Any]) -> None:
    """Categorize metrics into training history and model performance."""
    
    training_keywords = ['loss', 'train', 'val', 'validation', 'epoch', 'step']
    performance_keywords = ['accuracy', 'precision', 'recall', 'f1', 'auc', 'mse', 'mae', 'rmse', 'r2']
    
    for metric_name, metric_value in cell_metrics.items():
        # Check if it's a training metric
        if any(keyword in metric_name.lower() for keyword in training_keywords):
            if 'training_metrics' not in overall_metrics:
                overall_metrics['training_metrics'] = {}
            overall_metrics['training_metrics'][metric_name] = metric_value
        
        # Check if it's a performance metric
        elif any(keyword in metric_name.lower() for keyword in performance_keywords):
            overall_metrics['model_performance'][metric_name] = metric_value


def extract_training_history(nb: nbformat.NotebookNode) -> List[Dict[str, Any]]:
    """Extract training history from notebook outputs."""
    training_history = []
    
    for cell_idx, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        
        for output in cell.get('outputs', []):
            text = ""
            if output.get('output_type') == 'stream':
                text = ''.join(output.get('text', []))
            elif output.get('output_type') in ['execute_result', 'display_data']:
                data = output.get('data', {})
                if 'text/plain' in data:
                    text = ''.join(data['text/plain'])
            
            # Look for epoch-based training logs
            epoch_pattern = r'Epoch\s+(\d+)/(\d+).*?loss:\s*([0-9]*\.?[0-9]+).*?(?:val_loss:\s*([0-9]*\.?[0-9]+))?'
            matches = re.findall(epoch_pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                epoch_data = {
                    'cell': cell_idx,
                    'epoch': int(match[0]),
                    'total_epochs': int(match[1]),
                    'loss': float(match[2])
                }
                if match[3]:  # val_loss exists
                    epoch_data['val_loss'] = float(match[3])
                
                training_history.append(epoch_data)
    
    return training_history


def extract_model_performance(nb: nbformat.NotebookNode) -> Dict[str, Any]:
    """Extract final model performance metrics."""
    performance = {
        'final_metrics': {},
        'confusion_matrix': None,
        'feature_importance': []
    }
    
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        
        for output in cell.get('outputs', []):
            text = ""
            if output.get('output_type') == 'stream':
                text = ''.join(output.get('text', []))
            elif output.get('output_type') in ['execute_result', 'display_data']:
                data = output.get('data', {})
                if 'text/plain' in data:
                    text = ''.join(data['text/plain'])
            
            # Look for final test results
            if 'test' in text.lower() and any(metric in text.lower() for metric in ['accuracy', 'precision', 'recall', 'f1']):
                test_metrics = extract_metrics_from_text(text)
                for key, value in test_metrics.items():
                    if 'test' in key or any(metric in key for metric in ['accuracy', 'precision', 'recall', 'f1']):
                        performance['final_metrics'][key] = value
    
    return performance


def analyze_notebook_directory(directory_path: Path) -> Dict[str, Any]:
    """Analyze all notebooks in a directory."""
    results = {
        'directory': str(directory_path),
        'notebooks': {},
        'summary': {
            'total_notebooks': 0,
            'successfully_analyzed': 0,
            'with_errors': 0,
            'with_metrics': 0
        },
        'aggregated_metrics': {}
    }
    
    notebook_files = list(directory_path.rglob("*.ipynb"))
    results['summary']['total_notebooks'] = len(notebook_files)
    
    all_metrics = []
    
    for notebook_path in notebook_files:
        print(f"Analyzing {notebook_path.name}...")
        
        notebook_metrics = extract_metrics_from_notebook(notebook_path)
        notebook_name = notebook_path.relative_to(directory_path)
        results['notebooks'][str(notebook_name)] = notebook_metrics
        
        if notebook_metrics['errors']:
            results['summary']['with_errors'] += 1
        else:
            results['summary']['successfully_analyzed'] += 1
        
        if notebook_metrics['extracted_metrics']:
            results['summary']['with_metrics'] += 1
            all_metrics.append(notebook_metrics)
    
    # Aggregate metrics across all notebooks
    if all_metrics:
        results['aggregated_metrics'] = aggregate_metrics(all_metrics)
    
    return results


def aggregate_metrics(notebook_metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate metrics across multiple notebooks."""
    aggregated = {
        'common_metrics': {},
        'best_performance': {},
        'training_summary': {
            'total_epochs': 0,
            'avg_final_loss': None,
            'convergence_analysis': []
        }
    }
    
    # Collect all metric names
    all_metric_names = set()
    metric_values = {}
    
    for nb_metrics in notebook_metrics_list:
        for cell_metrics in nb_metrics['extracted_metrics'].values():
            for metric_name, value in cell_metrics.items():
                all_metric_names.add(metric_name)
                if metric_name not in metric_values:
                    metric_values[metric_name] = []
                metric_values[metric_name].append(value)
    
    # Calculate statistics for common metrics
    for metric_name, values in metric_values.items():
        if len(values) > 1:  # Only include metrics that appear in multiple places
            aggregated['common_metrics'][metric_name] = {
                'count': len(values),
                'mean': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'values': values
            }
            
            # Track best performance
            if any(perf_keyword in metric_name.lower() for perf_keyword in ['accuracy', 'f1', 'auc', 'r2']):
                aggregated['best_performance'][metric_name] = max(values)
            elif any(loss_keyword in metric_name.lower() for loss_keyword in ['loss', 'error', 'mse', 'mae']):
                aggregated['best_performance'][metric_name] = min(values)
    
    return aggregated


def generate_report(results: Dict[str, Any], output_format: str = 'json') -> str:
    """Generate a formatted report."""
    if output_format == 'json':
        return json.dumps(results, indent=2)
    
    elif output_format == 'summary':
        report_lines = []
        report_lines.append("=== Jupyter Notebook Metrics Analysis ===")
        report_lines.append(f"Directory: {results['directory']}")
        report_lines.append(f"Notebooks analyzed: {results['summary']['total_notebooks']}")
        report_lines.append(f"Successfully analyzed: {results['summary']['successfully_analyzed']}")
        report_lines.append(f"With metrics: {results['summary']['with_metrics']}")
        report_lines.append(f"With errors: {results['summary']['with_errors']}")
        
        if results['aggregated_metrics']['best_performance']:
            report_lines.append("\nBest Performance Metrics:")
            for metric, value in results['aggregated_metrics']['best_performance'].items():
                report_lines.append(f"  {metric}: {value:.4f}")
        
        if results['aggregated_metrics']['common_metrics']:
            report_lines.append("\nCommon Metrics Summary:")
            for metric, stats in results['aggregated_metrics']['common_metrics'].items():
                report_lines.append(f"  {metric}:")
                report_lines.append(f"    Mean: {stats['mean']:.4f}")
                report_lines.append(f"    Range: {stats['min']:.4f} - {stats['max']:.4f}")
                report_lines.append(f"    Count: {stats['count']}")
        
        return '\n'.join(report_lines)
    
    return str(results)


def main():
    parser = argparse.ArgumentParser(description='Extract metrics from Jupyter notebooks')
    parser.add_argument('path', help='Path to notebook file or directory containing notebooks')
    parser.add_argument('-o', '--output', help='Output file for results (default: stdout)')
    parser.add_argument('-f', '--format', choices=['json', 'summary'], default='summary',
                       help='Output format (default: summary)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    try:
        if path.is_file() and path.suffix == '.ipynb':
            # Single notebook analysis
            results = extract_metrics_from_notebook(path)
            if args.format == 'summary':
                print("=== Single Notebook Analysis ===")
                print(f"File: {results['file']}")
                print(f"Executed cells: {results['execution_info']['executed_cells']}")
                if results['extracted_metrics']:
                    print("Extracted metrics:")
                    for cell, metrics in results['extracted_metrics'].items():
                        print(f"  {cell}: {metrics}")
                if results['errors']:
                    print(f"Errors found: {len(results['errors'])}")
                output_text = json.dumps(results, indent=2) if args.verbose else "Use -v for full output"
            else:
                output_text = generate_report(results, args.format)
        
        elif path.is_dir():
            # Directory analysis
            results = analyze_notebook_directory(path)
            output_text = generate_report(results, args.format)
        
        else:
            print(f"Error: '{args.path}' is not a notebook file (.ipynb) or directory")
            return 1
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"Results saved to {args.output}")
        else:
            print(output_text)
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
