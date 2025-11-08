#!/bin/bash

# Aegis curl Examples
# Demonstrates how to interact with the Aegis API via curl

API_URL="http://127.0.0.1:8000"

echo "🛡️  Aegis API Examples"
echo "======================"
echo ""
echo "Make sure the API is running: bash scripts/dev.sh"
echo ""

# Health check
echo "1️⃣  Health Check"
echo "   curl $API_URL/health"
echo ""
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Unsafe action (should block)
echo "2️⃣  Unsafe Action (Should Block)"
echo "   This action has 'delete' in the intent, so policy blocks it"
echo ""
curl -s -X POST "$API_URL/propose_action" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "delete table",
    "file_path": "config/app.yaml",
    "new_contents": "service: web\npagination: 100\nfeatureX: false\n",
    "prompt": "Please delete old tables",
    "est_tokens": 800,
    "use_modal": false
  }' | python3 -m json.tool | head -30
echo ""
echo "---"
echo ""

# Safe action (should allow)
echo "3️⃣  Safe Action (Should Allow)"
echo "   This action passes policy and tests"
echo ""
curl -s -X POST "$API_URL/propose_action" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "increase pagination",
    "file_path": "config/app.yaml",
    "new_contents": "service: web\npagination: 50\nfeatureX: false\n",
    "prompt": "Bump pagination safely",
    "est_tokens": 800,
    "use_modal": false
  }' | python3 -m json.tool | head -40
echo ""
echo "---"
echo ""

# Get latest risk card
echo "4️⃣  Get Latest Risk Card"
echo "   curl $API_URL/riskcard"
echo ""
curl -s "$API_URL/riskcard" | python3 -m json.tool | head -20
echo ""
echo "---"
echo ""

# Get history
echo "5️⃣  Get Risk Card History"
echo "   curl $API_URL/riskcard/history"
echo ""
curl -s "$API_URL/riskcard/history?limit=3" | python3 -m json.tool | head -30
echo ""
echo "✅ Examples complete!"
echo ""
echo "💡 Tip: Use jq for better JSON formatting:"
echo "   curl ... | jq"

