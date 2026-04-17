# Deployment Information

## Public URL
`https://lab6-complete-production.up.railway.app`

## Platform
Railway

## Status
✅ Online - Service is running successfully

## Deployment Date
2026-04-17

---

## Test Commands & Results

### Root Endpoint

```bash
curl https://lab6-complete-production.up.railway.app/
```

**Result:**
```json
{
  "app": "Production AI Agent",
  "version": "1.0.0",
  "environment": "production",
  "endpoints": {
    "ask": "POST /ask (requires X-API-Key)",
    "health": "GET /health",
    "ready": "GET /ready"
  }
}
```

---

### Health Check

```bash
curl https://lab6-complete-production.up.railway.app/health
```

**Result:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 212.8,
  "total_requests": 5,
  "checks": {
    "llm": "mock"
  },
  "timestamp": "2026-04-17T16:33:49.923500+00:00"
}
```

---

### Readiness Check

```bash
curl https://lab6-complete-production.up.railway.app/ready
```

**Result:**
```json
{
  "ready": true
}
```

---

### API Test (with Authentication)

```bash
curl -X POST https://lab6-complete-production.up.railway.app/ask \
  -H "X-API-Key: ***REDACTED**" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

**Result:**
```json
{
  "question": "What is Docker?",
  "answer": "Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T16:34:04.149099+00:00"
}
```

---

### Second API Test

```bash
curl -X POST https://lab6-complete-production.up.railway.app/ask \
  -H "X-API-Key: ***REDACTED**" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain Kubernetes"}'
```

**Result:**
```json
{
  "question": "Explain Kubernetes",
  "answer": "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
  "model": "gpt-4o-mini",
  "timestamp": "2026-04-17T16:34:11.522758+00:00"
}
```

---

## Environment Variables Set on Railway

| Variable | Value |
|---|---|
| `AGENT_API_KEY` | `***REDACTED**` |
| `JWT_SECRET` | `***REDACTED**` |
| `RATE_LIMIT_PER_MINUTE` | `10` |
| `MONTHLY_BUDGET_USD` | `10.0` |
| `ENVIRONMENT` | `production` |
| `PORT` | `8000` |
| `REDIS_URL` | Railway internal Redis |

---

## Features Verified

- ✅ Health check endpoint (`GET /health`)
- ✅ Readiness probe (`GET /ready`)
- ✅ API Key authentication (`X-API-Key` header)
- ✅ Mock LLM responses
- ✅ Root endpoint with API information
- ✅ Redis connection (stateless design)
- ✅ Production environment configuration

---

## Deployment Notes

- Multi-stage Dockerfile used (< 500 MB)
- Redis for rate limiting and session storage
- Graceful shutdown configured
- Health check passes automatically
- Service is stateless and scalable

---

## Screenshots

- Railway Dashboard
- Service Running
- API Test Results

---

## Repository

GitHub: [https://github.com/AgentZoil/day12_ha-tang-cloud_va_deployment/tree/main/06-lab-complete](https://github.com/AgentZoil/day12_ha-tang-cloud_va_deployment/tree/main/06-lab-complete)