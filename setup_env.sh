#!/bin/bash

# ======================================================
# SETUP SCRIPT FOR GOOGLE MAPS MCP (REAL ESTATE AGENT)
# ======================================================
# This script:
# 1. Detects your GCP project
# 2. Enables required APIs
# 3. Creates a Google Maps API key
# 4. Stores it safely in a .env file
#
# WHY?
# So you don't hardcode API keys in Python code
# ======================================================


# ------------------------------------------------------
# STEP 1: Get Project ID
# ------------------------------------------------------
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project not set"
    echo "Run: gcloud config set project <PROJECT_ID>"
    exit 1
fi

echo "✅ Using Project: $PROJECT_ID"


# ------------------------------------------------------
# STEP 2: Enable Required APIs
# ------------------------------------------------------
echo "🔧 Enabling required APIs..."

# API for creating API keys
gcloud services enable apikeys.googleapis.com --project=$PROJECT_ID

# Google Maps MCP API (IMPORTANT)
gcloud services enable mapstools.googleapis.com --project=$PROJECT_ID

# Vertex AI (for Gemini / ADK)
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID


# ------------------------------------------------------
# STEP 3: Enable MCP Support
# ------------------------------------------------------
# This enables MCP integration for Maps
echo "⚙️ Enabling MCP for Maps..."

gcloud --quiet beta services mcp enable mapstools.googleapis.com --project=$PROJECT_ID


# ------------------------------------------------------
# STEP 4: Create API Key
# ------------------------------------------------------
echo "🔑 Creating Maps API Key..."

API_KEY_NAME="real-estate-maps-key-$(date +%s)"

API_KEY_JSON=$(gcloud alpha services api-keys create \
    --display-name="$API_KEY_NAME" \
    --api-target=service=mapstools.googleapis.com \
    --format=json 2>/dev/null)

if [ $? -eq 0 ]; then
    # Extract key value from JSON output
    API_KEY=$(echo "$API_KEY_JSON" | grep -oP '"keyString": "\K[^"]+')
    echo "✅ API Key created successfully"
else
    echo "⚠️ Could not auto-create API key"
    read -p "Enter your API key manually: " API_KEY
fi

# Validate API key
if [ -z "$API_KEY" ]; then
    echo "❌ API Key is empty"
    exit 1
fi


# ------------------------------------------------------
# STEP 5: Save to .env file
# ------------------------------------------------------
# This file will be used by Python (tools.py)
echo "💾 Saving configuration to .env file..."

ENV_FILE="./.env"

cat <<EOF > "$ENV_FILE"
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=global
MAPS_API_KEY=$API_KEY
EOF

echo "✅ .env file created at $ENV_FILE"

# DONE
echo "🎉 Setup complete!"
