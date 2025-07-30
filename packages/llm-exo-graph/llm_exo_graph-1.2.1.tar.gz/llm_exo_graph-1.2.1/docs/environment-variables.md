# Environment Variables Guide

Complete guide to environment variables for Knowledge Graph Engine v2.

## LLM Configuration

### Provider Selection

The system automatically detects the LLM provider based on environment variables:

```bash
# Explicit provider selection (recommended)
LLM_PROVIDER=openai    # or: ollama, litellm
```

**Auto-detection priority:**
1. `LLM_PROVIDER` if explicitly set
2. `LITELLM_BEARER_TOKEN` present → LiteLLM
3. `OLLAMA_BASE_URL` or `OPENAI_API_KEY=ollama` → Ollama  
4. `OPENAI_API_KEY` present → OpenAI
5. Error if none found

### OpenAI Configuration

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
OPENAI_MODEL=gpt-4o-mini                    # Default: gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1   # Default: official API
OPENAI_ORGANIZATION=your-org-id             # Optional org ID
```

**Recommended models:**
- `gpt-4o-mini`: Fast, cost-effective, production ready
- `gpt-4o`: Most capable, higher cost
- `gpt-3.5-turbo`: Legacy, still supported

### Ollama Configuration

```bash
# Provider selection
LLM_PROVIDER=ollama

# Configuration
OLLAMA_MODEL=llama3.2:3b                    # Default: llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434/v1   # Default: localhost

# Legacy compatibility
LLM_BASE_URL=http://localhost:11434/v1      # Still supported
OPENAI_API_KEY=ollama                       # Legacy pattern
OPENAI_MODEL=phi3:mini                      # Will map to OLLAMA_MODEL
```

**Recommended models:**
- `phi3:mini` (2.3GB): Best balance for notebooks
- `llama3.2:1b` (1.3GB): Smallest, basic tasks
- `llama3.2:3b` (2GB): Good performance
- `qwen2.5:1.5b` (1.5GB): Excellent JSON parsing

### LiteLLM Configuration

```bash
# Provider selection  
LLM_PROVIDER=litellm

# Required
LITELLM_BEARER_TOKEN=your-bearer-token
LITELLM_BASE_URL=https://your-endpoint.com/v1
LITELLM_MODEL=gpt-4o

# Optional
LITELLM_ADDITIONAL_HEADERS={"X-Custom-Header": "value"}
```

## Neo4j Configuration

```bash
# Required
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Optional
NEO4J_DATABASE=neo4j                        # Default: neo4j
```

**Connection types:**
- Local: `bolt://localhost:7687`
- Aura Cloud: `neo4j+s://your-id.databases.neo4j.io`
- Docker: `bolt://neo4j-container:7687`

## Performance Settings

```bash
# Caching
KG_CACHE_TTL=300                           # Cache TTL in seconds

# Batch processing
KG_MAX_BATCH_SIZE=50                       # Max items per batch

# Memory management
PYTHONUNBUFFERED=1                         # Disable Python buffering
```

## Application Settings

```bash
# Logging
LOG_LEVEL=INFO                             # DEBUG, INFO, WARNING, ERROR

# Development
PYTHONPATH=./src                           # Python path for imports
```

## API Server Specific

```bash
# Server configuration
API_HOST=0.0.0.0                          # Bind address
API_PORT=8080                              # Port number

# Security (production)
SECRET_KEY=your-secret-key                 # Session encryption
ALLOWED_ORIGINS=http://localhost:3000      # CORS origins
```

## Environment File Examples

### Development (.env)
```bash
# Core configuration
LLM_PROVIDER=ollama
OLLAMA_MODEL=phi3:mini
OLLAMA_BASE_URL=http://localhost:11434/v1

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Development settings
LOG_LEVEL=DEBUG
PYTHONPATH=./src
PYTHONUNBUFFERED=1
```

### Production (.env)
```bash
# Core configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your-production-key
OPENAI_MODEL=gpt-4o-mini

NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-secure-password

# Performance optimization
KG_CACHE_TTL=600
KG_MAX_BATCH_SIZE=100

# Production settings
LOG_LEVEL=INFO
```

### Notebook (.env.notebook)
```bash
# Optimized for Jupyter notebooks
LLM_PROVIDER=ollama
OLLAMA_MODEL=phi3:mini
OLLAMA_BASE_URL=http://localhost:11434/v1

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Notebook-optimized settings
KG_CACHE_TTL=300
KG_MAX_BATCH_SIZE=25
LOG_LEVEL=INFO
```

## Migration from Legacy Configuration

### Old Pattern
```bash
# Legacy (still works)
OPENAI_API_KEY=ollama
OPENAI_MODEL=phi3:mini
LLM_BASE_URL=http://localhost:11434/v1
```

### New Pattern
```bash
# Modern (recommended)
LLM_PROVIDER=ollama
OLLAMA_MODEL=phi3:mini
OLLAMA_BASE_URL=http://localhost:11434/v1
```

## Testing Configuration

```bash
# Test environment detection
export LLM_PROVIDER=ollama
python -c "from kg_engine import LLMClientFactory; print(LLMClientFactory.create_from_env().provider)"

# Test full initialization
python -c "from kg_engine import KnowledgeGraphEngineV2; engine = KnowledgeGraphEngineV2(); print('✅ Success')"
```

## Common Issues

### 1. Provider Not Detected
```bash
# Problem: No LLM configuration found
# Solution: Set explicit provider
export LLM_PROVIDER=ollama
```

### 2. Model Not Found
```bash
# Problem: Ollama model not available
# Solution: Pull the model first
ollama pull phi3:mini
```

### 3. Connection Failed
```bash
# Problem: Neo4j connection refused
# Solution: Check service and credentials
docker ps | grep neo4j
```

### 4. Legacy Variables
```bash
# Problem: Mixed old/new environment variables
# Solution: Use consistent pattern
unset OPENAI_API_KEY OPENAI_MODEL LLM_BASE_URL
export LLM_PROVIDER=ollama OLLAMA_MODEL=phi3:mini
```

## Environment File Loading

The system loads environment variables in this order:

1. System environment variables
2. `.env` file in current directory
3. `.env.local` file (if present)
4. Docker environment variables (if containerized)

**Priority**: System environment > `.env` files

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use `.env` files** for local development
3. **Use secrets management** in production
4. **Rotate credentials** regularly
5. **Use environment-specific files** (.env.dev, .env.prod)

---

**Last Updated**: Current version  
**Compatibility**: All KG Engine v2 components  
**Migration**: Fully backward compatible