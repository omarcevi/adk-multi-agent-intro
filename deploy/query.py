"""Send one message to the deployed agent and print the reply.

Usage:
  export GOOGLE_CLOUD_PROJECT=my-project
  export AGENT_RESOURCE_NAME=projects/.../reasoningEngines/123
  python deploy/query.py "What is an EV?"
"""

import asyncio
import os
import sys

import agentplatform

client = agentplatform.Client(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="us-central1",
)
# The resource name is printed at the end of deploy.sh.
agent = client.runtimes.get(name=os.environ["AGENT_RESOURCE_NAME"])


async def main(message: str) -> None:
    # Each event is a dict, like the events you saw in adk web.
    async for event in agent.async_stream_query(
        user_id="demo-user", message=message
    ):
        for part in event.get("content", {}).get("parts", []):
            if "text" in part:
                print(f"[{event['author']}]: {part['text']}")


asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "What is an EV?"))
