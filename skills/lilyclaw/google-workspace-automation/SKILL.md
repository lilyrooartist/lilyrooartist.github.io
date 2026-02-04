---
name: google-workspace-automation
description: "Automate Google Forms/Sheets workflows for Lily Roo (mailing list, contact, lightweight CRM) using Chrome Browser Relay: create forms, add validation, publish, link response spreadsheets, and retrieve share links. Use when building or editing Google Forms/Sheets pipelines."
---

# Google Workspace Automation (Forms/Sheets)

## Default account
- Use the Lily Roo Google account when available.

## Preferred method
- Use Chrome Browser Relay (profile="chrome").
- If control fails: restart gateway (commands.restart=true) and re-attach the tab.

## Create a mailing list form (standard)
1) Create new form.
2) Title: “Lily Roo Mailing List”.
3) Description: privacy-respecting, what they get.
4) Single question:
   - Label: “Email address”
   - Type: Short answer
   - Required: ON
   - Validation: must be Email
5) Responses → link to a new spreadsheet.
6) Publish and copy the responder link.

## Create a contact form (standard)
- Keep email off-site; use a Google Form.
- Fields: name (optional), email (optional), message (required).

## References
- `references/forms-templates.md`
