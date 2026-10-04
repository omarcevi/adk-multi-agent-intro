# Multi-Agent Talk — Code Repo

Code for a 1-hour talk on multi-agent architecture and orchestration with
Google ADK. Audience: AI bootcamp students who are **new to agents and know
basic Python**. The code is pre-written; the speaker walks through it on
slides and runs it live in `adk web`.

## Golden rules

- **Readable beats clever.** Every file will be shown on a slide. Keep each
  `agent.py` under ~40 lines where possible, lines under 80 characters, and
  no abstractions, helpers, or shared modules between steps.
- **Comment for beginners.** Short comments explaining *why*, not what. Mark
  the one line each step is about with `# <- KEY LINE`.
- **Each step is self-contained.** Every folder runs on its own and can be
  copied out alone. Duplicate code between steps instead of importing.
- **Verify the API, don't guess.** ADK 2 changed import paths and defaults.
  Before writing code, check the installed `google-adk` package source and
  the official docs (google.github.io/adk-docs). If something in this file
  conflicts with the real API, follow the real API and tell me.

## Scope: what to use and what not to use

Use only:
- `Agent` / `LlmAgent`, plain Python function tools
- `SequentialAgent`, `ParallelAgent`, `LoopAgent`
- `sub_agents` for coordinator delegation, `AgentTool` (one mention)
- Session state via `output_key` and `{key}` templating in instructions

Do NOT use: the ADK 2 `Workflow` graph API, `JoinNode`, `@node`, `START`,
`Event` routing, `ctx.run_node`, or agent `mode=` settings. The talk
deliberately stays with workflow agents.

## Stack

- Python 3.11+
- `google-adk`: latest stable **2.x**, pinned to an exact version in
  `requirements.txt`. Check PyPI for the current version first.
- Model: `gemini-2.5-flash` everywhere (also works on Agent Runtime regions).
- Local runs: Google AI Studio API key in a root `.env`
  (`GOOGLE_API_KEY=...`, `GOOGLE_GENAI_USE_VERTEXAI=False`).
- Deploy: Vertex AI / Agent Runtime via `adk deploy agent_engine`.
- Never commit real keys. Provide `.env.example`, add `.env` to `.gitignore`.

If `SequentialAgent` (or the others) prints a deprecation warning on the
pinned version, tell me. Don't silence it without asking.

## Repo layout

Each step is an ADK agent folder (`__init__.py` with `from . import agent`,
and `agent.py` defining `root_agent`), so `adk web` from the repo root lists
them all. Folder names must be valid Python identifiers.

```
step1_single_agent/
step2_sequential/
step3_parallel/
step4_loop/
step5_coordinator/
deploy/            # deploy.sh, query.py, notes
README.md
requirements.txt
.env.example
```

## Running example: a research assistant

The same app grows step by step. Topic is supplied by the user at runtime
(e.g. "electric cars in Turkey").

### step1_single_agent — what is an agent?
- One agent with one function tool: `get_current_date()` returning today's
  date as a string. The model can't know the date, so it must call the tool.
- Demo prompt: "What's today's date, and what day of the week is it?"
- Show in `adk web`: the function-call event.

### step2_sequential — assembly line
- `researcher` (writes key facts, `output_key="research"`)
  → `writer` (reads `{research}`, writes a short brief, `output_key="brief"`).
- Wrapped in a `SequentialAgent`.
- Demo prompt: "Write a brief on electric cars in Turkey."
- Show: state tab filling with `research`, then `brief`.

### step3_parallel — fan-out and gather
- `ParallelAgent` with three researchers, each with its own `output_key`:
  `background`, `current_state`, `future_outlook`.
- Then a `writer` that merges all three into one brief.
- Structure: `SequentialAgent([ParallelAgent([...3]), writer])`.
- Comment the rule: parallel agents must not depend on each other.

### step4_loop — writer and critic
- `SequentialAgent([first_draft_writer, LoopAgent([critic, reviser])])`.
- `first_draft_writer` -> `output_key="draft"`.
- `critic` reviews `{draft}`; if it is good enough, it calls an exit tool to
  stop the loop; otherwise it writes feedback (`output_key="feedback"`).
- `reviser` rewrites `{draft}` using `{feedback}` (`output_key="draft"`).
- `max_iterations=3` with a `# <- KEY LINE` comment: always bound loops.
- Use ADK's built-in exit-loop tool if the pinned version has one; otherwise
  write a tiny function that sets `tool_context.actions.escalate = True`.
- Watch out: the reviser must not run after the critic approves.

### step5_coordinator — the LLM decides
- `front_desk` coordinator with `sub_agents=[quick_answer, brief_pipeline]`.
- `quick_answer`: answers simple questions directly in a few sentences.
- `brief_pipeline`: copy of the step 4 pipeline (copied, not imported).
- Every sub-agent needs a clear `description=`; comment that this is what
  the coordinator reads when choosing.
- Demo prompts: "What is an EV?" (quick) vs "Write me a brief on EVs in
  Turkey" (pipeline).
- Add a short commented-out alternative showing the coordinator using
  `AgentTool(agent=quick_answer)` instead, with one comment on the
  difference (control returns to the caller).

### deploy/ — Agent Runtime
- `deploy.sh`: deploys `step5_coordinator` with
  `adk deploy agent_engine --project --region us-central1
  --display_name "Research Assistant"`. Read project from an env var.
  Check `adk deploy agent_engine --help` on the pinned version for
  required flags (e.g. staging bucket) and `requirements.txt` handling.
- Add a `requirements.txt` inside `step5_coordinator/` if the deploy needs it.
- `query.py`: a short script that sends one message to the deployed agent
  and prints the reply. Use the current Vertex AI / Agent Platform SDK;
  check the docs for the right client calls.
- `deploy/README.md`: prerequisites (billing, Vertex AI API enabled,
  `gcloud auth application-default login`), the commands, and how to delete
  the deployment afterwards to avoid cost.

## README.md

- Setup in under 5 commands (venv, install, copy `.env.example`, `adk web`).
- One section per step: what it teaches (one sentence), the demo prompt,
  and what to point at in `adk web`.

## How to work

- Build **one step at a time**. After each step, run it (`adk run <folder>`
  with the demo prompt), show me the output, and wait for my go-ahead.
- Keep a short `NOTES.md` of API surprises or version gotchas you hit; I
  will turn these into speaker notes.