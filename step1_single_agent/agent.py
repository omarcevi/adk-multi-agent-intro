"""Step 1: a single agent with one tool."""

from datetime import date

from google.adk.agents import Agent

MODEL = "gemini-2.5-flash"


# A tool is just a Python function. ADK sends the name, type hints and
# docstring to the model so it knows when (and how) to call it.
def get_current_date() -> str:
    """Returns today's date, including the day of the week."""
    # e.g. "Sunday, 04 October 2026"
    return date.today().strftime("%A, %d %B %Y")


root_agent = Agent(
    name="date_assistant",
    model=MODEL,
    description="Answers questions about today's date.",
    # The model has no clock, so we tell it to use the tool instead.
    instruction=(
        "You are a helpful assistant. You do not know today's date. "
        "Always call get_current_date to find it before answering."
    ),
    tools=[get_current_date],  # <- KEY LINE: give the agent a tool
)

# Compare: the same agent WITHOUT the tool. Uncomment to swap it in.
# With no tool it can only guess the date from its training data
# (often wrong) or admit it doesn't know. No function call in adk web.

# root_agent = Agent(
#     name="date_assistant_no_tool",
#     model=MODEL,
#     description="Answers questions about today's date.",
#     instruction="You are a helpful assistant.",
# )
