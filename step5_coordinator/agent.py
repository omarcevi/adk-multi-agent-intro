"""Step 5: a coordinator LLM decides which helper handles each request."""

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import exit_loop, google_search

# from google.adk.tools import AgentTool  # for the alternative below

MODEL = "gemini-2.5-flash"

# --- Helper 1: quick answers -------------------------------------------
# The coordinator reads each helper's description to decide who gets
# the request, so every description must say clearly what it is for.
quick_answer = Agent(
    name="quick_answer",
    model=MODEL,
    description="Answers simple questions directly in a few sentences.",
    instruction="Answer the user's question in 2 to 3 plain sentences.",
)

# --- Helper 2: web research, then the step 4 pipeline (copied) ---------
# google_search is a Gemini built-in tool: the model runs real Google
# searches itself. Gemini can't mix it with other tools in one agent,
# so this agent gets only this one tool.
web_researcher = Agent(
    name="web_researcher",
    model=MODEL,
    instruction=(
        "Search the web for the latest facts on the user's topic. Reply "
        "with 5 to 7 short bullets, each naming its source site. No intro."
    ),
    tools=[google_search],
    output_key="research",
)

first_draft_writer = Agent(
    name="first_draft_writer",
    model=MODEL,
    instruction=(
        "Write a quick first draft of a brief (about 150 words) on the "
        "topic, using only these research notes:\n\n{research}"
    ),
    output_key="draft",
)

critic = Agent(
    name="critic",
    model=MODEL,
    instruction=(
        "You are a strict editor. Review this draft:\n\n{draft}\n\n"
        "Approve it only if it has a title, is under 200 words and ends "
        "with a one-line takeaway. If it passes, call exit_loop and say "
        "nothing else. Otherwise, list up to 3 specific fixes."
    ),
    tools=[exit_loop],
    output_key="feedback",
)
reviser = Agent(
    name="reviser",
    model=MODEL,
    instruction=(
        "Rewrite the draft using the feedback. Reply with the new draft "
        "only.\n\nDraft:\n{draft}\n\nFeedback:\n{feedback}"
    ),
    output_key="draft",
)
improve_loop = LoopAgent(
    name="improve_loop",
    sub_agents=[critic, reviser],
    max_iterations=3,  # always bound loops
)
brief_pipeline = SequentialAgent(
    name="brief_pipeline",
    description=(
        "Searches the web, then writes a polished, reviewed brief or "
        "report on a topic."
    ),
    sub_agents=[web_researcher, first_draft_writer, improve_loop],
)

# --- The coordinator ----------------------------------------------------
front_desk = Agent(
    name="front_desk",
    model=MODEL,
    instruction=(
        "You are the front desk of a research assistant. Do not answer "
        "yourself. Hand each request to the best helper."
    ),
    sub_agents=[quick_answer, brief_pipeline],  # <- KEY LINE
)

# Alternative: call quick_answer as a TOOL instead of handing over.
# With AgentTool, control returns to front_desk after the answer.
# With sub_agents, the helper takes over the conversation.
#
# front_desk = Agent(
#     name="front_desk",
#     model=MODEL,
#     instruction="Use quick_answer for simple questions.",
#     tools=[AgentTool(agent=quick_answer)],
#     sub_agents=[brief_pipeline],
# )

root_agent = front_desk
