from pydantic import BaseModel, Field
from typing import Literal, List
from pydantic import BaseModel

# Label Definition schema
class Locale(BaseModel):
    lang: str = Field(default='en', description='Language code (e.g., fr, en, es, sw)')
    name: str | None = Field(..., description='The name of the label') #required field
    description: str | None = Field(default=None, description='The description for the label')

class LabelValueDefinition(BaseModel):
    identifier: str = Field(..., description='Snake_case identifier for the label')
    blurs: Literal['content', 'media', 'none'] = Field(
        default='none',
        description='What to blur: content (entire post), media (images/video), or none ()'
    )
    severity: Literal['alert', 'inform', 'none'] = Field(
        default='inform',
        description='Severity level: alert (harmful), inform (informational), or none (neutral)'
    )
    default_setting: Literal['hide', 'warn', 'ignore'] = Field(
        default='ignore',
        description='Default visibility: hide (hidden), warn (shown with warning), or ignore (shown normally)'
    )
    locales: list[Locale] = Field(..., description='Label text in different languages')


# Labeller Definition schema
# NOTE: defaults have been taken from bsky docs to demonstrate format.
class Policies(BaseModel):
    labelValues: List[str] = Field(
        default=[], description="List of label names - e.g. ['porn', 'spider']"
    )
    labelValueDefinitions: List[LabelValueDefinition] = Field(
        default=[], description="List of label definitions."
    )

class Labeler(BaseModel):
    type: str = Field(
        default="app.bsky.labeler.service",
        description="Announces account as labeller.", 
        alias="$type"
    ) 
    policies: Policies
    subjectTypes: List[str] = Field(
        default=["record"],
        description= "subjectTypes can include 'record' for individual pieces of content, and 'account' for overall accounts."
    )
    subjectCollections: List[str] = Field(
        default=["app.bsky.feed.post", "app.bsky.actor.profile"],
        description="subjectCollections is a list of NSIDs of record types; if not defined, any record type is allowed"
    )
    reasonTypes: List[str] = Field(
        default=["com.atproto.moderation.defs#reasonOther"], 
        description="reasonTypes is a list of report reason codes (Lexicon references)."
    ) 
    createdAt: str = Field(
        ...,
        description="sample format: 2024-03-03T05:31:08.938Z"
    )