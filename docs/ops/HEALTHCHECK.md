# Health Check and Production Configuration

This document describes the health check endpoint and production configuration recommendations for the AI Decision Traceability Engine API.

## Health Check Endpoint

The API provides a `/health` endpoint for monitoring and load balancer health checks.

### Endpoint Details

- **Path**: `GET /health`
- **Response**: JSON with the following structure:
  ```json
  {
    "status": "ok",
    "version": "0.1.0",
    "time": "2024-01-15T10:30:45.123456Z"
  }
  ```
- **Status Code**: `200 OK` when the service is healthy

### Usage

The health endpoint can be used by:
- Load balancers for health checks
- Monitoring systems (e.g., Prometheus, Datadog)
- Container orchestration systems (e.g., Kubernetes liveness/readiness probes)
- CI/CD pipelines for deployment verification

## Request Size Limits

The API enforces a configurable maximum request body size to protect against oversized requests.

### Configuration

- **Environment Variable**: `MAX_REQUEST_SIZE` (in bytes)
- **Default**: `1048576` (1 MB)
- **Behavior**: Requests exceeding the limit return `413 Request Entity Too Large`

### Example Response (Oversized Request)

```json
{
  "error": "Request entity too large",
  "detail": "Request body size (2097152 bytes) exceeds maximum allowed size (1048576 bytes)"
}
```

## Uvicorn Timeout Configuration

When running the API with Uvicorn, configure appropriate timeouts for production use:

### Recommended Settings

```bash
uvicorn src.api.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --timeout-keep-alive 5 \
  --timeout-graceful-shutdown 30 \
  --limit-concurrency 100 \
  --limit-max-requests 1000
```

### Timeout Parameters

- **`--timeout-keep-alive`**: Time in seconds to wait for additional data on a connection before closing it. Recommended: `5` seconds.
- **`--timeout-graceful-shutdown`**: Maximum time to wait for graceful shutdown. Recommended: `30` seconds.
- **`--limit-concurrency`**: Maximum number of concurrent connections. Adjust based on your server capacity.
- **`--limit-max-requests`**: Maximum number of requests before restarting workers (useful for memory leak prevention).

### Production Considerations

1. **Worker Processes**: Use multiple workers for better concurrency:
   ```bash
   uvicorn src.api.app:app --workers 4
   ```

2. **Reverse Proxy**: Deploy behind a reverse proxy (nginx, Traefik) for:
   - SSL/TLS termination
   - Additional rate limiting
   - Request buffering
   - Static file serving

3. **Monitoring**: Configure health check monitoring with appropriate intervals:
   - Liveness probe: Every 10-30 seconds
   - Readiness probe: Every 5-10 seconds

## Manual Testing

### Health Check Test

```bash
# Basic health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "ok",
#   "version": "0.1.0",
#   "time": "2024-01-15T10:30:45.123456Z"
# }
```

### Request Size Limit Test

To test the request size limit, create a payload that exceeds the configured maximum (default 1MB):

```bash
# Create a large JSON payload (conceptually)
# This example shows the concept - in practice, you would generate a file
# with content exceeding 1MB

# Example: POST with oversized payload
curl -X POST http://localhost:8000/decision/run \
  -H "Content-Type: application/json" \
  -H "Content-Length: 2097152" \
  -d @large_payload.json

# Expected response (413):
# {
#   "error": "Request entity too large",
#   "detail": "Request body size (2097152 bytes) exceeds maximum allowed size (1048576 bytes)"
# }
```

**Note**: To actually test this, you would need to:
1. Create a JSON file larger than 1MB (or your configured limit)
2. Use that file with the `-d @filename.json` option
3. The middleware checks the `Content-Length` header, so ensure it matches the actual file size

### Example: Creating a Test Payload

```bash
# Generate a large test payload (Python example)
python -c "
import json
large_data = {'context': {'data': 'x' * 2000000}}  # ~2MB string
with open('large_payload.json', 'w') as f:
    json.dump(large_data, f)
"

# Then test with:
curl -X POST http://localhost:8000/decision/run \
  -H "Content-Type: application/json" \
  -d @large_payload.json
```

## Error Response Format

All error responses follow a consistent JSON format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

This ensures consistent error handling across all endpoints, including the health check and request size validation.
