"""Step 2: two agents in a fixed order (an assembly line)."""

from google.adk.agents import Agent, SequentialAgent

MODEL = "gemini-2.5-flash"

# Agent 1 gathers facts. output_key saves its final answer in session
# state under "research", so the next agent can read it.
researcher = Agent(
    name="researcher",
    model=MODEL,
    description="Lists key facts about a topic.",
    instruction=(
        "You are a researcher. Using what you already know, list 5 to 7 "
        "key facts about the topic the user asks about, as short bullet "
        "points. Facts only, no introduction."
    ),
    output_key="research",
)

# Agent 2 writes the brief. ADK replaces {research} with the value from
# session state before the instruction is sent to the model.
writer = Agent(
    name="writer",
    model=MODEL,
    description="Turns research notes into a short brief.",
    instruction=(
        "You are a writer. Turn these research notes into a brief of "
        "about 150 words, with a title.\n\n"
        "Research notes:\n{research}"
    ),
    output_key="brief",
)

# A SequentialAgent has no LLM of its own. It runs its sub-agents in order.
root_agent = SequentialAgent(
    name="brief_pipeline",
    description="Researches a topic, then writes a brief.",
    sub_agents=[researcher, writer],  # <- KEY LINE: runs in this order
)
