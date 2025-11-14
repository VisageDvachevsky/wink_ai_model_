# Hugging Face Integration

This service supports loading models from Hugging Face Hub.

## Configuration

### Environment Variables

- `ML_USE_HUGGINGFACE`: Enable Hugging Face integration (default: `false`)
- `ML_HUGGINGFACE_MODEL_ID`: Model ID from Hugging Face Hub (e.g., `username/model-name`)
- `ML_HUGGINGFACE_TOKEN`: Hugging Face API token (required for private models)
- `ML_MODELS_CACHE_DIR`: Directory for caching downloaded models (default: `./models_cache`)

### Local Development

For local testing without Hugging Face:

```bash
ML_USE_HUGGINGFACE=false
ML_MODEL_NAME=all-MiniLM-L6-v2
```

### Using Hugging Face Models

1. Upload your model to Hugging Face Hub
2. Set environment variables:

```bash
ML_USE_HUGGINGFACE=true
ML_HUGGINGFACE_MODEL_ID=your-username/your-model
ML_HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
```

3. Start the service - it will automatically download the model on first run

## CI/CD Integration

### GitHub Actions Setup

1. Add repository variables:
   - `USE_HUGGINGFACE`: Set to `true` to enable
   - `HUGGINGFACE_MODEL_ID`: Your model ID

2. Add repository secret:
   - `HUGGINGFACE_TOKEN`: Your Hugging Face API token

### Manual Model Download

```bash
export ML_HUGGINGFACE_MODEL_ID="username/model-name"
export ML_HUGGINGFACE_TOKEN="hf_xxxxx"
export ML_MODELS_CACHE_DIR="./models_cache"

python download_model.py
```

## Model Requirements

Models must be compatible with `sentence-transformers` library.
