# GitHub Copilot Instructions for LogSentinelAI

## Project Overview

LogSentinelAI is an AI-powered log analysis tool that leverages Large Language Models (LLMs) to analyze various log formats (Apache HTTP access, Apache error, Linux system logs, TCPDump packets) for security threats, anomalies, and operational insights. The project transforms unstructured log data into structured JSON format for visualization in Elasticsearch and Kibana dashboards.

## Project Goals and Philosophy

- **Security & Operations-First**: Primary focus on detecting security threats (SQL injection, XSS, brute force attacks, network anomalies) and operational issues (system errors, malfunctions, potential problems)
- **AI-Driven**: Use LLMs (OpenAI, Ollama, vLLM) for intelligent log interpretation rather than traditional regex patterns
- **Structured Output**: Transform raw logs into standardized JSON with Pydantic validation
- **Enterprise-Ready**: Support for Elasticsearch integration, remote SSH monitoring, and production deployment
- **Flexibility**: Support multiple LLM providers and configurable sensitivity levels

## Repository Structure

- `/src/logsentinelai/`: Main source code
  - `/analyzers/`: Log type-specific analyzers (httpd_access.py, httpd_apache.py, linux_system.py, tcpdump_packet.py)
  - `/core/`: Core functionality (config.py, llm.py, elasticsearch.py, ssh.py, monitoring.py, prompts.py)
  - `/utils/`: Utility functions (geoip_downloader.py)
- `/sample-logs/`: Sample log files for testing different formats
- `/.github/`: GitHub workflow configurations, issue templates, and community health files
- `/img/`: Documentation images (dashboard examples)

## Technical Stack and Dependencies

- **Python**: 3.11+ with modern async/await patterns
- **LLM Integration**: OpenAI API, Ollama, vLLM support via outlines library
- **Data Validation**: Pydantic v2 for structured schema validation
- **Elasticsearch**: v9+ for data storage and search
- **SSH Connectivity**: Paramiko for remote log monitoring
- **GeoIP**: MaxMind GeoLite2 for IP geolocation
- **Configuration**: python-dotenv for environment management

## Coding Standards and Conventions

### Python Style
- Use Python 3.11+ features and type hints throughout
- Follow PEP 8 with line length of 120 characters
- Use async/await for I/O operations
- Prefer f-strings for string formatting
- Use dataclasses or Pydantic models for structured data

### Error Handling
- Use structured exception handling with specific exception types
- Log errors with appropriate severity levels
- Provide meaningful error messages for troubleshooting
- Gracefully handle LLM API failures and network issues

### Security Considerations
- Never hardcode credentials or API keys
- Use environment variables for sensitive configuration
- Validate all external inputs (log data, configurations)
- Implement proper SSH key validation for remote connections
- Follow principle of least privilege for Elasticsearch access

### Testing and Quality
- Include comprehensive error handling for production scenarios
- Validate Pydantic schemas thoroughly
- Test with various log formats and edge cases
- Consider LLM response variability in error handling

## Log Analysis Architecture

### Core Architecture Pattern
The project follows a **configuration-driven + shared libraries + simple analyzer classes** pattern:

1. **Configuration Foundation**: `config.template` centralizes all settings (LLM providers, API keys, parameters)
2. **Common Core Libraries**: `/core/commons.py` provides shared analysis logic and interfaces
3. **Simple Analyzer Classes**: Each log type analyzer is minimal, focusing only on:
   - Pydantic model definitions (schemas for SecurityEvent, Statistics, LogAnalysis)
   - Calling generic functions from `commons.py`

### Analyzer Pattern
Each analyzer (`httpd_access.py`, `httpd_apache.py`, `linux_system.py`, `tcpdump_packet.py`) follows this structure:
```python
# 1. Define Pydantic schemas
class SecurityEvent(BaseModel): ...
class LogAnalysis(BaseModel): ...

# 2. Simple main function calling commons
def main():
    run_generic_batch_analysis(
        log_type="httpd_access",
        analysis_schema_class=LogAnalysis,
        prompt_template=PROMPT_TEMPLATE_HTTPD_ACCESS_LOG
    )
```

### Core Library Responsibilities
- **`commons.py`**: Main analysis orchestration, batch/realtime processing
- **`llm.py`**: LLM provider abstraction and model initialization
- **`elasticsearch.py`**: Data storage and indexing
- **`geoip.py`**: IP geolocation enrichment
- **`prompts.py`**: Structured prompts for each log type
- **`ssh.py`**: Remote log access capabilities

### LLM Integration
- Use structured prompts in `/core/prompts.py`
- Implement retry logic for LLM API calls
- Support multiple providers with fallback mechanisms
- Validate LLM responses against Pydantic schemas using Outlines

### Data Pipeline
1. Log ingestion (file/SSH)
2. LLM analysis with structured prompts
3. Pydantic validation and transformation
4. GeoIP enrichment
5. Elasticsearch indexing

## Development Priorities

1. **Reliability**: Handle LLM inconsistencies and network failures gracefully
2. **Performance**: Efficient batch processing and real-time monitoring
3. **Extensibility**: Easy addition of new log formats and LLM providers
4. **Observability**: Comprehensive logging and monitoring capabilities
5. **Documentation**: Clear examples and troubleshooting guides

## Common Patterns to Follow

### Architecture Patterns
- **Configuration-Driven**: Use `config.template` for all configurable parameters
- **Shared Core Logic**: Leverage `commons.py` functions rather than duplicating analysis logic
- **Minimal Analyzer Classes**: Keep log type analyzers focused on schema definition and calling generic functions
- **Pydantic-First**: Define clear data models before implementation

### Implementation Patterns
- Use dependency injection for LLM providers and storage backends
- Implement proper resource cleanup (SSH connections, file handles)
- Use configuration classes with validation (Pydantic Settings)
- Follow async patterns for I/O-bound operations
- Implement proper logging with structured messages

### Adding New Log Types
When adding a new analyzer, follow this pattern:
1. Define Pydantic models for the log type's specific events and statistics
2. Create a prompt template in `/core/prompts.py`
3. Use `run_generic_batch_analysis()` or `run_generic_realtime_analysis()` from commons
4. Test with sample logs in `/sample-logs/`

## AI/LLM Specific Guidelines

- Design prompts for consistency and reliability across different LLM models
- Implement schema validation to handle LLM response variations
- Use temperature settings appropriate for analytical tasks (typically low)
- Consider token limits and cost optimization
- Implement fallback strategies for LLM failures
