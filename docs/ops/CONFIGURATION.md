# Configuration & Environment Variables

This document describes the configuration system, environment variables, and validation behavior for the AI Decision Traceability Engine.

## Overview

The application uses Pydantic Settings for strongly-validated configuration management. Configuration is loaded from environment variables (with optional `.env` file support) and validated based on the deployment environment.

## Environment Variables

### Required Variables

#### `ENV`
- **Type**: `"local"` | `"prod"`
- **Default**: `"local"`
- **Description**: Deployment environment identifier
- **Behavior**:
  - `local`: Development mode with relaxed validation
  - `prod`: Production mode with strict validation

#### `OPENAI_MODEL`
- **Type**: String
- **Default**: `""` (empty)
- **Required**: Always
- **Description**: Model name/identifier for the LLM provider
- **Examples**: `"llama3.2"`, `"gpt-4o-mini"`, `"gpt-4"`

### Optional Variables

#### `LLM_PROVIDER`
- **Type**: `"openai"` | `"ollama"` | `"lmstudio"`
- **Default**: `"ollama"`
- **Description**: LLM provider type
- **Behavior**:
  - `openai`: Use OpenAI API (requires `OPENAI_API_KEY` in production)
  - `ollama`: Use local Ollama server (default base URL: `http://localhost:11434/v1`)
  - `lmstudio`: Use local LM Studio server (default base URL: `http://localhost:1234/v1`)

#### `OPENAI_API_KEY`
- **Type**: String
- **Default**: `""` (empty)
- **Required**: 
  - **Local**: Optional (allowed to be empty)
  - **Production**: Required when `LLM_PROVIDER=openai`
- **Description**: API key for LLM provider
- **Security**: Never logged or exposed in error messages

#### `OPENAI_BASE_URL`
- **Type**: String (URL)
- **Default**: `""` (empty)
- **Description**: Base URL for LLM API
- **Behavior**:
  - Empty for OpenAI API (uses default OpenAI endpoint)
  - Set for local models (e.g., `http://localhost:11434/v1` for Ollama)
  - If not set and provider is `ollama` or `lmstudio`, uses default localhost URLs

#### `LOG_LEVEL`
- **Type**: String
- **Default**: `"INFO"`
- **Description**: Logging verbosity level
- **Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

#### `MAX_REQUEST_SIZE`
- **Type**: Integer (bytes)
- **Default**: `1048576` (1MB)
- **Description**: Maximum allowed request body size in bytes
- **Usage**: Requests exceeding this size are rejected with HTTP 413

## Environment Behavior

### Local Environment (`ENV=local`)

In local mode, the application:
- **Allows missing API keys** with friendly warnings
- **Logs configuration issues** as warnings (non-fatal)
- **Starts normally** even with incomplete configuration
- **Provides helpful error messages** when runtime issues occur

**Example Local Configuration:**
```bash
ENV=local
LLM_PROVIDER=ollama
OPENAI_MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_API_KEY can be empty for local models
LOG_LEVEL=INFO
```

### Production Environment (`ENV=prod`)

In production mode, the application:
- **Validates all required settings** on startup
- **Fails fast** with clear error messages if configuration is invalid
- **Requires API keys** when using OpenAI provider
- **Prevents silent misconfigurations** that could cause runtime failures

**Example Production Configuration:**
```bash
ENV=prod
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...  # Required for OpenAI
# OPENAI_BASE_URL should be empty for OpenAI
LOG_LEVEL=INFO
MAX_REQUEST_SIZE=1048576
```

## Configuration File (.env)

You can create a `.env` file in the project root to set environment variables. The file is automatically loaded by Pydantic Settings.

**Example .env file (safe template, no secrets):**
```bash
# Deployment Environment
ENV=local

# LLM Configuration
LLM_PROVIDER=ollama
OPENAI_MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_API_KEY=  # Leave empty for local models, or set your key

# Application Settings
LOG_LEVEL=INFO
MAX_REQUEST_SIZE=1048576
```

**Important Security Notes:**
- Never commit `.env` files with real API keys to version control
- Use environment variables or secret management systems in production
- The `.env` file should be listed in `.gitignore`

## Startup Validation

The application validates configuration on startup and logs a summary (without exposing secrets):

```
============================================================
AI Decision Traceability Engine - Startup Configuration
============================================================
Environment: local
LLM Provider: ollama
Model: llama3.2
Base URL: http://localhost:11434/v1
API Key: ***configured***  (or "(not set)")
Log Level: INFO
Max Request Size: 1048576 bytes
============================================================
```

### Validation Rules

1. **LLM Provider Validation**
   - Must be one of: `openai`, `ollama`, `lmstudio`
   - Invalid values cause immediate failure

2. **Production API Key Validation**
   - If `ENV=prod` and `LLM_PROVIDER=openai`, `OPENAI_API_KEY` must be set and non-empty
   - Failure results in application startup failure with clear error message

3. **Model Name Validation**
   - `OPENAI_MODEL` must be set (non-empty) in production
   - In local, missing model name will cause runtime errors when agents are invoked

## Common Misconfigurations

### Error: "OPENAI_API_KEY is required in production when LLM_PROVIDER=openai"

**Cause**: Production environment requires API key for OpenAI provider.

**Solution**:
- Set `OPENAI_API_KEY` in your environment or `.env` file
- Or switch to a local provider (`LLM_PROVIDER=ollama` or `LLM_PROVIDER=lmstudio`)

### Error: "Invalid LLM_PROVIDER: 'xyz'. Must be one of: openai, ollama, lmstudio"

**Cause**: Invalid provider value specified.

**Solution**:
- Use one of the valid values: `openai`, `ollama`, or `lmstudio`
- Check for typos or case sensitivity issues

### Error: "OPENAI_MODEL is required"

**Cause**: Model name not specified.

**Solution**:
- Set `OPENAI_MODEL` to a valid model name (e.g., `llama3.2`, `gpt-4o-mini`)

### Warning: "Configuration issue (non-fatal in local): ..."

**Cause**: Configuration issue detected in local environment.

**Solution**:
- Review the warning message and fix the configuration
- In local, these are warnings only; the app will start but may fail at runtime

## Provider-Specific Configuration

### OpenAI Provider

```bash
ENV=prod
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-key-here
# OPENAI_BASE_URL should be empty (uses default OpenAI endpoint)
```

### Ollama Provider

```bash
ENV=local
LLM_PROVIDER=ollama
OPENAI_MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_API_KEY can be empty
```

**Note**: Ensure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3.2`).

### LM Studio Provider

```bash
ENV=local
LLM_PROVIDER=lmstudio
OPENAI_MODEL=your-model-name
OPENAI_BASE_URL=http://localhost:1234/v1
# OPENAI_API_KEY can be empty
```

**Note**: Ensure LM Studio local server is running and accessible on the configured port.

## Security Best Practices

1. **Never log secrets**: The application never logs API keys or sensitive values
2. **Use environment variables in production**: Avoid hardcoding secrets in files
3. **Rotate keys regularly**: Update `OPENAI_API_KEY` periodically
4. **Restrict file permissions**: Ensure `.env` files have appropriate permissions (e.g., `chmod 600 .env`)
5. **Use secret management**: In production, use systems like:
   - Kubernetes Secrets
   - AWS Secrets Manager
   - HashiCorp Vault
   - Environment variables from your deployment platform

## Troubleshooting

### Application fails to start in production

1. Check that `ENV=prod` is set
2. Verify all required variables are set (see "Required Variables" section)
3. Check startup logs for specific validation errors
4. Ensure `OPENAI_API_KEY` is set if using OpenAI provider

### Application starts but agents fail

1. Verify `OPENAI_MODEL` is set correctly
2. For local providers, ensure the server is running and accessible
3. Check network connectivity to the LLM endpoint
4. Verify the model name exists for your provider

### Configuration changes not taking effect

1. Restart the application after changing environment variables
2. Verify `.env` file is in the project root
3. Check for typos in variable names (they are case-insensitive)
4. Ensure no conflicting environment variables are set in the shell

## Migration Notes

If upgrading from a previous version:

- The `LLM_PROVIDER` variable is new and defaults to `ollama`
- The `ENV` variable is new and defaults to `local`
- Existing configurations without these variables will continue to work
- For production deployments, explicitly set `ENV=prod` and `LLM_PROVIDER` as needed
