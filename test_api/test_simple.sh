#!/bin/bash

echo "🧪 Simple Test - Create Session and Run Agent"
echo "=============================================="
echo ""

# Test 1: Create Session
echo "1️⃣  Creating session..."
curl -s -X POST http://localhost:8000/apps/my_sample_agent/users/u_456/sessions/s_456 \
  -H "Content-Type: application/json" \
  -d '{"state": {"test": "simple"}}' | jq '.id, .appName'

echo ""
echo "✅ Session created"
echo ""

# Test 2: Run Agent
echo "2️⃣  Running agent..."
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_456",
    "session_id": "s_456",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write a very short article about robots (2 sentences max)"}
      ]
    },
    "streaming": false
  }'

echo ""
echo ""
echo "✅ Test complete"
