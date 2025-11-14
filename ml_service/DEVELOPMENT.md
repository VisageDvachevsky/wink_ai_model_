# ML Service Development Guide

## Working with Models

### Option 1: Using Hugging Face Hub (Recommended for production)

#### 1. Train and Upload Model

```bash
# Train your model locally
python train_model.py

# Upload to Hugging Face
huggingface-cli login
huggingface-cli upload your-org/movie-rating-model-v2 ./model_output
```

#### 2. Update Configuration

**Using environment variables (`.env` file):**
```bash
ML_USE_HUGGINGFACE=true
ML_HUGGINGFACE_MODEL_ID=your-org/movie-rating-model-v2
ML_HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
ML_MODEL_VERSION=v2.0
```

**Or update `ml_service/app/config.py`:**
```python
model_version: str = "v2.0"
huggingface_model_id: str = "your-org/movie-rating-model-v2"
use_huggingface: bool = True
```

#### 3. Deploy

Push to GitHub - CI/CD will:
- Download model from Hugging Face
- Build Docker image with tag `v2.0`
- Push to GitHub Container Registry

#### 4. Use Specific Version in Docker Compose

```yaml
ml-service:
  image: ghcr.io/visagedvachevsky/wink-ai-model/ml-service:v2.0
```

### Option 2: Local Model Testing

For testing models locally without Hugging Face:

#### 1. Place Model Files

```bash
mkdir -p ml_service/models/my-model
cp -r /path/to/trained/model/* ml_service/models/my-model/
```

#### 2. Update Docker Compose

Add volume mount in `infra/docker/compose.dev.yml`:

```yaml
ml-service:
  volumes:
    - ../../ml_service/app:/app/app
    - ../../ml_service/models:/app/models  # Add this line
```

#### 3. Update Configuration

```bash
ML_USE_HUGGINGFACE=false
ML_MODEL_NAME=/app/models/my-model
ML_MODELS_CACHE_DIR=/app/models
```

#### 4. Start Service

```bash
cd infra/docker
docker-compose -f compose.dev.yml up ml-service
```

### Option 3: Local Cache with Hugging Face

Models are automatically cached in `models_cache/` directory:

```bash
ML_USE_HUGGINGFACE=true
ML_HUGGINGFACE_MODEL_ID=your-org/model
ML_MODELS_CACHE_DIR=./models_cache
```

First run downloads the model, subsequent runs use cached version.

## Testing Changes Locally

### 1. Build and Run

```bash
cd infra/docker
docker-compose -f compose.dev.yml up --build ml-service
```

### 2. Test API

```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "INT. DARK ROOM - NIGHT\nA man shoots another man.", "script_id": "test"}'
```

### 3. Check Metrics

```bash
curl http://localhost:8001/metrics
```

## CI/CD Configuration

### GitHub Repository Variables

Set these in repository settings (Settings > Secrets and variables > Actions):

**Variables:**
- `USE_HUGGINGFACE`: `true` or `false`
- `HUGGINGFACE_MODEL_ID`: `your-org/model-name`

**Secrets:**
- `HUGGINGFACE_TOKEN`: Your Hugging Face API token

### Workflow Behavior

When `USE_HUGGINGFACE=true`:
- CI downloads model before building Docker image
- Model is included in the image
- No need to download at runtime

When `USE_HUGGINGFACE=false`:
- Image uses default model (all-MiniLM-L6-v2)
- Or configure custom model via environment variables

## Model Version Management

### Semantic Versioning

Use semantic versioning for models:
- `v1.0.0` - Initial model
- `v1.1.0` - Improved features, backward compatible
- `v2.0.0` - Breaking changes

### Tagging Docker Images

CI automatically tags images:
- `latest` - Latest build from main branch
- `v2.0` - Specific version tag
- `sha-abc123` - Git commit SHA

### Rollback

To rollback to previous version:

```yaml
ml-service:
  image: ghcr.io/visagedvachevsky/wink-ai-model/ml-service:v1.0
```

## Development Workflow

### 1. Local Development

```bash
# Edit model code
vim app/pipeline.py

# Test locally
docker-compose -f compose.dev.yml up --build ml-service

# Check logs
docker-compose -f compose.dev.yml logs -f ml-service
```

### 2. Train New Model

```bash
# Train model
python train_model.py --output ./model_output

# Test locally
ML_USE_HUGGINGFACE=false ML_MODEL_NAME=./model_output python -m app.main

# Upload to Hugging Face
huggingface-cli upload your-org/model-v2 ./model_output
```

### 3. Deploy

```bash
# Update version in config.py or .env
# Commit and push
git add .
git commit -m "Update model to v2.0"
git push origin develop

# Create PR to main
gh pr create --title "Model v2.0" --body "New model version"
```

## Monitoring

### Prometheus Metrics

Available at `http://localhost:9090` or `http://nginx/metrics/ml`

Key metrics:
- `ml_inference_latency_seconds` - Inference time
- `ml_requests_total` - Request count
- `ml_inference_errors_total` - Error count
- `ml_avg_violence_score` - Average violence score

### Grafana Dashboards

Available at `http://localhost:3000` (admin/admin)

Pre-configured dashboards show:
- Request rates
- Latency percentiles
- Error rates
- Feature score distributions

### Logs with Loki

View logs in Grafana:
1. Go to Explore
2. Select Loki datasource
3. Query: `{job="ml_service"}`
