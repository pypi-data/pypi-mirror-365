# Changelog

All notable changes to KayGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- MCP (Model Context Protocol) integration for standardized tool calling
- Graph visualization tools (Mermaid, DOT, ASCII, HTML)
- Voice chat example with STT/TTS integration
- Majority vote pattern for LLM consensus
- Basic async tutorial for beginners
- Human-in-the-loop (HITL) workflows
- Real-time monitoring example
- Comprehensive release documentation
- GitHub Actions CI/CD workflows
- Docker support with multi-stage builds

### Changed
- Updated CLAUDE.md with complete framework documentation
- Enhanced project structure with new examples

### Fixed
- None yet

## [0.1.3] - 2025-01-29

### Added
- Real-time monitoring capabilities with MonitoringNode
- Production-ready API example with FastAPI integration
- Fault-tolerant workflow patterns
- Parallel batch processing examples
- Chat memory management patterns

### Changed
- Improved error handling in async nodes
- Enhanced retry mechanisms

### Fixed
- Memory leak in batch processing
- Race condition in parallel execution

## [0.1.2] - 2025-01-15

### Added
- AsyncGraph and AsyncNode for non-blocking operations
- ValidatedNode for input/output validation
- MetricsNode for execution tracking
- Context manager support in BaseNode

### Changed
- Improved node lifecycle with hooks
- Better error propagation

### Fixed
- Thread safety issues with node reuse

## [0.1.1] - 2025-01-01

### Added
- Basic Node and Graph abstractions
- BatchNode for processing iterables
- Simple workflow examples

### Changed
- Initial release

## [0.1.0] - 2024-12-15

### Added
- Initial framework design
- Core abstractions
- Basic documentation

[Unreleased]: https://github.com/yourusername/kaygraph/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/yourusername/kaygraph/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/yourusername/kaygraph/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/yourusername/kaygraph/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yourusername/kaygraph/releases/tag/v0.1.0