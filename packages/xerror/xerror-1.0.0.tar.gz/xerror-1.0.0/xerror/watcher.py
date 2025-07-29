"""
Real-time error watcher for monitoring running processes.
"""

import subprocess
import signal
import sys
import time
import threading
import os
import shlex
from typing import Optional, Callable, Dict, List
from pathlib import Path
import json
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .explainer import ErrorExplainer
from .rule_based_explainer import rule_explainer
from .parser import parser
from .config import config


class ProcessWatcher:
    """Monitor a running process and detect errors in real-time."""
    
    def __init__(
        self,
        command: str,
        use_ai: bool = True,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        save_explanations: bool = False,
        background: bool = False,
        log_file: Optional[str] = None
    ):
        self.command = command
        self.use_ai = use_ai
        self.api_key = api_key
        self.model = model
        self.save_explanations = save_explanations
        self.background = background
        self.log_file = log_file
        
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.error_buffer = []
        self.error_count = 0
        
        self.console = Console()
        
        # Initialize explainer
        if use_ai:
            try:
                self.explainer = ErrorExplainer(api_key=api_key, model=model)
            except Exception as e:
                self.console.print(f"[yellow]⚠️ AI explainer failed to initialize: {e}[/yellow]")
                self.console.print("[yellow]Falling back to rule-based explanations[/yellow]")
                self.use_ai = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        self.console.print("\n[yellow]🛑 Received interrupt signal. Shutting down...[/yellow]")
        self.stop()
        sys.exit(0)
    
    def _log_error(self, error_content: str, explanation: Dict):
        """Log error and explanation to file."""
        if not self.log_file:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': self.command,
            'error_content': error_content,
            'explanation': explanation,
            'error_number': self.error_count
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, indent=2) + '\n\n')
        except Exception as e:
            self.console.print(f"[red]Failed to log error: {e}[/red]")
    
    def _explain_error(self, error_content: str) -> Dict:
        """Explain an error using AI or rule-based system."""
        try:
            if self.use_ai:
                result = self.explainer.explain_error(error_content)
            else:
                result = rule_explainer.explain_error(error_content)
            
            return result
        except Exception as e:
            # Fallback to rule-based
            self.console.print(f"[yellow]⚠️ AI explanation failed: {e}[/yellow]")
            self.console.print("[yellow]Using rule-based fallback[/yellow]")
            return rule_explainer.explain_error(error_content)
    
    def _display_error_explanation(self, error_content: str, explanation: Dict):
        """Display error explanation in a formatted way."""
        self.error_count += 1
        
        # Create error panel
        error_text = Text()
        error_text.append(f"🚨 Error #{self.error_count}\n", style="red bold")
        error_text.append(f"⏰ {datetime.now().strftime('%H:%M:%S')}\n", style="cyan")
        error_text.append(f"🔍 {explanation.get('error_summary', 'Unknown error')}\n", style="yellow")
        
        if explanation.get('explanation'):
            error_text.append("\n🧐 Explanation:\n", style="bold")
            error_text.append(explanation['explanation'][:200] + "...\n", style="white")
        
        if explanation.get('suggested_fixes'):
            error_text.append("\n🔧 Quick Fix:\n", style="bold green")
            for i, fix in enumerate(explanation['suggested_fixes'][:2], 1):
                error_text.append(f"{i}. {fix}\n", style="green")
        
        error_panel = Panel(
            error_text,
            title="[bold red]Error Detected![/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        
        self.console.print(error_panel)
        
        # Log if requested
        if self.save_explanations:
            self._log_error(error_content, explanation)
    
    def _process_output_line(self, line: str, is_stderr: bool = False):
        """Process a single line of output and detect errors."""
        if not line.strip():
            return
        
        # Add to buffer
        self.error_buffer.append(line)
        
        # Keep only last 20 lines
        if len(self.error_buffer) > 20:
            self.error_buffer.pop(0)
        
        # Check if this looks like an error
        if is_stderr or self._is_error_line(line):
            # Get the last few lines as context
            error_context = '\n'.join(self.error_buffer[-10:])
            
            # Check if it's a Python error
            if parser.is_python_error(error_context):
                # Explain the error
                explanation = self._explain_error(error_context)
                
                if explanation.get('success', False):
                    self._display_error_explanation(error_context, explanation)
                
                # Clear buffer after processing
                self.error_buffer.clear()
    
    def _is_error_line(self, line: str) -> bool:
        """Check if a line looks like an error."""
        error_indicators = [
            'Traceback',
            'Error:',
            'Exception:',
            'Failed',
            'ERROR',
            'FATAL',
            'CRITICAL'
        ]
        
        line_lower = line.lower()
        return any(indicator.lower() in line_lower for indicator in error_indicators)
    
    def _monitor_process(self):
        """Monitor the running process for errors."""
        try:
            # Start the process
            self.process = subprocess.Popen(
                shlex.split(self.command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.console.print(f"[green]🚀 Started process: {self.command}[/green]")
            self.console.print("[green]📡 Monitoring for errors... (Press Ctrl+C to stop)[/green]\n")
            
            # Monitor stdout and stderr
            while self.running and self.process.poll() is None:
                # Check stdout
                stdout_line = self.process.stdout.readline()
                if stdout_line:
                    self.console.print(f"[blue]STDOUT:[/blue] {stdout_line.rstrip()}")
                    self._process_output_line(stdout_line, is_stderr=False)
                
                # Check stderr
                stderr_line = self.process.stderr.readline()
                if stderr_line:
                    self.console.print(f"[red]STDERR:[/red] {stderr_line.rstrip()}")
                    self._process_output_line(stderr_line, is_stderr=True)
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
            
            # Process any remaining output
            if self.process.poll() is not None:
                remaining_stdout, remaining_stderr = self.process.communicate()
                
                if remaining_stdout:
                    for line in remaining_stdout.splitlines():
                        self.console.print(f"[blue]STDOUT:[/blue] {line}")
                        self._process_output_line(line, is_stderr=False)
                
                if remaining_stderr:
                    for line in remaining_stderr.splitlines():
                        self.console.print(f"[red]STDERR:[/red] {line}")
                        self._process_output_line(line, is_stderr=True)
                
                self.console.print(f"\n[green]✅ Process completed with exit code: {self.process.returncode}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Error monitoring process: {e}[/red]")
        finally:
            self.running = False
    
    def start(self):
        """Start monitoring the process."""
        self.running = True
        
        if self.background:
            # Run in background thread
            thread = threading.Thread(target=self._monitor_process, daemon=True)
            thread.start()
            return thread
        else:
            # Run in main thread
            self._monitor_process()
    
    def stop(self):
        """Stop monitoring and terminate the process."""
        self.running = False
        
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                self.console.print(f"[red]Error stopping process: {e}[/red]")
        
        self.console.print(f"\n[green]📊 Summary: {self.error_count} errors detected and explained[/green]")


class BackgroundWatcherManager:
    """Manage background watcher processes."""
    
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = log_dir or Path.home() / ".error_explainer_logs" / "background"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.console = Console()
        self.active_watchers: Dict[str, ProcessWatcher] = {}
        self.pid_file = self.log_dir / "active_watchers.json"
    
    def start_background_watcher(
        self,
        command: str,
        name: Optional[str] = None,
        use_ai: bool = True,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash"
    ) -> str:
        """Start a background watcher."""
        if not name:
            name = f"watcher_{int(time.time())}"
        
        log_file = self.log_dir / f"{name}.log"
        
        watcher = ProcessWatcher(
            command=command,
            use_ai=use_ai,
            api_key=api_key,
            model=model,
            save_explanations=True,
            background=True,
            log_file=str(log_file)
        )
        
        # Start in background
        thread = watcher.start()
        
        # Store watcher info
        self.active_watchers[name] = watcher
        
        # Save to PID file
        self._save_watcher_info()
        
        self.console.print(f"[green]✅ Started background watcher '{name}' for: {command}[/green]")
        self.console.print(f"[green]📝 Log file: {log_file}[/green]")
        
        return name
    
    def stop_background_watcher(self, name: str) -> bool:
        """Stop a background watcher."""
        if name not in self.active_watchers:
            self.console.print(f"[red]❌ Watcher '{name}' not found[/red]")
            return False
        
        watcher = self.active_watchers[name]
        watcher.stop()
        del self.active_watchers[name]
        
        self._save_watcher_info()
        self.console.print(f"[green]✅ Stopped background watcher '{name}'[/green]")
        return True
    
    def list_background_watchers(self) -> List[str]:
        """List all active background watchers."""
        return list(self.active_watchers.keys())
    
    def stop_all_watchers(self):
        """Stop all background watchers."""
        for name in list(self.active_watchers.keys()):
            self.stop_background_watcher(name)
    
    def _save_watcher_info(self):
        """Save active watcher information to file."""
        watcher_info = {
            name: {
                'command': watcher.command,
                'started_at': datetime.now().isoformat(),
                'error_count': watcher.error_count
            }
            for name, watcher in self.active_watchers.items()
        }
        
        try:
            with open(self.pid_file, 'w') as f:
                json.dump(watcher_info, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]Failed to save watcher info: {e}[/red]")


# Global background watcher manager
background_manager = BackgroundWatcherManager()


def watch_process(
    command: str,
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    save_explanations: bool = False,
    background: bool = False,
    name: Optional[str] = None
) -> Optional[str]:
    """
    Watch a process for errors and provide real-time explanations.
    
    Args:
        command: Command to run and monitor
        use_ai: Whether to use AI explanations
        api_key: Google Gemini API key
        model: AI model to use
        save_explanations: Whether to save explanations to log
        background: Whether to run in background
        name: Name for background watcher (required if background=True)
    
    Returns:
        Watcher name if background=True, None otherwise
    """
    if background and not name:
        raise ValueError("Name is required for background watchers")
    
    if background:
        return background_manager.start_background_watcher(
            command=command,
            name=name,
            use_ai=use_ai,
            api_key=api_key,
            model=model
        )
    else:
        watcher = ProcessWatcher(
            command=command,
            use_ai=use_ai,
            api_key=api_key,
            model=model,
            save_explanations=save_explanations,
            background=False
        )
        watcher.start()
        return None


def stop_background_watcher(name: str) -> bool:
    """Stop a background watcher by name."""
    return background_manager.stop_background_watcher(name)


def list_background_watchers() -> List[str]:
    """List all active background watchers."""
    return background_manager.list_background_watchers()


def stop_all_background_watchers():
    """Stop all background watchers."""
    background_manager.stop_all_watchers() 