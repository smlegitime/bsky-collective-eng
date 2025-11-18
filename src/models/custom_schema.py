from pydantic import BaseModel, Field
from typing import Literal
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