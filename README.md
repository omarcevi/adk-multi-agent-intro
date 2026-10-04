# Multi-Agent Research Assistant (Google ADK)

Code for a talk on multi-agent architecture with Google ADK 2.x. One
research assistant grows step by step, from a single agent to a
coordinator that chooses between pipelines.

## Setup

You need Python 3.11+ and a free key from
[Google AI Studio](https://aistudio.google.com/apikey).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your key into .env
adk web                # open http://localhost:8000
```

Pick a step from the dropdown in the top-left corner of `adk web`.

## step1_single_agent: what is an agent?

An agent is an LLM plus instructions plus tools it can call.

- Demo prompt: `What's today's date, and what day of the week is it?`
- Point at: the `get_current_date` function-call and function-response
  events. The model can't know the date, so it has to ask the tool.

## step2_sequential: assembly line

A `SequentialAgent` runs agents in a fixed order, passing work along
through session state.

- Demo prompt: `Write a brief on electric cars in Turkey.`
- Point at: the State tab. `research` appears after the researcher
  finishes, then `brief` after the writer.

## step3_parallel: fan-out and gather

A `ParallelAgent` runs independent agents at the same time, then a writer
merges their results.

- Demo prompt: `Write a brief on electric cars in Turkey.`
- Point at: the three researchers finishing in a different order each
  run, then `background`, `current_state` and `future_outlook` in State.

## step4_loop: writer and critic

A `LoopAgent` repeats critic and reviser until the critic approves or
`max_iterations` is reached.

- Demo prompt: `Write a brief on electric cars in Turkey.`
- Point at: `draft` being overwritten in State on each pass, and the
  critic's `exit_loop` call that ends the loop.

## step5_coordinator: the LLM decides

A coordinator reads each helper's `description` and hands the request to
the best one.

- Demo prompts: `What is an EV?` (goes to `quick_answer`) and
  `Write me a brief on EVs in Turkey` (goes to `brief_pipeline`).
- Point at: the `transfer_to_agent` call, and which agent it names.
- The brief pipeline starts with `web_researcher`, which uses Gemini's
  built-in `google_search`. Open its event to see the real search
  queries and source sites.
- Open the **Traces** tab to see each `call_llm` span with the exact
  prompt sent to the model.

## Deploy

See [deploy/README.md](deploy/README.md) to run step 5 on Agent Runtime.
