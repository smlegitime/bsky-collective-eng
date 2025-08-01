sample_labeler_declaration = {
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