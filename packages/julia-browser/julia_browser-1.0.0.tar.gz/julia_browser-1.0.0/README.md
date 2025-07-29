# Julia Browser 🌐

A comprehensive Python-based CLI web browser with JavaScript support and modern web compatibility.

Julia Browser transforms command-line web browsing into a dynamic, intelligent experience with comprehensive JavaScript simulation and rendering capabilities.

## Features

- **Enhanced JavaScript Engine**: Mozilla SpiderMonkey integration via PythonMonkey
- **Modern Web Compatibility**: Full HTML DOM API, CSS Object Model (CSSOM), and modern JavaScript APIs
- **Interactive CLI Interface**: Rich terminal interface with comprehensive web interaction support
- **Advanced Navigation**: Back/forward, bookmarks, history, and smart link following
- **Intelligent Content Processing**: Dynamic content filtering and clean markdown output
- **Performance Optimizations**: Caching, asynchronous execution, and connection pooling
- **Real Web Interactions**: Form submission, file uploads, authentication flows
- **Multiple Output Formats**: Markdown, HTML, and JSON rendering
- **Responsive Design Detection**: Breakpoint analysis and mobile-first patterns

## Installation

```bash
pip install julia-browser
```

## Quick Start

### Command Line Usage

```bash
# Browse a website
julia-browser browse https://example.com

# Start interactive mode
julia-browser interactive

# Render to different formats
julia-browser render https://api.github.com --format json
```

### Python API

```python
from julia_browser import BrowserEngine, BrowserSDK

# Initialize browser
sdk = BrowserSDK()

# Browse a website
result = sdk.browse_url("https://example.com")
print(result['markdown'])

# Interactive CLI
from julia_browser import CLIBrowser
browser = CLIBrowser()
browser.start_interactive_mode()
```

## Interactive Mode Commands

- `browse <url>` - Navigate to a website
- `elements` - Show all interactive elements (buttons, links, forms)
- `click <number>` - Click on numbered elements
- `type <text>` - Type into input fields
- `submit` - Submit forms
- `back/forward` - Navigate browser history
- `bookmark add <name>` - Save bookmarks
- `help` - Show all commands

## Advanced Features

### JavaScript Support
- Full ES6+ compatibility with Mozilla SpiderMonkey
- React, Vue, Angular framework support
- Real API calls and network requests
- Modern browser API simulation

### Web Interaction
- Smart form handling with real submission
- File upload support
- Authentication flows and session management
- Cookie handling and persistent sessions

### Performance
- Intelligent caching with SQLite backend
- Asynchronous request handling
- Connection pooling and optimization
- Lazy loading for large websites

## Examples

### Browse and Interact
```bash
julia-browser interactive
> browse github.com
> elements
> click 1  # Click login button
> type username myuser
> type password mypass
> submit
```

### API Integration
```python
from julia_browser import BrowserSDK

sdk = BrowserSDK()

# Handle JSON APIs
result = sdk.browse_url("https://api.github.com/users/octocat")
user_data = result['json_data']

# Process forms
result = sdk.submit_form("https://httpbin.org/post", {
    "username": "test",
    "email": "test@example.com"
})
```

## Requirements

- Python 3.8+
- PythonMonkey (Mozilla SpiderMonkey)
- Rich (terminal formatting)
- Click (CLI framework)
- BeautifulSoup4 (HTML parsing)
- Requests (HTTP client)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

## Links

- [Documentation](https://docs.juliabrowser.com)
- [GitHub Repository](https://github.com/juliabrowser/julia-browser)
- [Issue Tracker](https://github.com/juliabrowser/julia-browser/issues)
- [PyPI Package](https://pypi.org/project/julia-browser/)