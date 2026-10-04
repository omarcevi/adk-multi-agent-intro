# API notes and gotchas (google-adk 2.11.0)

Raw notes for speaker notes. Newest at the bottom.

## Setup

- Latest stable 2.x on PyPI is **2.11.0** (released 2026-10-02). Pinned.
- The docs moved: `google.github.io/adk-docs` now 301-redirects to
  `adk.dev`. Use the new URL on slides.
- `adk run <folder> "<prompt>"` takes a one-shot prompt as an argument,
  handy for demos. Without it, you get an interactive prompt.
- ADK looks for `.env` by walking up from the agent folder, so one root
  `.env` works for every step.

## Step 1

- `from google.adk.agents import Agent` is the documented import.
  `Agent` is just an alias of `LlmAgent` (same class).
- A plain function in `tools=[...]` is wrapped as a `FunctionTool`
  automatically. The docstring and type hints become the tool schema.
- Docs prefer tools that return a `dict`. A plain `str` is fine: ADK
  wraps it as `{"result": "..."}`, which is what you see in the event.
- First version returned only `2026-10-04`. Gemini then said "I can't
  tell you what day of the week it is" instead of working it out. The
  tool now returns `"Sunday, 04 October 2026"`. Lesson for students: the
  model only knows what the tool hands back.
- `adk run` prints three `[EXPERIMENTAL] UserWarning`s on every run
  (`InMemoryCredentialService`, `BaseCredentialService`,
  `JSON_SCHEMA_FOR_FUNC_DECL`). They come from ADK itself, not our code,
  and are harmless. Mention them so nobody panics live.
- `adk run --jsonl` prints the raw events, including the function call
  and response. That's a good terminal fallback if `adk web` misbehaves.

## Step 2

- **`SequentialAgent`, `ParallelAgent` and `LoopAgent` are marked
  `@deprecated` in 2.11.0**: "deprecated in favor of Workflow and will be
  removed in a future version. Workflow cannot yet be used as an LlmAgent
  sub-agent."
- It is a `DeprecationWarning`, which Python hides by default. It does
  **not** show in `adk run` or `adk web`. You only see it with
  `python -W default`. Worth one sentence in the talk: these still work
  and are the simplest way to learn, but ADK is moving to `Workflow`.
- `output_key` writes the agent's final text into state as a
  `state_delta` on that agent's event. You can watch `research`, then
  `brief`, appear in the State tab.
- `{research}` in an instruction is filled from state before the model
  call. If the key is missing, ADK raises `KeyError: Context variable
  not found`. Write `{research?}` to get an empty string instead.
- The researcher has no search tool, so its "facts" come from the
  model's training data. Say this out loud; they can be out of date.

## Step 3

- `ParallelAgent` isolates only conversation history between branches.
  **State is shared**: if two branches write the same key, the last one
  wins. That's why each researcher needs its own `output_key`.
- In the output, the researchers finish in a different order each run
  and within ~0.1s of each other. That's the clearest proof they run at
  the same time.
- Researchers kept opening with "Here's a brief on...". Adding "no
  intro" to the instruction fixed it. Anything the agent says ends up
  in state.

## Step 4

- Built-in exit tool: `from google.adk.tools import exit_loop`. It sets
  `escalate = True` and `skip_summarization = True`, so the critic makes
  no extra LLM call after approving.
- "Reviser must not run after approval" is handled by `LoopAgent`
  itself. On escalate it breaks out mid-iteration, so the next
  sub-agent never starts. Seen in every run: `critic CALL exit_loop`
  is the last event.
- With the exit tool removed, the reviser ran exactly 3 times, then
  stopped. `max_iterations` works as the safety net.
- Gemini usually approves on pass 2 or 3. The first draft is almost
  always over 200 words, so the loop reliably shows at least one
  revision.

## Step 5

- Transfer happens through an auto-added `transfer_to_agent` tool call,
  visible as an event. The coordinator picks the agent by name, based
  on the `description`s.
- Same session, two prompts: `quick_answer` answered the first question,
  then handed the brief request to its **peer** `brief_pipeline` itself.
  After the pipeline, the next simple question reached `quick_answer`
  again. Routing works without restarting the session.
- The agents inside `SequentialAgent`/`LoopAgent` get no transfer
  tool, because their parent is not an LLM agent. Good: the critic
  can't wander off.
- The reviser once added "**Date:** October 26, 2023" to a brief. The
  model hallucinated a date. Nice callback to step 1.
- Docs: the multi-agent page on adk.dev now redirects to the
  `Workflow` page.
- `LlmAgent` has a `mode` field (default `None`). We never set it.

## Step 5: web search (added later)

- `from google.adk.tools import google_search` is a **Gemini built-in**
  tool. The model runs Google searches itself, and no Python code runs.
- Gemini can't combine built-in search with function calling. An agent
  with `google_search` **and** transfer targets raises an error on 2.11,
  unless you use `GoogleSearchTool(bypass_multi_tools_limit=True)`.
  Putting `web_researcher` inside `brief_pipeline` avoids that: agents
  under a `SequentialAgent` get no transfer tool.
- The event carries `grounding_metadata`: the queries the model ran
  (e.g. "Electric vehicle sales Turkey 2023 2024") and the source sites.
  Worth showing in `adk web`.
- Real data made the first draft about 270 words, and the loop ran out
  (3 passes) without approval. Adding "about 150 words" to the
  first-draft instruction fixed it. The critic now approves on pass 3.
- The search agent ignores "No intro" and still opens with "Here's a
  brief…". Harmless: only the writer reads it.

## "Performance Alert: System instructions were modified…"

- This comes from the `adk web` UI, not from Gemini or our code. The UI
  sorts every `call_llm` span in the session by time and compares each
  system instruction with the **previous LLM call's**, whichever agent
  made it. Any difference gets flagged.
- In a multi-agent app it fires on almost every agent switch
  (researcher → writer, critic → reviser), because each agent has its
  own instruction by design. Those calls never shared a cache, so it's
  a false positive.
- The one real case: `{draft}` templating changes the critic's own
  instruction on every loop pass. That's the price of state templating,
  and with prompts this short it doesn't matter.
- Speaker note: ignore it, or use it to show that every agent really
  has its own system prompt. Click the warning to see the side-by-side
  diff.

## Traces

- Local: the `adk web` **Traces** tab. Spans are `invocation` →
  `call_llm` / `execute_tool`. The web UI always records full prompts and
  replies, even when content capture is off elsewhere.
- Deployed: needs `--otel_to_cloud` (see below), then Cloud Trace. The
  runtime forces `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`, so cloud
  spans show timing and agent names, not prompt text.

## Deploy

- `--staging_bucket` and `--requirements_file` are **deprecated** on
  2.11. If `requirements.txt` is missing in the agent folder, ADK
  creates one in the staged copy (`google-cloud-aiplatform[adk,
  agent_engines]` + `google-adk[a2a]==2.11.0`). We don't add one.
- `adk deploy agent_engine` needs `vertexai`, which is **not**
  installed by `google-adk`. Hence `deploy/requirements.txt`.
- The deploy reads `.env` only from the agent folder, not the repo root,
  so the AI Studio key is not uploaded. The deployed app gets
  `GOOGLE_GENAI_USE_ENTERPRISE=1` (Vertex) automatically.
- Env var rename: `google-genai` now prefers `GOOGLE_GENAI_USE_ENTERPRISE`
  and `adk create` writes that one. The old `GOOGLE_GENAI_USE_VERTEXAI`
  still works. If both are set and disagree, ENTERPRISE wins (with a
  warning).
- SDK rename: current docs use `import agentplatform` and
  `client.runtimes.get(...)`. The older `vertexai.Client().agent_engines`
  still exists. Both ship in `google-cloud-aiplatform` 2.3.0.
- `stream_query` is deprecated. Use `async_stream_query`.
- `adk deploy` itself prints `FutureWarning: The vertexai.Client class
  is deprecated. Please use agentplatform.Client instead.` That warning
  is from ADK's own code and harmless. It confirms `query.py` uses the
  right SDK.
- The deploy took a few minutes. It creates and then removes a
  `step5_coordinator_tmp<timestamp>/` folder in the repo root, so don't
  panic if you see it mid-deploy.
- It ends with a Cloud Console playground link for the agent. That's a
  good thing to click live.
- The deployed agent routed both demo prompts exactly like the local
  one, including the critic → reviser loop.
- **Telemetry is off by default.** The console's Observability tab said
  "Settings not available for this agent" and blamed outdated
  dependencies. Our dependencies were fine. The real cause: without
  `--otel_to_cloud`, ADK doesn't set
  `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY`, and the console toggle
  only works when that variable exists. `deploy.sh` now passes the flag.
- Even with telemetry on, ADK sets
  `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`, so traces show timing
  and agent names but not prompts and replies.
- Re-running `deploy.sh` creates a new instance. Use `--agent_engine_id`
  to update an existing one in place.
- Cloud docs moved from `cloud.google.com/vertex-ai/...` to
  `docs.cloud.google.com/gemini-enterprise-agent-platform/...`.
