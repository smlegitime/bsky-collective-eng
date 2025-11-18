LABELER_DEFINITION = """Labelers are third-party moderation services on the Bluesky social media app. They work by assigning a set of labels/tags (manually or automatically) to accounts and posts.

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

COMMUNITY_GUIDELINES = """
# Community guidelines \
- Respectful communication \
- No hate speech, bigotry, or discrimination \
- No sensitive information (e.g., address, social security number) \
- No explicit content, spam, or content that is not related to decentralized social media, bluesky, or labelers \
"""