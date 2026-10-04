"""Step 4: a critic and a reviser improve a draft in a loop."""

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import exit_loop  # built-in tool that ends a loop

MODEL = "gemini-2.5-flash"

first_draft_writer = Agent(
    name="first_draft_writer",
    model=MODEL,
    instruction="Write a quick first draft of a short brief on the topic.",
    output_key="draft",
)

# The critic either approves (calls exit_loop) or writes feedback.
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

# The reviser overwrites "draft", so the critic sees the new version.
reviser = Agent(
    name="reviser",
    model=MODEL,
    instruction=(
        "Rewrite the draft using the feedback. Reply with the new draft "
        "only.\n\nDraft:\n{draft}\n\nFeedback:\n{feedback}"
    ),
    output_key="draft",
)

# When the critic calls exit_loop, the loop stops right away,
# so the reviser does not run after an approval.
improve_loop = LoopAgent(
    name="improve_loop",
    sub_agents=[critic, reviser],
    max_iterations=3,  # <- KEY LINE: always bound loops
)

root_agent = SequentialAgent(
    name="brief_pipeline",
    sub_agents=[first_draft_writer, improve_loop],
)
