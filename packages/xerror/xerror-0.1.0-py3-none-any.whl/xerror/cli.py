"""
Command Line Interface for Error Explainer.
"""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from .config import config
from .explainer import ErrorExplainer
from .parser import parser
from .utils import (
    read_file_content, read_stdin, save_explanation, 
    search_logs, display_explanation, validate_file_extension,
    get_file_size_mb
)

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="xerror")
def main():
    """
    🧪 Error Explainer - AI-powered error analysis and explanation tool.
    
    Explain Python error logs using Google's Gemini AI from your terminal.
    """
    pass


@main.command()
@click.argument('file_path', required=False)
@click.option('--paste', is_flag=True, help='Paste error interactively')
@click.option('--save', is_flag=True, help='Save explanation to log directory')
@click.option('--markdown', is_flag=True, help='Output in markdown format')
@click.option('--api-key', help='Google Gemini API key')
@click.option('--model', default='gemini-1.5-flash', help='AI model to use (gemini, openai, ollama, etc.)')
@click.option('--offline', is_flag=True, help='Use offline rule-based explanation (no AI required)')
def explain(file_path: Optional[str], paste: bool, save: bool, markdown: bool, api_key: Optional[str], model: str, offline: bool):
    """
    Explain an error from file, stdin, or interactive input.
    
    Examples:
        xerror error.log              # Read from file
        xerror --paste                # Paste error interactively  
        xerror < error.log            # Pipe file into stdin
        xerror error.log --save       # Save explanation
        xerror error.log --markdown   # Output in markdown
    """
    # Check configuration (only for AI mode)
    if not offline:
        if not config.is_configured() and not api_key:
            console.print("[red]❌ Error: Google API key not configured![/red]")
            console.print("Please set the GOOGLE_API_KEY environment variable or use --api-key option.")
            console.print("Get your API key from: https://makersuite.google.com/app/apikey")
            console.print("\n[yellow]💡 Tip: Use --offline flag for rule-based explanations without AI[/yellow]")
            sys.exit(1)
    
    # Get error content
    error_content = None
    
    if paste:
        console.print("[yellow]📝 Paste your error log below (press Enter twice when done):[/yellow]")
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        error_content = '\n'.join(lines)
    elif file_path:
        # Check if file exists and is valid
        if not Path(file_path).exists():
            console.print(f"[red]❌ Error: File not found: {file_path}[/red]")
            sys.exit(1)
        
        if not validate_file_extension(file_path):
            console.print(f"[yellow]⚠️  Warning: File extension not recognized: {Path(file_path).suffix}[/yellow]")
            console.print("Supported extensions: .log, .txt, .py, .error")
        
        # Check file size
        file_size = get_file_size_mb(file_path)
        if file_size > 10:  # 10MB limit
            console.print(f"[red]❌ Error: File too large ({file_size:.1f}MB). Maximum size is 10MB.[/red]")
            sys.exit(1)
        
        try:
            error_content = read_file_content(file_path)
        except Exception as e:
            console.print(f"[red]❌ Error reading file: {str(e)}[/red]")
            sys.exit(1)
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            error_content = read_stdin()
        else:
            console.print("[red]❌ Error: No input provided![/red]")
            console.print("Use: xerror <file> or xerror --paste or pipe input")
            sys.exit(1)
    
    if not error_content or not error_content.strip():
        console.print("[red]❌ Error: No error content provided![/red]")
        sys.exit(1)
    
    # Validate that it's a valid error and detect language
    if not parser.is_error(error_content):
        console.print("[yellow]⚠️  Warning: No valid error detected in the content.[/yellow]")
        console.print("[yellow]The tool will still attempt to explain, but results may be limited.[/yellow]")
    else:
        # Get the detected language
        detected_language = parser.get_error_language(error_content)
        console.print(f"[blue]🌐 Detected language: {detected_language.title()}[/blue]")
    
    # Initialize explainer based on mode
    if offline:
        # Use rule-based explainer
        from .rule_based_explainer import rule_explainer
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Analyzing error with rule-based system...", total=None)
            
            try:
                result = rule_explainer.explain_error(error_content)
                progress.update(task, description="✅ Analysis complete!")
            except Exception as e:
                progress.update(task, description="❌ Analysis failed!")
                console.print(f"[red]❌ Error during rule-based analysis: {str(e)}[/red]")
                sys.exit(1)
    else:
        # Use AI explainer
        try:
            explainer = ErrorExplainer(api_key=api_key, model=model)
        except Exception as e:
            console.print(f"[red]❌ Error initializing AI explainer: {str(e)}[/red]")
            sys.exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🤖 Analyzing error with AI...", total=None)
            
            try:
                result = explainer.explain_error(error_content)
                progress.update(task, description="✅ Analysis complete!")
            except Exception as e:
                progress.update(task, description="❌ Analysis failed!")
                console.print(f"[red]❌ Error during AI analysis: {str(e)}[/red]")
                sys.exit(1)
    
    # Display result
    display_explanation(result, markdown=markdown)
    
    # Save if requested
    if save and result.get('success', False):
        try:
            saved_path = save_explanation(result)
            console.print(f"\n[green]💾 Explanation saved to: {saved_path}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error saving explanation: {str(e)}[/red]")


@main.command()
@click.argument('query')
@click.option('--limit', default=10, help='Maximum number of results')
@click.option('--markdown', is_flag=True, help='Output in markdown format')
def search(query: str, limit: int, markdown: bool):
    """
    Search through saved error explanations.
    
    Examples:
        xerror search "NameError"        # Search by error type
        xerror search "undefined"        # Search by keyword
        xerror search "views.py"         # Search by filename
    """
    results = search_logs(query, limit)
    
    if not results:
        console.print(f"[yellow]🔍 No saved explanations found matching: {query}[/yellow]")
        return
    
    if markdown:
        print(f"# Search Results for: {query}")
        print()
        for i, result in enumerate(results, 1):
            print(f"## {i}. {result['error_summary']}")
            print(f"**File:** {result['file']}")
            print(f"**Time:** {result['timestamp']}")
            print()
            print(result['data'].get('explanation', 'No explanation available'))
            print()
    else:
        console.print(f"[blue]🔍 Found {len(results)} saved explanations matching: {query}[/blue]")
        console.print()
        
        for i, result in enumerate(results, 1):
            console.print(f"[bold]{i}.[/bold] {result['error_summary']}")
            console.print(f"   📁 {result['file']} | 🕒 {result['timestamp']}")
            console.print()


@main.command()
def config_check():
    """
    Check configuration and API key status.
    """
    console.print("[blue]🔧 Configuration Check[/blue]")
    console.print()
    
    # Check API key
    if config.is_configured():
        console.print("[green]✅ Google API key: Configured[/green]")
    else:
        console.print("[red]❌ Google API key: Not configured[/red]")
        console.print("   Set GOOGLE_API_KEY environment variable or use --api-key option")
    
    # Check log directory
    console.print(f"📁 Log directory: {config.log_dir}")
    if config.log_dir.exists():
        console.print("[green]✅ Log directory: Exists[/green]")
    else:
        console.print("[yellow]⚠️  Log directory: Will be created when needed[/yellow]")
    
    # Check model
    console.print(f"🤖 Default model: {config.default_model}")
    
    # Show saved explanations count
    if config.log_dir.exists():
        saved_count = len(list(config.log_dir.glob("*.json")))
        console.print(f"📊 Saved explanations: {saved_count}")


@main.command()
@click.argument('command', required=True)
@click.option('--background', '-b', is_flag=True, help='Run in background mode')
@click.option('--name', '-n', help='Name for background watcher (required if --background)')
@click.option('--offline', is_flag=True, help='Use offline rule-based explanation (no AI required)')
@click.option('--save', is_flag=True, help='Save explanations to log file')
@click.option('--api-key', help='Google Gemini API key')
@click.option('--model', default='gemini-1.5-flash', help='AI model to use (gemini, openai, ollama, etc.)')
def watch(command: str, background: bool, name: Optional[str], offline: bool, save: bool, api_key: Optional[str], model: str):
    """
    Watch a process for errors and provide real-time explanations.
    
    Examples:
        xerror watch "python my_script.py"           # Watch a Python script
        xerror watch "python manage.py runserver"    # Watch Django development server
        xerror watch "npm start" --offline           # Watch with offline explanations
        xerror watch "python app.py" --background --name "myapp"  # Background mode
    """
    try:
        from .watcher import watch_process
        
        if background:
            if not name:
                console.print("[red]❌ Error: --name is required when using --background[/red]")
                sys.exit(1)
            
            watcher_name = watch_process(
                command=command,
                use_ai=not offline,
                api_key=api_key,
                model=model,
                save_explanations=save,
                background=True,
                name=name
            )
            
            console.print(f"[green]✅ Background watcher '{watcher_name}' started successfully![/green]")
            console.print(f"[green]Use 'xerror stop {name}' to stop it later.[/green]")
            
        else:
            console.print(f"[green]🚀 Starting process watcher for: {command}[/green]")
            console.print("[green]📡 Monitoring for errors... (Press Ctrl+C to stop)[/green]\n")
            
            watch_process(
                command=command,
                use_ai=not offline,
                api_key=api_key,
                model=model,
                save_explanations=save,
                background=False
            )
            
    except ImportError:
        console.print("[red]❌ Error: Watch functionality not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error starting watcher: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.argument('name', required=True)
def stop(name: str):
    """
    Stop a background watcher by name.
    
    Examples:
        xerror stop myapp           # Stop watcher named "myapp"
        xerror stop all             # Stop all background watchers
    """
    try:
        from .watcher import stop_background_watcher, stop_all_background_watchers, list_background_watchers
        
        if name.lower() == 'all':
            stop_all_background_watchers()
            console.print("[green]✅ All background watchers stopped[/green]")
        else:
            if stop_background_watcher(name):
                console.print(f"[green]✅ Background watcher '{name}' stopped[/green]")
            else:
                console.print(f"[red]❌ Background watcher '{name}' not found[/red]")
                console.print(f"[yellow]Active watchers: {', '.join(list_background_watchers())}[/yellow]")
                
    except ImportError:
        console.print("[red]❌ Error: Watch functionality not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error stopping watcher: {str(e)}[/red]")
        sys.exit(1)


@main.command()
def list():
    """
    List all active background watchers.
    """
    try:
        from .watcher import list_background_watchers
        
        watchers = list_background_watchers()
        
        if not watchers:
            console.print("[yellow]📋 No active background watchers[/yellow]")
        else:
            console.print(f"[blue]📋 Active background watchers ({len(watchers)}):[/blue]")
            for watcher in watchers:
                console.print(f"  • {watcher}")
                
    except ImportError:
        console.print("[red]❌ Error: Watch functionality not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error listing watchers: {str(e)}[/red]")
        sys.exit(1)


@main.command()
def models():
    """
    List all available AI models.
    """
    try:
        from .models import list_available_models
        
        models = list_available_models()
        
        if not models:
            console.print("[yellow]📋 No AI models available[/yellow]")
            console.print("[yellow]💡 Install required packages:[/yellow]")
            console.print("  • Gemini: pip install google-generativeai")
            console.print("  • OpenAI: pip install openai")
            console.print("  • Ollama: Install Ollama and run: ollama serve")
        else:
            console.print(f"[blue]🤖 Available AI models ({len(models)}):[/blue]")
            for model in models:
                status = "✅" if model.get('available') else "❌"
                provider = model.get('provider', 'Unknown')
                model_name = model.get('model', 'Unknown')
                console.print(f"  {status} {provider} - {model_name}")
                
    except ImportError:
        console.print("[red]❌ Error: Model functionality not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error listing models: {str(e)}[/red]")
        sys.exit(1)


@main.command()
def languages():
    """
    List all supported programming languages.
    """
    try:
        from .language_parsers import get_supported_languages
        
        languages = get_supported_languages()
        
        if not languages:
            console.print("[yellow]📋 No languages supported[/yellow]")
        else:
            console.print(f"[blue]🌐 Supported programming languages ({len(languages)}):[/blue]")
            for lang in languages:
                console.print(f"  ✅ {lang.value.title()}")
                
    except ImportError:
        console.print("[red]❌ Error: Language functionality not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error listing languages: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.argument('error_content')
def detect(error_content: str):
    """
    Detect the programming language of an error.
    
    Examples:
        xerror detect "NameError: name 'x' is not defined"
        xerror detect "TypeError: Cannot read property 'length' of undefined"
        xerror detect "error: cannot find symbol"
    """
    try:
        from .language_parsers import detect_language, parse_error
        
        # Detect language
        language = detect_language(error_content)
        
        if language.value == 'unknown':
            console.print("[yellow]⚠️ Could not detect programming language[/yellow]")
            console.print("[yellow]💡 The error format may not be supported yet[/yellow]")
        else:
            console.print(f"[green]✅ Detected language: {language.value.title()}[/green]")
            
            # Parse error for additional info
            error_info = parse_error(error_content)
            if error_info.is_valid_error:
                console.print(f"[blue]📝 Error type: {error_info.error_type}[/blue]")
                console.print(f"[blue]📄 Error message: {error_info.error_message}[/blue]")
                if error_info.file_path:
                    console.print(f"[blue]📁 File: {error_info.file_path}[/blue]")
                if error_info.line_number:
                    console.print(f"[blue]📍 Line: {error_info.line_number}[/blue]")
            else:
                console.print("[yellow]⚠️ Could not parse error details[/yellow]")
                
    except ImportError:
        console.print("[red]❌ Error: Language detection not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error during detection: {str(e)}[/red]")
        sys.exit(1)


@main.command()
@click.argument('error_content')
@click.option('--model', default='gemini-1.5-flash', help='Model to use for benchmarking')
def benchmark(error_content: str, model: str):
    """
    Benchmark all available AI models with an error.
    
    Examples:
        xerror benchmark "NameError: name 'x' is not defined"
        xerror benchmark "TypeError: can only concatenate str (not 'int') to str"
    """
    try:
        from .models import benchmark_all_models
        from .explainer import ErrorExplainer
        
        # Create a simple prompt for benchmarking
        prompt = f"""Explain this Python error and provide a fix:

{error_content}

Please provide a clear explanation and solution."""
        
        console.print(f"[blue]🏃‍♂️ Benchmarking all available models...[/blue]")
        console.print(f"[blue]📝 Error: {error_content[:50]}...[/blue]\n")
        
        results = benchmark_all_models(error_content, prompt)
        
        if not results:
            console.print("[yellow]⚠️ No models available for benchmarking[/yellow]")
            return
        
        # Display results
        console.print("[green]📊 Benchmark Results:[/green]")
        console.print("-" * 60)
        
        for model_name, result in results.items():
            if result.get('success'):
                response_time = result.get('response_time', 0)
                provider = result.get('model_info', {}).get('provider', 'Unknown')
                console.print(f"✅ {model_name} ({provider}): {response_time:.2f}s")
            else:
                error = result.get('error', 'Unknown error')
                console.print(f"❌ {model_name}: {error}")
        
        console.print("-" * 60)
        
    except ImportError:
        console.print("[red]❌ Error: Benchmark functionality not available[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error during benchmarking: {str(e)}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main() 