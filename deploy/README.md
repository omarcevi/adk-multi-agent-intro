# Deploy step 5 to Agent Runtime

Deploys `step5_coordinator` to Agent Runtime (Vertex AI Agent Engine) in
`us-central1`, then sends it one message.

## Prerequisites

1. A Google Cloud project with **billing enabled**.
2. The Vertex AI API enabled:
   `gcloud services enable aiplatform.googleapis.com`
3. Local credentials:
   `gcloud auth application-default login`
4. The deploy SDK, on top of the root requirements:
   `pip install -r deploy/requirements.txt`

The deployed agent uses Vertex AI with your project's credentials, not
the AI Studio key in the root `.env`. That file is not uploaded.

## Deploy

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
./deploy/deploy.sh
```

This takes several minutes. At the end it prints a line like:

```
Deployed to Agent Platform: projects/123/locations/us-central1/reasoningEngines/456
```

Copy that resource name.

Running `deploy.sh` again creates a **second** agent (and a second bill).
To update the existing one instead, run the same `adk deploy agent_engine`
command with `--agent_engine_id <ID>` added, where `<ID>` is the last
number in the resource name.

`deploy.sh` passes `--otel_to_cloud` so traces and logs show up in the
Cloud Console's Observability tab. Prompts and replies are **not**
recorded in traces by default.

## Query

```bash
export AGENT_RESOURCE_NAME=projects/123/locations/us-central1/reasoningEngines/456
python deploy/query.py "What is an EV?"
python deploy/query.py "Write me a brief on EVs in Turkey"
```

## Delete it afterwards (avoid cost)

A deployed agent costs money while it exists. Delete it when you are done:

```bash
python -c "import agentplatform, os; agentplatform.Client(project=os.environ['GOOGLE_CLOUD_PROJECT'], location='us-central1').runtimes.delete(name=os.environ['AGENT_RESOURCE_NAME'], force=True)"
```

`force=True` also deletes the agent's sessions. You can also delete it
from the Agent Engine page in the Cloud Console (check that the list
is empty afterwards).
