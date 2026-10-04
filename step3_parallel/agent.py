"""Step 3: three researchers at once (fan-out), then one writer (gather)."""

from google.adk.agents import Agent, ParallelAgent, SequentialAgent

MODEL = "gemini-2.5-flash"
STYLE = "Use what you know. Reply with 3 to 4 short bullets, no intro."

# Rule: parallel agents must not depend on each other. Each one only
# needs the user's topic, and each saves to its OWN output_key.
background = Agent(
    name="background_researcher",
    model=MODEL,
    instruction="Research the history and background of the topic. " + STYLE,
    output_key="background",
)
current_state = Agent(
    name="current_state_researcher",
    model=MODEL,
    instruction="Research where the topic stands today. " + STYLE,
    output_key="current_state",
)
future_outlook = Agent(
    name="future_outlook_researcher",
    model=MODEL,
    instruction="Research the future outlook for the topic. " + STYLE,
    output_key="future_outlook",
)

# The writer runs after ALL three finish and reads their results.
writer = Agent(
    name="writer",
    model=MODEL,
    instruction=(
        "Merge these notes into one brief of about 200 words, with a "
        "title.\n\nBackground:\n{background}\n\n"
        "Today:\n{current_state}\n\nFuture:\n{future_outlook}"
    ),
    output_key="brief",
)

research_team = ParallelAgent(
    name="research_team",
    sub_agents=[background, current_state, future_outlook],  # <- KEY LINE
)

root_agent = SequentialAgent(
    name="brief_pipeline",
    sub_agents=[research_team, writer],  # fan out first, then gather
)
