# MCP Optimizer - Integration Examples

This directory contains comprehensive integration examples for the `mcp-optimizer` package available on PyPI.

## Installation

```bash
# Install the main package
pip install mcp-optimizer

# For running examples that require additional dependencies (streamlit, plotly, etc.)
pip install "mcp-optimizer[examples]"

# Or install additional dependencies manually
pip install streamlit plotly pandas numpy
```

## Available Integration Examples

### 🐍 Python Direct API
- **[python_direct_api.py](python_direct_api.py)** - Direct Python API usage
- **[async_optimization.py](async_optimization.py)** - Asynchronous optimization examples
- **[batch_processing.py](batch_processing.py)** - Batch optimization processing

### 🌐 Web Applications
- **[fastapi_integration.py](fastapi_integration.py)** - FastAPI web service
- **[streamlit_dashboard.py](streamlit_dashboard.py)** - Interactive Streamlit dashboard
- **[flask_webapp.py](flask_webapp.py)** - Flask web application

### 📊 Data Science & Analytics
- **[jupyter_notebook.ipynb](jupyter_notebook.ipynb)** - Jupyter notebook examples
- **[pandas_integration.py](pandas_integration.py)** - Pandas DataFrame integration
- **[numpy_optimization.py](numpy_optimization.py)** - NumPy array optimization

### 🔧 MCP Protocol Integration
- **[claude_desktop_config.json](claude_desktop_config.json)** - Claude Desktop configuration
- **[mcp_client_example.py](mcp_client_example.py)** - MCP client implementation
- **[mcp_server_wrapper.py](mcp_server_wrapper.py)** - Custom MCP server wrapper

### 🐳 Containerization & Deployment
- **[docker/](docker/)** - Docker containerization examples
- **[kubernetes/](kubernetes/)** - Kubernetes deployment manifests
- **[docker-compose.yml](docker-compose.yml)** - Docker Compose setup

### 📈 Monitoring & Observability
- **[prometheus_metrics.py](prometheus_metrics.py)** - Prometheus metrics integration
- **[logging_example.py](logging_example.py)** - Comprehensive logging setup
- **[health_checks.py](health_checks.py)** - Health monitoring

### 🔒 Security & Authentication
- **[auth_middleware.py](auth_middleware.py)** - Authentication middleware
- **[rate_limiting.py](rate_limiting.py)** - Rate limiting implementation
- **[secure_config.py](secure_config.py)** - Secure configuration management

## Quick Start

### 1. Basic Python Usage

```python
from mcp_optimizer import LinearProgrammingSolver

# Create solver instance
solver = LinearProgrammingSolver()

# Define optimization problem
result = solver.solve({
    "objective": {"coefficients": [3, 2], "direction": "maximize"},
    "constraints": [
        {"coefficients": [1, 1], "operator": "<=", "value": 4},
        {"coefficients": [2, 1], "operator": "<=", "value": 6}
    ],
    "bounds": [(0, None), (0, None)]
})

print(f"Optimal value: {result.objective_value}")
print(f"Solution: {result.variables}")
```

### 2. Web Service Integration

```python
from fastapi import FastAPI
from mcp_optimizer import OptimizationEngine

app = FastAPI()
optimizer = OptimizationEngine()

@app.post("/optimize")
async def optimize_problem(problem_data: dict):
    result = await optimizer.solve_async(problem_data)
    return {"status": "success", "result": result}
```

### 3. MCP Protocol Usage

```json
{
  "mcpServers": {
    "mcp-optimizer": {
      "command": "python",
      "args": ["-m", "mcp_optimizer.server"],
      "env": {
        "SOLVER_TIMEOUT": "300",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Features Demonstrated

### Core Optimization Capabilities
- ✅ Linear Programming
- ✅ Integer Programming
- ✅ Assignment Problems
- ✅ Transportation Problems
- ✅ Knapsack Problems
- ✅ Routing & Scheduling
- ✅ Portfolio Optimization

### Integration Patterns
- ✅ Synchronous and Asynchronous APIs
- ✅ Batch processing workflows
- ✅ Real-time optimization services
- ✅ Microservices architecture
- ✅ Event-driven processing
- ✅ Caching and performance optimization

### Production Features
- ✅ Error handling and validation
- ✅ Logging and monitoring
- ✅ Authentication and authorization
- ✅ Rate limiting and throttling
- ✅ Health checks and metrics
- ✅ Configuration management

## Performance Benchmarks

| Problem Type | Problem Size | Avg. Solve Time | Memory Usage |
|--------------|--------------|-----------------|--------------|
| Linear Programming | 1000 variables | 0.1s | 50MB |
| Assignment | 500x500 matrix | 0.5s | 100MB |
| Transportation | 100x100 | 0.2s | 75MB |
| Knapsack | 1000 items | 0.3s | 60MB |
| TSP | 50 cities | 2.0s | 200MB |

## Environment Variables

```bash
# Solver Configuration
SOLVER_TIMEOUT=300
MAX_ITERATIONS=10000
SOLVER_THREADS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
API_KEY_REQUIRED=true
RATE_LIMIT_PER_MINUTE=100

# Performance
CACHE_ENABLED=true
CACHE_TTL=3600
```

## Testing

Run all integration tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest examples/integration/tests/ -v

# Run with coverage
pytest examples/integration/tests/ --cov=mcp_optimizer
```

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure `mcp-optimizer` is installed
   ```bash
   pip install --upgrade mcp-optimizer
   ```

2. **Solver Timeout**: Increase timeout for large problems
   ```python
   solver.set_timeout(600)  # 10 minutes
   ```

3. **Memory Issues**: Use batch processing for large datasets
   ```python
   results = solver.solve_batch(problems, batch_size=10)
   ```

### Performance Optimization

1. **Enable Caching**:
   ```python
   solver.enable_cache(ttl=3600)
   ```

2. **Use Async for I/O-bound Operations**:
   ```python
   results = await solver.solve_async(problem)
   ```

3. **Parallel Processing**:
   ```python
   solver.set_parallel_threads(4)
   ```

## Contributing

To add new integration examples:

1. Create example file in appropriate subdirectory
2. Add comprehensive documentation
3. Include error handling and logging
4. Add tests in `tests/` directory
5. Update this README

## Usage Examples

### 1. Run FastAPI Service
```bash
cd examples/integration
uvicorn fastapi_integration:app --reload --port 8000
```

### 2. Launch Streamlit Dashboard
```bash
cd examples/integration
streamlit run streamlit_dashboard.py
```

### 3. Deploy with Docker
```bash
cd examples/integration
docker-compose up -d
```

### 4. Configure Claude Desktop
Copy `claude_desktop_config.json` to your Claude Desktop configuration directory.

## API Examples

### Linear Programming via HTTP
```bash
curl -X POST "http://localhost:8000/optimize/linear-programming" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": {"coefficients": [3, 2], "direction": "maximize"},
    "constraints": [
      {"coefficients": [1, 1], "operator": "<=", "value": 4},
      {"coefficients": [2, 1], "operator": "<=", "value": 6}
    ],
    "bounds": [[0, null], [0, null]]
  }'
```

### Python Direct API
```python
from mcp_optimizer import LinearProgrammingSolver

solver = LinearProgrammingSolver()
result = solver.solve({
    "objective": {"coefficients": [3, 2], "direction": "maximize"},
    "constraints": [
        {"coefficients": [1, 1], "operator": "<=", "value": 4}
    ],
    "bounds": [(0, None), (0, None)]
})
print(f"Optimal value: {result.objective_value}")
```

## Support

- 📧 Email: support@mcp-optimizer.com
- 🐛 Issues: [GitHub Issues](https://github.com/dmitryanchikov/mcp-optimizer/issues)
- 📖 Documentation: [Full Documentation](https://mcp-optimizer.readthedocs.io)
- 💬 Discord: [Community Server](https://discord.gg/mcp-optimizer) 