"""
Utility functions for Error Explainer.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .config import config

console = Console()


def read_file_content(file_path: Union[str, Path]) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")


def read_stdin() -> str:
    """
    Read content from stdin.
    
    Returns:
        Stdin content as string
    """
    return sys.stdin.read()


def save_explanation(explanation_data: Dict, filename: Optional[str] = None) -> Path:
    """
    Save explanation to log directory.
    
    Args:
        explanation_data: Explanation data to save
        filename: Optional custom filename
        
    Returns:
        Path to saved file
    """
    # Ensure log directory exists
    config.ensure_log_directory()
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_type = explanation_data.get('parsed_error', {}).get('error_type', 'unknown')
        filename = f"{timestamp}_{error_type.lower()}.json"
    
    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    file_path = config.log_dir / filename
    
    # Add metadata
    explanation_data['saved_at'] = datetime.now().isoformat()
    explanation_data['log_file'] = str(file_path)
    
    # Save to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(explanation_data, f, indent=2, ensure_ascii=False)
    
    return file_path


def search_logs(query: str, limit: int = 10) -> list:
    """
    Search through saved explanations.
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of matching explanations
    """
    if not config.log_dir.exists():
        return []
    
    results = []
    query_lower = query.lower()
    
    for json_file in config.log_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Search in various fields
            searchable_text = " ".join([
                data.get('error_summary', ''),
                data.get('explanation', ''),
                str(data.get('parsed_error', {}).get('error_type', '')),
                str(data.get('parsed_error', {}).get('error_message', ''))
            ]).lower()
            
            if query_lower in searchable_text:
                results.append({
                    'file': json_file.name,
                    'timestamp': data.get('saved_at', ''),
                    'error_summary': data.get('error_summary', ''),
                    'data': data
                })
                
                if len(results) >= limit:
                    break
                    
        except Exception:
            continue
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    return results


def display_explanation(explanation_data: Dict, markdown: bool = False) -> None:
    """
    Display explanation in a formatted way.
    
    Args:
        explanation_data: Explanation data to display
        markdown: Whether to output in markdown format
    """
    if not explanation_data.get('success', False):
        console.print(f"[red]❌ Error: {explanation_data.get('error', 'Unknown error')}[/red]")
        return
    
    if markdown:
        # Output in markdown format
        print("# Error Explanation")
        print()
        print(f"**Error:** {explanation_data.get('error_summary', 'Unknown')}")
        print()
        print("## AI Explanation")
        print()
        print(explanation_data.get('explanation', ''))
        print()
        print("## Metadata")
        print(f"- Model: {explanation_data.get('model_used', 'Unknown')}")
        print(f"- Timestamp: {datetime.fromtimestamp(explanation_data.get('timestamp', 0)).isoformat()}")
    else:
        # Rich console output
        error_summary = explanation_data.get('error_summary', 'Unknown Error')
        explanation = explanation_data.get('explanation', 'No explanation available')
        
        # Create panels
        summary_panel = Panel(
            Text(error_summary, style="bold yellow"),
            title="🔍 Error Summary",
            border_style="yellow"
        )
        
        explanation_panel = Panel(
            Text(explanation),
            title="🧐 AI Explanation",
            border_style="blue"
        )
        
        # Display panels
        console.print(summary_panel)
        console.print()
        console.print(explanation_panel)
        
        # Show metadata
        if explanation_data.get('method') == 'rule-based':
            confidence = explanation_data.get('confidence', 'unknown')
            metadata = f"Method: Rule-based | Confidence: {confidence} | "
            metadata += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            metadata = f"Model: {explanation_data.get('model_used', 'Unknown')} | "
            metadata += f"Time: {datetime.fromtimestamp(explanation_data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}"
        
        console.print(f"\n[dim]{metadata}[/dim]")


def validate_file_extension(file_path: Union[str, Path]) -> bool:
    """
    Validate if file has supported extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file extension is supported
    """
    supported_extensions = {'.log', '.txt', '.py', '.error'}
    return Path(file_path).suffix.lower() in supported_extensions


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    return Path(file_path).stat().st_size / (1024 * 1024) 