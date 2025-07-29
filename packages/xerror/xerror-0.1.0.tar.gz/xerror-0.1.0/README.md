# 🧪 Error Explainer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-xerror-blue.svg)](https://pypi.org/project/xerror/)

**AI-powered error analysis and explanation tool for Python developers.**

Explain Python error logs using Google's Gemini AI directly from your terminal. Get instant, intelligent explanations and fix suggestions for any Python error.

## ✨ Features

- 🤖 **AI-Powered Explanations**: Uses Google Gemini 1.5 Flash for intelligent error analysis
- 🔍 **Offline Rule-Based Analysis**: Works without AI - instant explanations for common errors
- 📁 **Multiple Input Methods**: Read from files, stdin, or paste interactively
- 💾 **Save & Search**: Store explanations and search through your error history
- 🎨 **Rich Output**: Beautiful terminal formatting with progress indicators
- 🔍 **Smart Parsing**: Intelligent Python traceback and error detection
- 📊 **Markdown Export**: Export explanations in markdown format
- ⚡ **Fast & Lightweight**: Quick analysis with minimal dependencies
- 🌐 **Works Offline**: No internet connection required for rule-based mode

## 🚀 Quick Start

### Installation

```bash
pip install xerror
```

### Setup API Key

1. Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:

```bash
export GOOGLE_API_KEY=your-api-key-here
```

Or create a `.env` file in your project directory:

```env
GOOGLE_API_KEY=your-api-key-here
```

### Basic Usage

```bash
# Explain error from file (AI mode - requires API key)
xerror error.log

# Explain error offline (no API key required)
xerror error.log --offline

# Paste error interactively
xerror --paste

# Paste error offline
xerror --paste --offline

# Pipe error from stdin
xerror < error.log

# Save explanation to history
xerror error.log --save

# Output in markdown format
xerror error.log --markdown
```

## 🐍 Python API

The Error Explainer also provides a Python API for programmatic use:

```python
import error_explainer

# Basic usage
result = error_explainer.explain_error("NameError: name 'x' is not defined")
print(result['explanation'])

# Quick explanation (rule-based only)
explanation = error_explainer.quick_explain("TypeError: can only concatenate str (not 'int') to str")
print(explanation)

# Automatic error handling
with error_explainer.auto_explain_exceptions():
    undefined_variable  # This will be automatically explained

# Function decorator
@error_explainer.explain_function_errors()
def my_function():
    return undefined_variable
```

**See [API Documentation](API_DOCUMENTATION.md) for complete API reference.**

## 📖 Usage Examples

### 1. File-based Error Analysis

```bash
# Analyze a Python error log file (AI mode)
xerror my_error.log

# Analyze a Python error log file (offline mode)
xerror my_error.log --offline
```

**Example Output (Offline Mode):**
```
🔍 Error Summary
NameError: name 'context' is not defined (in views.py:22)

🧐 Explanation
This error occurs when you try to use a variable or function that hasn't been defined or imported.

🔧 Suggested Fixes:
1. Define the variable before using it: `variable_name = value`
2. Import the required module: `from module import function`
3. Check for typos in variable names
4. Ensure the variable is in the correct scope

💡 Prevention Tips:
1. Always define variables before using them
2. Use meaningful variable names to avoid typos
3. Import required modules at the top of your file
4. Use an IDE with autocomplete to catch undefined variables
```

### 2. Interactive Error Pasting

```bash
xerror --paste
```

Then paste your error when prompted.

### 3. Save Explanations

```bash
# Save explanation to ~/.error_explainer_logs/
xerror error.log --save
```

### 4. Search Past Explanations

```bash
# Search by error type
xerror search "NameError"

# Search by keyword
xerror search "undefined"

# Search by filename
xerror search "views.py"
```

### 5. Markdown Export

```bash
# Export explanation in markdown format
xerror error.log --markdown
```

### 6. Configuration Check

```bash
# Check your setup
xerror config-check
```

## 🔧 Advanced Usage

### AI Mode vs Offline Mode

**AI Mode** (Default):
- Requires Google Gemini API key
- Provides detailed, contextual explanations
- Best for complex or unique errors
- Requires internet connection

**Offline Mode**:
- No API key required
- Instant rule-based explanations
- Covers common Python errors
- Works completely offline

```bash
# AI mode (requires API key)
xerror error.log

# Offline mode (no API key needed)
xerror error.log --offline
```

### Custom API Key

```bash
# Use custom API key for this session
xerror error.log --api-key your-custom-key
```

### Different AI Model

```bash
# Use a different Gemini model
xerror error.log --model gemini-1.5-pro
```

### Search with Limits

```bash
# Limit search results
xerror search "error" --limit 5
```

## 📁 Supported File Formats

- `.log` - Log files
- `.txt` - Text files
- `.py` - Python files
- `.error` - Error files

## 🏗️ Project Structure

```
xerror/
├── xerror/
│   ├── __init__.py          # Package initialization
│   ├── cli.py              # Command line interface
│   ├── config.py           # Configuration management
│   ├── explainer.py        # AI explanation engine
│   ├── parser.py           # Error parsing logic
│   └── utils.py            # Utility functions
├── examples/
│   └── error_sample.log    # Example error files
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🔮 Coming Soon

- 🎯 **Real-time Watch Mode**: Monitor running processes for live error detection
- 🔄 **Background Mode**: Daemon-style error monitoring
- 🌐 **Multi-language Support**: JavaScript, TypeScript, C++ error parsing
- 🤖 **Multi-model Support**: OpenAI, Claude, Ollama integration
- 🔌 **VSCode Extension**: IDE integration
- 📱 **Desktop Notifications**: Get notified of critical errors

## 🛠️ Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/xerror/xerror.git
cd xerror

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=xerror
```

### Building for Distribution

```bash
# Build package
python setup.py sdist bdist_wheel

# Install from local build
pip install dist/error_explainer-0.1.0.tar.gz
```

## 📋 Requirements

- Python 3.10+
- Google Gemini API key (only for AI mode)
- Internet connection (only for AI mode)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for providing the AI capabilities
- [Click](https://click.palletsprojects.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Python Community](https://www.python.org/community/) for inspiration

## 📞 Support

- 📧 Email: contact@xerror.dev
- 🐛 Issues: [GitHub Issues](https://github.com/xerror/xerror/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/xerror/xerror/wiki)

---

**Made with ❤️ for Python developers everywhere** 