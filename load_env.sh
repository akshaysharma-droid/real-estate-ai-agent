#!/bin/bash

# ======================================================
# LOAD ENV VARIABLES FROM .env FILE
# ======================================================
# This script reads your .env file and exports variables
# into your current shell environment.
#
# WHY?
# - Avoid manually typing export commands
# - Reuse .env for local + deployment
# ======================================================


# ------------------------------------------------------
# STEP 1: Check if .env file exists
# ------------------------------------------------------
if [ ! -f .env ]; then
  echo "❌ .env file not found in current directory"
  return 1
fi


# ------------------------------------------------------
# STEP 2: Export variables
# ------------------------------------------------------
echo "🔄 Loading environment variables from .env..."

# Ignore comments and empty lines
export $(grep -v '^#' .env | grep -v '^$' | xargs)


# ------------------------------------------------------
# STEP 3: Verify important variables
# ------------------------------------------------------
echo "✅ Loaded variables:"

echo "PROJECT_ID=$GOOGLE_CLOUD_PROJECT"
echo "MAPS_API_KEY=${MAPS_API_KEY:0:5}*****"
echo "TAVILY_API_KEY=${TAVILY_API_KEY:0:5}*****"

echo "🎉 Environment ready!"
