# Day 12 Lab — Mission Answers

> **Student Name:** Nhữ Gia Bách
> **Student ID:** 2A202600248
> **Date:** 17/04/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns Found

1. `01-localhost-vs-production/develop/app.py` hardcodes `OPENAI_API_KEY`, làm lộ secret nếu đẩy repo lên.
2. File này cũng hardcode `DATABASE_URL` kèm credentials khiến config không an toàn và để lộ host/password nhạy cảm.
3. `DEBUG = True` và các hằng số khác nằm trong code thay vì lấy từ env/config, nên không thể chuyển đổi giữa localhost và production.
4. Handler `/ask` dùng `print(...)` để log câu hỏi/key/response — log không có cấu trúc và in cả secret ra stdout.
5. Không có endpoint `/health` hoặc readiness, nên platform không biết service còn sống để restart khi lỗi.
6. `uvicorn.run` chỉ bind tới `localhost:8000` với `reload=True`, bỏ qua biến `PORT`/host runtime và vẫn bật reload debug trong production.

---

### Exercise 1.3: Comparison Table

| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Khóa API/DB URL và flag debug được hardcode | `config.settings` lấy từ env (`PORT`, secret, log level) | Đám mây cần env vars cho secret và để chuyển môi trường linh hoạt |
| Health check | Không có | Có endpoint `/health`, `/ready`, `/metrics` cùng flag startup | Probe của platform cần liveness/readiness để restart và tránh chuyển traffic sớm |
| Logging | `print()` lộ secret | Logging JSON có cấu trúc, chỉ metadata của request/response | Giúp observability, parse log dễ mà không leak credential |
| Shutdown | `uvicorn.run(... reload=True)` bind localhost và ignore signal | Lifespan + SIGTERM handler cho shutdown trơn tru | Shutdown nhẹ nhàng bảo vệ request đang xử lý và cleanup tài nguyên |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile Questions

1. **Base image** là image nền được dùng làm điểm khởi đầu, thường bao gồm hệ điều hành và runtime (ở đây `python:3.11` có sẵn Python/pip). Các lệnh sau build theo từng layer trên image đó; chọn image phù hợp giúp giữ kích thước nhỏ và có sẵn các công cụ cần thiết.
2. **Working directory:** `/app` trong container để các lệnh tiếp theo chạy trong thư mục đó.
3. Copy `requirements.txt` **trước** phần code còn lại để tận dụng cache của Docker layer — `pip install` chỉ chạy lại khi file dependencies thay đổi.
4. `CMD` định nghĩa lệnh mặc định có thể ghi đè lúc chạy, trong khi `ENTRYPOINT` cố định executable (thường dùng cho wrapper/bootloader). Dockerfile này dùng `CMD ["python", "app.py"]` để giữ tính linh hoạt.

---

### Exercise 2.3: Image Size Comparison

| Image | Size |
|-------|------|
| Develop | 1,670 MB (1.67 GB) |
| Production | 262 MB |
| **Difference** | **1,408 MB (84.3% smaller)** |

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway Deployment

- **URL:** <https://fabulous-motivation-production-d61d.up.railway.app/>
- **Screenshot:** `day12_ha-tang-cloud_va_deployment/Screenshot.png`

---

## Part 4: API Security

### Exercise 4.1–4.3: Test Results

**Develop — API key auth:**

```bash
curl -X POST \
  -H "X-API-Key: demo-key-change-in-production" \
  "http://localhost:8000/ask?question=hello"
```

```json
{
  "question": "hello",
  "answer": "Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."
}
```

**Production — JWT Bearer auth:**

```bash
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}'
```

```json
{
  "question": "Explain JWT",
  "answer": "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
  "usage": {
    "requests_remaining": 9,
    "budget_remaining_usd": 1.9e-05
  }
}
```

**Rate limiting analysis:**

1. **Algorithm:** Sliding Window
   - Mỗi user có một deque lưu timestamp của các request.
   - Khi có request mới, loại bỏ các request cũ ngoài khoảng 60 giây, đếm số request còn lại.
   - Nếu vượt quá giới hạn → trả về `429 Too Many Requests`.

2. **Limits:**
   - User thường: 10 requests / phút
   - Admin: 100 requests / phút

3. **Admin bypass:** Admin không bypass hoàn toàn, nhưng dùng rate limiter riêng với giới hạn cao hơn (100 thay vì 10). Hệ thống phân biệt role và áp dụng limiter tương ứng.

**Rate limit stress test (20 requests):**

```bash
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"Test $i\"}"
  echo ""
done
```

<details>
<summary>Output (click to expand)</summary>

```
{"question":"Test 1","answer":"...","usage":{"requests_remaining":9,"budget_remaining_usd":3.5e-05}}
{"question":"Test 2","answer":"...","usage":{"requests_remaining":8,"budget_remaining_usd":5.3e-05}}
{"question":"Test 3","answer":"...","usage":{"requests_remaining":7,"budget_remaining_usd":7.4e-05}}
{"question":"Test 4","answer":"...","usage":{"requests_remaining":6,"budget_remaining_usd":9.3e-05}}
{"question":"Test 5","answer":"...","usage":{"requests_remaining":5,"budget_remaining_usd":0.000114}}
{"question":"Test 6","answer":"...","usage":{"requests_remaining":4,"budget_remaining_usd":0.00013}}
{"question":"Test 7","answer":"...","usage":{"requests_remaining":3,"budget_remaining_usd":0.000149}}
{"question":"Test 8","answer":"...","usage":{"requests_remaining":2,"budget_remaining_usd":0.000165}}
{"question":"Test 9","answer":"...","usage":{"requests_remaining":1,"budget_remaining_usd":0.000186}}
{"question":"Test 10","answer":"...","usage":{"requests_remaining":0,"budget_remaining_usd":0.000205}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":59}}
... (×10 more 429 responses)
```

</details>

---

### Exercise 4.4: Cost Guard Implementation

Để kiểm soát chi phí sử dụng LLM, cơ chế kiểm tra budget theo từng user được triển khai với các đặc điểm:

- Mỗi user có budget cố định **$10 / tháng**.
- Sử dụng **Redis** để lưu trữ tổng chi tiêu của user theo từng tháng.
- Key trong Redis có dạng: `cost:{user_id}:{year-month}` (ví dụ: `cost:student:2026-04`).

**Quy trình:**

1. Khi có request mới, lấy tổng chi tiêu hiện tại của user trong tháng từ Redis.
2. Nếu chưa có dữ liệu → coi như $0.
3. Kiểm tra:
   - Nếu `current_spent + estimated_cost > $10` → từ chối (`return False`).
   - Ngược lại → cho phép (`return True`) và cập nhật lại chi tiêu.
4. Reset budget tự động theo tháng vì key chứa `year-month`.

**Lợi ích:**
- Không cần cron job để reset.
- Scale tốt khi dùng Redis trong production.

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health Checks

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "uptime_seconds": 151.4,
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-04-17T10:23:06.592989+00:00",
  "checks": {
    "memory": { "status": "ok", "note": "psutil not installed" }
  }
}
```

```bash
curl http://localhost:8000/ready
# {"ready":true,"in_flight_requests":1}

curl http://localhost:8000/
# {"message":"AI Agent with health checks!"}
```

---

### Exercise 5.2: Graceful Shutdown

```bash
# Gửi request (có thể kéo dài)
curl -X POST "http://localhost:8000/ask?question=Tell%20me%20a%20long%20story" &

# Ngay lập tức gửi SIGTERM
kill -TERM $PID
```

**Kết quả:** Request hoàn thành trước khi server tắt.

```
{"answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận."}
```

---

### Exercise 5.4: Load Balancing

Nginx được sử dụng làm Load Balancer với thuật toán **round-robin**.

```nginx
upstream agent_cluster {
    server agent:8000;
    keepalive 16;
}
```

**Test — 10 requests liên tiếp:**

```bash
for i in {1..10}; do
  curl http://localhost:8080/chat -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "Request '$i'"}'
done
```

**Logs từ agent-1:**

```
agent-1  | INFO:     172.18.0.6:40764 - "POST /chat HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.6:40764 - "POST /chat HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.6:40764 - "POST /chat HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.6:40764 - "POST /chat HTTP/1.1" 200 OK
```

**Logs từ agent-2:**

```
agent-2  | INFO:     172.18.0.6:40906 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:40906 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:40906 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:49028 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:49028 - "POST /chat HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:49028 - "POST /chat HTTP/1.1" 200 OK
```

---

### Exercise 5.5: Stateless Scaling with Redis

```bash
python test_stateless.py
```

```
============================================================
Stateless Scaling Demo
============================================================

Session ID: 1c7ee991-4d43-4899-8cab-e8699b53f362

Request 1: [instance-66bce1]
  Q: What is Docker?
  A: Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!...

Request 2: [instance-66bce1]
  Q: Why do we need containers?
  A: Đây là câu trả lời từ AI agent (mock)...

Request 3: [instance-66bce1]
  Q: What is Kubernetes?
  A: Đây là câu trả lời từ AI agent (mock)...

Request 4: [instance-66bce1]
  Q: How does load balancing work?
  A: Tôi là AI agent được deploy lên cloud...

Request 5: [instance-66bce1]
  Q: What is Redis used for?
  A: Đây là câu trả lời từ AI agent (mock)...

------------------------------------------------------------
Total requests: 5
Instances used: {'instance-66bce1'}
ℹ️  Only 1 instance (scale up với: docker compose up --scale agent=3)

--- Conversation History ---
Total messages: 10
  [user]: What is Docker?...
  [assistant]: Container là cách đóng gói app để chạy ở mọi nơi...
  [user]: Why do we need containers?...
  [assistant]: Đây là câu trả lời từ AI agent (mock)...
  [user]: What is Kubernetes?...
  [assistant]: Đây là câu trả lời từ AI agent (mock)...
  [user]: How does load balancing work?...
  [assistant]: Tôi là AI agent được deploy lên cloud...
  [user]: What is Redis used for?...
  [assistant]: Đây là câu trả lời từ AI agent (mock)...

✅ Session history preserved across all instances via Redis!
```