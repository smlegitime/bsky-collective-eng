"""
Feedback Agent

This agent infers user intent, gives feedback, asks for user permission before saving feedback.
"""

from typing import Literal
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from langchain.agents import create_agent, AgentState
from langgraph.types import Command
from langchain.agents.middleware import HumanInTheLoopMiddleware

from models.custom_schema import LabelValueDefinition, Locale
from src import model # Claude model defined in package __init__

# ---- SYSTEM PROMPT AND STATE ----

FEEDBACK_AGENT_PROMPT = """
When the user wants to create a label, first interpret their intent and provide feedback 
on the proposed label configuration before saving it.

When the user asks for feedback on an existing label, use get_label to retrieve it, 
then analyze and provide suggestions on:
- Whether the severity level matches the content type
- If the blur settings are appropriate for the topic
- Whether the default_setting balances safety and user experience
- If the locale text is clear, accurate, and non-judgmental
- Potential edge cases or unintended consequences

Extract and infer for new labels:
- identifier: a snake_case identifier derived from the label's purpose
- severity: 'alert' (harmful content), 'inform' (informational), or 'none' (neutral)
- blurs: 'content' (blur entire post), 'media' (blur images/videos), or 'none'
- default_setting: 'hide' (hidden by default), 'warn' (shown with warning), or 'ignore' (shown normally)
- locales: name and description in the user's language

After interpreting a new label request, explain your reasoning for each choice and ask 
if they'd like to adjust anything before saving.

Only use create_label once the user confirms or if they explicitly ask to save it.
Use get_label to check if an identifier already exists before creating.
"""

class CustomState(AgentState):
    labels: dict[str, LabelValueDefinition]


# ---- TOOLS ----

@tool
def get_label(
    identifier: str,
    runtime: ToolRuntime
) -> LabelValueDefinition | Exception:
    """Retrieves an existing label value definition. Returns label or error if not found."""
    try:
        labels = runtime.state.get('labels', {})
        label = labels.get(identifier)

        if label is None:
            return f"Label '{identifier}' not found. Available labels: {', '.join(labels.keys()) if labels else 'none'}"
        return label
    except Exception as e:
        return f"Error retrieving label '{identifier}': {str(e)}"
    
@tool
def create_label(
    runtime: ToolRuntime,
    identifier: str,
    blurs: Literal['content', 'media', 'none'] = 'none',
    severity: Literal['alert', 'inform', 'none'] = 'inform',
    default_setting: Literal['hide', 'warn', 'ignore'] = 'ignore',
    locales: list[Locale] = None
) -> Command:
    """Creates a new label definition and stores it in state."""

    locale_objects = [
        Locale(lang=loc.lang, name=loc.name, description=loc.description)
        for loc in locales
    ]

    label = LabelValueDefinition(
        identifier=identifier,
        blurs=blurs,
        severity=severity,
        default_setting=default_setting,
        locales=locale_objects
    )

    return Command(
        update={
            'labels': {identifier: label},
            'messages': [
                ToolMessage(
                    f"Successfully created label '{identifier}'",
                    tool_call_id=runtime.tool_call_id
                )
            ]
        }
    )

# ---- AGENT DEFINITION ----

feedback_agent = create_agent(
    model=model,
    tools=[get_label, create_label],
    state_schema=CustomState,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"create_label": True}, # all decisions allowed (approve, edit, reject)
            description_prefix="Label definition pending approval"
        )
    ]
)