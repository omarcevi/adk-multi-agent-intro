#!/usr/bin/env bash
# Deploys step5_coordinator to Agent Runtime (Vertex AI Agent Engine).
# Usage: GOOGLE_CLOUD_PROJECT=my-project ./deploy/deploy.sh
set -euo pipefail

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT to your project ID}"

cd "$(dirname "$0")/.."  # run from the repo root

# No staging bucket or requirements flag needed on ADK 2.11: ADK builds
# the requirements for the deployed copy automatically.
# --otel_to_cloud turns on traces and logs (the console's Observability
# tab). Without it, the console says "Settings not available".
adk deploy agent_engine \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region us-central1 \
  --display_name "Research Assistant" \
  --otel_to_cloud \
  step5_coordinator
