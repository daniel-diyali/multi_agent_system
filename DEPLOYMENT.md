# Deployment Guide

## Quick Start (Local Development)

```bash
# 1. Clone and setup
git clone https://github.com/daniel-diyali/multi_agent_system.git
cd multi_agent_system

# 2. Environment setup
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start vector database
docker-compose up -d

# 5. Run the demo
streamlit run ui/app.py
```

## Production Deployment

### Option 1: Docker (Recommended)

```bash
# Build image
docker build -t multi-agent-system .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  multi-agent-system
```

### Option 2: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Option 3: Vercel (Serverless)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM calls |
| `LANGCHAIN_API_KEY` | No | LangSmith tracing (optional) |
| `CHROMA_PERSIST_DIRECTORY` | No | Vector DB storage path |

## API Endpoints

- `POST /chat` - Main customer service endpoint
- `GET /conversation/{user_id}` - Get conversation history
- `POST /evaluate` - Run system evaluation
- `GET /health` - Health check
- `GET /docs` - API documentation

## Performance Tuning

### Vector Database Optimization
```python
# Increase chunk overlap for better context
chunk_overlap = 100  # Default: 50

# Adjust retrieval count
k = 5  # Default: 3
```

### Response Caching
```python
# Add Redis for conversation caching
REDIS_URL = "redis://localhost:6379"
```

### Load Balancing
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    image: multi-agent-system
    replicas: 3
    ports:
      - "8000-8002:8000"
```

## Monitoring

### Health Checks
```bash
curl http://localhost:8000/health
```

### Evaluation Metrics
```bash
curl -X POST http://localhost:8000/evaluate
```

### Logs
```bash
docker logs multi-agent-system
```

## Scaling Considerations

1. **Stateless Design**: Conversation memory uses in-memory storage
2. **Database**: Consider PostgreSQL for production conversation storage
3. **Caching**: Add Redis for frequently accessed data
4. **Load Balancing**: Use nginx or cloud load balancers
5. **Monitoring**: Implement Prometheus + Grafana for metrics