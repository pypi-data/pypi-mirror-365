# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KayGraph is an opinionated framework for building context-aware AI applications with production-ready graphs. The core abstraction is **Context Graph + Shared Store**, where Nodes handle operations (including LLM calls) and Graphs connect nodes through Actions (labeled edges) to create sophisticated workflows.

## Development Commands

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_graph_basic.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=kaygraph tests/

# Run async tests
pytest tests/test_async.py -v
```

### Installation
```bash
# Install the framework
pip install kaygraph

# Or install from source for custom modifications
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Using uv (recommended)
uv pip install kaygraph
```

### Linting and Code Quality
```bash
# Run ruff linter
ruff check kaygraph/

# Fix linting issues automatically
ruff check --fix kaygraph/

# Format code (ruff also formats)
ruff format kaygraph/
```

## Architecture & Key Components

### Core Framework (`/kaygraph/__init__.py`)
The framework provides these opinionated abstractions:
- **BaseNode**: Foundation with 3-step lifecycle: `prep()` → `exec()` → `post()`
  - Includes hooks: `before_prep()`, `after_exec()`, `on_error()`
  - Context manager support for resource management
  - Execution context storage per node
- **Node**: Standard node with retry and fallback capabilities
  - `max_retries` and `wait` parameters for resilience
  - `exec_fallback()` for graceful degradation
- **Graph**: Orchestrates node execution through Actions
  - Supports operator overloading: `>>` for default, `-` for named actions
  - Copy nodes before execution for thread safety
- **BatchNode/Graph**: Process iterables of items
  - `prep()` returns iterable, `exec()` called per item
- **AsyncNode/Graph**: Asynchronous versions for I/O operations
  - Replace methods with `_async` versions
  - `run_async()` for standalone execution
- **ParallelBatchNode/Graph**: Concurrent execution using ThreadPoolExecutor
- **ValidatedNode**: Input/output validation with custom validators
- **MetricsNode**: Execution metrics collection
  - Tracks execution times, retry counts, success/error rates
  - `get_stats()` for comprehensive metrics

### Node Design Principles
1. **prep(shared)**: Read from shared store, prepare data for execution
   - Access shared context to gather required data
   - Return data needed for exec phase
   - Should be lightweight and fast
2. **exec(prep_res)**: Execute compute logic (LLM calls, APIs) - NO shared access
   - Pure function that processes prep_res
   - Can be retried independently
   - Should be idempotent when retries are enabled
3. **post(shared, prep_res, exec_res)**: Write to shared store, return next action
   - Update shared context with results
   - Return action string for next node or None for default
   - Nodes for conditional branching MUST return specific action strings

### Shared Store Design
- Use dictionary for simple systems: `shared = {"key": value}`
- Params are for identifiers, Shared Store is for data
- Don't repeat data - use references or foreign keys

## Agentic Coding Workgraph

When implementing a KayGraph application:

1. **Start Simple**: Begin with minimal implementation and iterate
2. **Design First**: Create `docs/design.md` with:
   - High-level requirements
   - Graph structure (mermaid diagram)
   - Node descriptions (one-line each)
   - Utility functions needed
3. **Project Structure**:
   ```
   my_project/
   ├── main.py          # Entry point
   ├── nodes.py         # Node definitions
   ├── graph.py         # Graph creation
   ├── utils/           # Utility functions
   │   ├── call_llm.py
   │   └── search_web.py
   ├── requirements.txt
   └── docs/
       └── design.md    # High-level design
   ```

## Implementation Guidelines

### Node Implementation
```python
class MyNode(Node):
    def prep(self, shared):
        # Read from shared store
        return shared.get("input_data")
    
    def exec(self, prep_res):
        # Process data (LLM calls, etc)
        # This should be idempotent if retries enabled
        return process_data(prep_res)
    
    def post(self, shared, prep_res, exec_res):
        # Write results to shared store
        shared["output_data"] = exec_res
        return "next_action"  # or None for "default"
```

### Graph Connection
```python
# Connect nodes with default action
node1 >> node2 >> node3

# Connect with named actions
node1 >> ("success", node2)
node1 >> ("error", error_handler)
```

### Utility Functions
- One file per external API (`utils/call_llm.py`, `utils/search_web.py`)
- Include `if __name__ == "__main__"` test in each utility
- Document input/output and necessity
- NO vendor lock-in - implement your own wrappers

## Best Practices

1. **FAIL FAST**: Avoid try/except in initial implementation
2. **No Complex Features**: Keep it simple, no full type checking
3. **Extensive Logging**: Add logging throughout for debugging
4. **Separation of Concerns**: Data storage (shared) vs processing (nodes)
5. **Idempotent exec()**: Required when using retries
6. **Test Utilities**: Each utility should have a simple test

## Common Patterns

- **Agent**: Autonomous decision-making with context and actions
- **Workgraph**: Chain multiple tasks in sequence
- **RAG**: Offline indexing graph + online retrieval graph
- **MapReduce**: Split data processing into map and reduce steps
- **Multi-Agent**: Coordinate multiple agents with shared state
- **Real-time Monitoring**: MonitoringNode base class for observability
- **Fault-tolerant Workflows**: Retry mechanisms with circuit breakers
- **Streaming Processing**: AsyncNode with generator patterns
- **Validated Pipelines**: Input/output validation at each stage

## Documentation References

When implementing, consult `.cursor/rules/` for detailed patterns:
- Core abstractions: `node.mdc`, `graph.mdc`, `communication.mdc`
- Design patterns: `agent.mdc`, `rag.mdc`, `mapreduce.mdc`
- Utilities: `llm.mdc`, `embedding.mdc`, `vector.mdc`

## Example Projects

The `workbooks/` directory contains comprehensive examples:
- `kaygraph-hello-world/`: Basic workflow patterns
- `kaygraph-agent/`: Autonomous AI agent implementation
- `kaygraph-rag/`: Complete RAG pipeline with indexing and retrieval
- `kaygraph-chat-memory/`: Conversational AI with memory management
- `kaygraph-parallel-batch/`: High-performance batch processing
- `kaygraph-fault-tolerant-workflow/`: Production error handling
- `kaygraph-realtime-monitoring/`: Real-time observability system
- `kaygraph-production-ready-api/`: FastAPI integration with monitoring

## Important Notes

- The framework has ZERO dependencies - only Python standard library
- All utility functions (LLM calls, embeddings, etc.) must be implemented by you
- When humans can't specify the graph, AI agents can't automate it
- Node instances are copied before execution for thread safety
- Use `--` operator to log graph structure during development
- Conditional nodes must explicitly return action strings from `post()`
- Default transitions (>>) expect `post()` to return None

## Testing Strategy

- Unit tests for individual nodes in isolation
- Integration tests for complete workflows
- Use mock shared stores to test node behavior
- Test both success and failure paths
- Verify retry and fallback mechanisms
- Check async node behavior with pytest-asyncio