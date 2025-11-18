"""
Coordinator

This agent uses the hierarchical/supervisor design pattern, implemented via tool calling.
"""

from typing import Literal
from pydantic import BaseModel, Field
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model

from models.custom_schema import LabelValueDefinition, Locale
from feedback_agent import feedback_agent
from researcher_agent import researcher_agent

model = init_chat_model("gpt-4o-mini") # Different from model in init

# ---- SYSTEM PROMPT ----

labeler_definition = """Labelers are third-party moderation services on the Bluesky social media app. They work by assigning a set of labels/tags (manually or automatically) to accounts and posts.

All users on the platform can “subscribe” to one or more of these services and configure how they want these labels to affect their experience: for any label type, they can choose if the user/post 
marked with such label should be hidden from their view, just marked with a label, or if this kind of label should be ignored.

Labelers will usually be specialized in some area: they could be protecting their users from things such as racism, antisemitism, or homophobia; they could be automatically detecting some unwanted 
behaviors like following a huge number of people quickly; marking some specific types of accounts like new accounts without an avatar, or accounts from a different network; fighting disinformation 
or political extremism; or they could be serving a community using a specific language or from a specific country.

Labelers publish an /app.bsky.labeler.service/self record to declare that they are a labeler and publish their policies. 
As an example, a record for a labeler that warns users blurs media about spiders on feeds and profiles looks like this:

{
  "$type": "app.bsky.labeler.service",
  "policies": {
    "labelValues": ["porn", "spider"],
    "labelValueDefinitions": [
      {
        "identifier": "spider",
        "severity": "alert",
        "blurs": "media",
        "defaultSetting": "warn",
        "locales": [
          {"lang": "en", "name": "Spider Warning", "description": "Spider!!!"}
        ]
      }
    ]
  },
  "subjectTypes": ["record"],
  "subjectCollections": ["app.bsky.feed.post", "app.bsky.actor.profile"],
  "reasonTypes": ["com.atproto.moderation.defs#reasonOther"],
  "createdAt": "2024-03-03T05:31:08.938Z"
}

The "labelValues" declares what to expect from the Labeler. It may include global and custom label values.

The "labelValueDefinitions" defines the custom labels. It includes the locales field for specifying human-readable copy in various languages. If the user\'s language is not found, it will use the first set of strings in the array.

"subjectTypes", "subjectCollections", and "reasonTypes" declare what type of moderation reports are reviewed by the Labeler. subjectTypes can include record for individual pieces of content, and account for overall accounts. subjectCollections is a list of NSIDs of record types; if not defined, any record type is allowed. reasonTypes is a list of report reason codes (Lexicon references).
"""

community_guidelines = """
# Community guidelines \
- Respectful communication \
- No hate speech, bigotry, or discrimination \
- No sensitive information (e.g., address, social security number) \
- No explicit content, spam, or content that is not related to decentralized social media, bluesky, or labelers \
"""

COORDINATOR_AGENT_PROMPT = """ You are an expert assistant, who assists the user in brainstorming ideas for a labeler for the Bluesky social media app.
For context, here is information about the Bluesky labeler: {labeler_definition}.

Before you reply to a user message, ensure that the message follows these community guidelines {community_guidelines}.
If the message does not follow the community guidelines, respond by listing the community guidelines and asking the user to try again.

If a user asks for the conversation summary, return a brief chronological summary of the current conversation between you and the user.

You can retrieve additional context from a knowledge base to help answer user queries and provide feedback on newly created or existing labels.
Break down user requests into appropriate tool calls and coordinate the results.
When a request involves multiple actions, use multiple tools in sequence.
"""

# Custom state for agent
class CustomState(AgentState):
    labels: dict[str, LabelValueDefinition]

# ---- TOOLS ----

@tool
def retrieve_additional_context(query: str) -> str:
    """Retrieve additional context about labelers from user query.
    
    Use this when the user asks for information about Bluesky that you don't have immediate context for.
    Handles retrieval of additional context from knowledge base.
    
    Input: Natural language query (e.g., 'what are Bluesky labelers?')
    """

    result = researcher_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    return result['messages'][-1].content

@tool
def provide_feedback_on_label(request: str) -> str:
    """Interpret user intent when the user wants to create a label, then provide feedback on 
    the proposed label configuration before saving it.

    Use this when the user wants to create, modify, or get feedback on a label.

    Input: Natural language request for label creation or for getting feedback on label. 
    (e.g., 'i want to make a label to tag posts that show misinformation')
    """

    result = feedback_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })

    return result['messages'][-1].content

# ---- AGENT DEFINITION ----

coordinator_agent = create_agent(
    model=model,
    tools=[retrieve_additional_context, provide_feedback_on_label],
    system_prompt=COORDINATOR_AGENT_PROMPT
)