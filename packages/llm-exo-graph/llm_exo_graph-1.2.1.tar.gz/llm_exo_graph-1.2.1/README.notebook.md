# 🎓 KG Engine v2 - Notebook Environment

Docker Compose setup for running Knowledge Graph Engine v2 with Neo4j and Ollama (local LLM) - optimized for notebook/development environments.

## 🚀 Quick Start

### 1. Start Services
```bash
# Start Neo4j + Ollama with lightweight model
docker-compose -f docker-compose.notebook.yml up -d

# Check services are running
docker-compose -f docker-compose.notebook.yml ps
```

### 2. Wait for Model Download
```bash
# Monitor model download progress
docker logs -f kg-ollama-init

# Should see: "Model phi3:mini ready for use!"
```

### 3. Test Environment
```bash
# Copy environment file
cp .env.notebook .env

# Test the setup
python examples/notebook_test.py

# Run demo
python examples/notebook_test.py --demo
```

### 4. Start Jupyter (Optional)
```bash
# Install jupyter if not already installed
pip install jupyter notebook

# Start notebook server
jupyter notebook notebooks/
```

## 📊 Included Services

### Neo4j Database
- **Port**: 7474 (HTTP), 7687 (Bolt)
- **Credentials**: neo4j/password
- **Web UI**: http://localhost:7474
- **Features**: APOC plugins enabled

### Ollama LLM Server  
- **Port**: 11434
- **Model**: phi3:mini (2.3GB) - recommended for notebooks
- **API**: http://localhost:11434
- **Alternative models available** (see below)

## 🤖 Model Options

The setup uses **phi3:mini** by default - the best balance for notebook environments:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **phi3:mini** | 2.3GB | Fast | Good | **Recommended - balanced** |
| llama3.2:1b | 1.3GB | Fastest | Basic | Limited resources |
| qwen2.5:1.5b | 1.5GB | Fast | Good | JSON parsing |
| gemma2:2b | 1.6GB | Medium | Good | Google reliability |

### Change Model
```bash
# Pull different model
docker exec kg-ollama ollama pull llama3.2:1b

# Update .env.notebook
OPENAI_MODEL=llama3.2:1b

# Restart your notebooks/scripts
```

## 💻 Development Environment

### Using the Development Container
```bash
# Start with development container
docker-compose -f docker-compose.notebook.yml --profile dev up -d

# Access development environment
docker exec -it kg-engine-dev bash

# Inside container:
python examples/notebook_test.py --demo
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser
```

### Local Development
```bash
# Install dependencies
pip install -e .
pip install jupyter notebook python-dotenv

# Set environment
export $(cat .env.notebook | xargs)

# Test
python examples/notebook_test.py
```

## 📚 Tutorial Notebook

Open [`notebooks/kg_engine_tutorial.ipynb`](notebooks/kg_engine_tutorial.ipynb) for a comprehensive tutorial covering:

1. **Setup & Configuration** - Environment verification
2. **Basic Usage** - Adding knowledge from text
3. **Search & Query** - Natural language queries  
4. **Advanced Features** - Entity exploration, statistics
5. **Conflict Resolution** - Temporal tracking demo
6. **Performance Testing** - Speed benchmarks

## 🔧 Configuration

### Environment Variables (.env.notebook)
```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Ollama 
OPENAI_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=phi3:mini

# Performance
KG_CACHE_TTL=300
KG_MAX_BATCH_SIZE=50
```

### Custom Neo4j Configuration
Edit `docker-compose.notebook.yml`:
```yaml
neo4j:
  environment:
    - NEO4J_AUTH=neo4j/your-password
    - NEO4J_dbms_memory_heap_initial__size=1G
    - NEO4J_dbms_memory_heap_max__size=2G
```

## 🧪 Testing LLM Tasks

The setup is optimized for the LLM interface tasks:

### 1. Entity & Relationship Extraction
```python
items = [InputItem("Alice works as a senior engineer at Google")]
results = engine.process_input(items)
# Tests: JSON parsing, entity extraction, relationship identification
```

### 2. Query Parsing
```python
response = engine.search("Who works at Google?")
# Tests: Natural language understanding, query structuring
```

### 3. Answer Generation  
```python
print(response.answer)
# Tests: Context understanding, natural language generation
```

### 4. Category Classification
```python
# Automatic via graph standardizer
# Tests: Semantic classification, category inference
```

## 📈 Performance Expectations

With **phi3:mini** on typical notebook hardware:

| Operation | Time | Notes |
|-----------|------|-------|
| Model Loading | 30-60s | First startup only |
| Entity Extraction | 2-5s | Per text item |
| Search Query | 1-3s | Including answer generation |
| Graph Operations | <100ms | Neo4j operations |

## 🛠️ Troubleshooting

### Services Not Starting
```bash
# Check Docker resources
docker system df

# Clean up if needed
docker system prune

# Restart services
docker-compose -f docker-compose.notebook.yml down
docker-compose -f docker-compose.notebook.yml up -d
```

### Model Download Issues
```bash
# Check Ollama logs
docker logs kg-ollama

# Manual model pull
docker exec kg-ollama ollama pull phi3:mini

# List available models
docker exec kg-ollama ollama list
```

### Performance Issues
```bash
# Check system resources
docker stats

# Use smaller model
OPENAI_MODEL=llama3.2:1b

# Reduce batch size
KG_MAX_BATCH_SIZE=25
```

### Connection Issues
```bash
# Test Neo4j connection
curl http://localhost:7474

# Test Ollama connection  
curl http://localhost:11434/api/tags

# Check networking
docker network ls
docker network inspect llama_neo4j_demo_kg-network
```

## 🔄 Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.notebook.yml down

# Stop and remove volumes (⚠️ deletes data)
docker-compose -f docker-compose.notebook.yml down -v

# Stop specific service
docker-compose -f docker-compose.notebook.yml stop neo4j
```

## 📊 Resource Usage

**Minimum Requirements**:
- RAM: 8GB (4GB for models + 2GB for Neo4j + 2GB for system)
- Disk: 5GB (models + Neo4j data)
- CPU: 4 cores recommended

**Storage Breakdown**:
- phi3:mini model: ~2.3GB
- Neo4j data: ~100MB (grows with usage)
- Docker images: ~2GB total

## 🎯 Next Steps

1. **Explore the Tutorial**: [`notebooks/kg_engine_tutorial.ipynb`](notebooks/kg_engine_tutorial.ipynb)
2. **Try Different Models**: Experiment with model sizes vs performance
3. **Scale Up**: Move to OpenAI GPT models for production
4. **Integrate**: Use as library in your own projects

## 📞 Support

- **Issues**: Check logs with `docker logs <container-name>`
- **Performance**: Try smaller models or increase Docker resources
- **Development**: Use the dev container for debugging
- **Production**: See main README.md for production deployment options

---

**Happy Knowledge Graphing! 🎉**