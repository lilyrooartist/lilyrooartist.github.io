# AOL to Gmail Bridge

## Goal
Copy new mail from `lilyroo.artist@aol.com` into `lilyroo.artist@gmail.com` without relying on AOL auto-forwarding or Gmail's deprecated POP fetch path.

## Why This Setup
- AOL does not currently offer automatic forwarding from AOL Mail.
- AOL supports IMAP access with an app password.
- Gmail's legacy "check mail from other accounts" POP retrieval is no longer a good foundation.
- The bridge copies raw message bytes into Gmail through IMAP, which preserves original headers better than re-sending messages through SMTP.

## Local Secret File
Create this file outside the repo:

```bash
../secrets/aol-gmail-bridge.env
```

Template:

```bash
AOL_EMAIL=lilyroo.artist@aol.com
AOL_APP_PASSWORD=replace-with-aol-app-password
AOL_IMAP_HOST=imap.aol.com
AOL_IMAP_PORT=993
AOL_MAILBOX=INBOX

GMAIL_EMAIL=lilyroo.artist@gmail.com
GMAIL_APP_PASSWORD=replace-with-gmail-app-password
GMAIL_IMAP_HOST=imap.gmail.com
GMAIL_IMAP_PORT=993
GMAIL_MAILBOX=INBOX

STATE_PATH=../secrets/aol-gmail-bridge-state.json
```

Keep this file mode `600`:

```bash
chmod 600 ../secrets/aol-gmail-bridge.env
```

To paste app passwords through a local-only browser form instead of editing the file manually:

```bash
python3 scripts/aol_gmail_bridge_setup_helper.py
```

Then open `http://127.0.0.1:4189`.

## First Run
Initialize state without copying old AOL mail:

```bash
scripts/aol_gmail_bridge_run.sh
```

Copy existing unread AOL messages instead:

```bash
scripts/aol_gmail_bridge_run.sh --copy-existing unread
```

Preview before copying:

```bash
scripts/aol_gmail_bridge_run.sh --copy-existing unread --dry-run
```

## Recurring Run
After app passwords are stored and the first run succeeds, schedule:

```bash
scripts/aol_gmail_bridge_run.sh
```

Run it every 5 to 15 minutes. The bridge tracks AOL UIDs in `../secrets/aol-gmail-bridge-state.json` so messages are not copied twice.

On this Mac, install the guarded LaunchAgent. It keeps one local runner alive and checks AOL every 5 minutes:

```bash
scripts/install_aol_gmail_bridge_launchd.sh
```

The installer refuses to run until both app passwords are present. It copies the runtime into `~/Library/Application Support/LilyRoo/AOLGmailBridge` so macOS launchd can run it outside the Documents privacy boundary. It writes logs to:

```bash
~/Library/Application Support/LilyRoo/AOLGmailBridge/aol-gmail-bridge.log
```

## Credential Notes
- AOL app password: create from AOL Account Security while signed in as `lilyroo.artist@aol.com`.
- Gmail app password: create from the Google Account for `lilyroo.artist@gmail.com`.
- Gmail IMAP must be enabled for the Gmail account.
- Do not commit app passwords, state files, or copied email metadata.
