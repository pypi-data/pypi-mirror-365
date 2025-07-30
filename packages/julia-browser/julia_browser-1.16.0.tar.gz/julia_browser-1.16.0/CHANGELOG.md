# Changelog

All notable changes to Julia Browser will be documented in this file.

## [1.16.0] - 2025-01-29

### Added
- Clean rendering mode as default to show only core page content
- Comprehensive technical content filtering (CSS blocks, accessibility markers, media queries)
- Simplified form element display without technical attributes
- Enhanced content filtering to remove implementation details

### Fixed
- Eliminated CSS code blocks from rendered output
- Removed accessibility labels and custom element details from clean display
- Filtered out media conditions and form validation technical information
- Clean, readable markdown output focused on actual website content

## [1.15.0] - 2025-01-29

### Fixed
- **JavaScript Bridge Return Values**: Resolved critical issue where JavaScript engine always returned empty dictionaries instead of actual JavaScript values. Modified execute_script() method to return pm.eval() result directly instead of DOM modifications only. JavaScript expressions now properly return values: 2+2 returns 4.0, "hello" returns "hello", true returns True, document.title returns actual page title.

- **Interactive Mode Session Loop**: Resolved issue where interactive CLI mode immediately exited after showing welcome screen. Changed EOFError handling from break to continue with user message, preventing premature session termination. Interactive mode now maintains proper session state and waits for user input instead of exiting immediately.

### Improved
- JavaScript-Python bridge communication now provides real bidirectional communication between contexts
- Interactive CLI maintains proper session loops without premature termination
- Component integration improved with consistent method naming across modules
- Enhanced error handling in JavaScript execution with better debugging output

## [1.0.0] - 2025-01-26

### Added
- Initial release of Julia Browser
- Enhanced JavaScript engine with Mozilla SpiderMonkey integration
- Interactive CLI interface with Rich terminal formatting
- Modern web compatibility with HTML DOM API and CSS Object Model
- Advanced navigation system with back/forward, bookmarks, and history
- Intelligent content processing and clean markdown output
- Performance optimizations with caching and asynchronous execution
- Real web interactions including form submission and file uploads
- Authentication flows and session management
- Multiple output formats (Markdown, HTML, JSON)
- Comprehensive button interaction logic
- Enhanced JavaScript engine for modern web compatibility
- Google search compatibility with DuckDuckGo fallback
- Advanced CSS layout engine with Grid/Flexbox visualization
- High-performance asynchronous browser engine
- Intelligent caching system with SQLite backend
- Enhanced image handling and content filtering
- Complete module import filtering
- Natural redirect handling
- Client-side redirect support
- Form submission bug fixes
- API website compatibility
- Button navigation system

### Features
- Command-line interface with multiple commands
- Python SDK for programmatic access
- JavaScript execution with real browser environment simulation
- Modern web framework support (React, Vue, Angular)
- Network request handling with fetch API and WebSocket support
- Cookie management and persistent sessions
- Responsive design detection
- JSON API support with search capabilities

### Technical Improvements
- Fixed critical JavaScript engine errors
- Resolved form submission bugs
- Enhanced URL resolution for protocol-relative URLs
- Improved error handling and logging
- Dynamic content filtering with intelligent pattern recognition
- Separated interactive elements display
- Fixed Wikipedia rendering errors
- Enhanced search engine compatibility

## Future Releases

### Planned Features
- Headless browser integration for enhanced JavaScript support
- Advanced network simulation with Service Workers
- Progressive Web App (PWA) support
- Enhanced mobile device simulation
- Plugin system for extensibility
- Advanced debugging capabilities
- Performance monitoring dashboard
- Export functionality for browsing sessions