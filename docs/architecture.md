# GhostNote Architecture

This document captures the architectural decisions, design philosophy, and long-term direction of GhostNote.

It exists to preserve important decisions over time, reduce repeated discussions, and keep future development aligned with the project's vision.

Unlike implementation notes or GitHub Issues, this document focuses on decisions that should remain true across multiple releases.

---

# GhostNote Architecture & Product Philosophy

## Purpose

GhostNote is a local-first Windows utility that makes invisible engineering work visible with the least possible friction.

It exists because fast-paced technical work is often completed, context-switched away from, and forgotten before it can be documented for:

- 1:1 meetings
- Performance reviews
- Promotion discussions
- Resume updates
- Weekly status meetings

GhostNote does not record activity.

It preserves meaningful work before it is forgotten.

---

## Current State (v1)

GhostNote v1 is feature complete.

Current architecture:

- Python 3
- Tkinter desktop UI
- SQLite database
- Local AppData storage
- Windows installer
- Right-click desktop integration
- Single executable with CLI modes
- Local-first operation

---

## Core Philosophy

- Capture first. Organize later.
- Fast capture is more important than perfect structure.
- Ugly but useful beats polished but slow.
- The tool should work how engineers actually behave.
- Hidden work should become visible without becoming productivity tracking.
- The user remains the source of truth.
- AI may assist recall but should never automatically decide what work happened.

---

## Product Boundary

GhostNote is not:

- A productivity tracker
- A time tracker
- A journaling application
- Spyware
- Employee monitoring software
- Surveillance software

GhostNote is:

- Operational visibility for hidden work
- A lightweight capture utility
- A personal work evidence tool
- A memory aid
- A way to prepare for reviews, promotions, raises, and resumes

---

## Product Test

Every future feature should answer one question:

> Does this help the user remember hidden work, or does it attempt to tell the user what they did?

If it helps users recall context or reduce forgotten work, it belongs.

If it moves toward surveillance, productivity metrics, automatic attribution, or employee monitoring, it does not.

---

## Success Criteria

GhostNote succeeds when:

- Capturing work takes less than five seconds.
- Users naturally build a work history.
- Hidden work becomes visible.
- Review preparation becomes easier.
- Promotion preparation no longer depends on memory.
- Engineers remain in flow while documenting meaningful work.

---

## Technical Stack

Current:

- Python 3
- Tkinter
- SQLite
- PyInstaller
- Inno Setup
- PowerShell (Windows integration)

Avoid:

- Web applications
- Cloud sync
- Authentication
- Accounts
- Electron
- Enterprise architecture
- Complex abstractions
- Databases beyond SQLite

---

## Storage

SQLite is the authoritative local datastore.

User data is stored under the user's AppData directory.

GhostNote supports export to human-readable formats while keeping SQLite as the operational database.

Current exports:

- CSV
- Markdown

Future exports may include:

- TXT
- PDF
- Reports

---

## Database

Current core tables:

- entries
- settings
- metadata

The metadata table stores database-level information including schema versioning and creation metadata to support future database migrations.

Current user-facing Categories are stored internally as tags.

---

## Terminology

GhostNotes
: Individual captured entries.

Echoes
: AI-generated summaries.

Signals
: High-impact work identified from captured history.

---

## CLI Philosophy

GhostNote packages as a single executable.

Current supported modes:

```
GhostNote.exe
GhostNote.exe new
GhostNote.exe viewer
```

Future CLI functionality may expand while maintaining the single-executable philosophy.

---

## Background Service

Future reminders should run as a separate process.

Preferred architecture:

```
Background Service
    -> launches popup
    -> launches export
    -> launches AI
```

Avoid embedding all functionality into one long-running process.

---

## Popup Reuse

Every capture path should reuse the same popup.

```
Right Click
Background Service
Global Hotkey
Reminder
Future AI

        ↓

PromptWindow

        ↓

sqlite_store.add_entry()
```

No duplicate popup implementations.

---

## AI Direction

AI is intentionally deferred.

Future AI may:

- Summarize GhostNotes
- Generate weekly Echoes
- Suggest promotion evidence
- Suggest resume bullets
- Identify Signals
- Build reports

AI should assist recall—not replace user judgment.

---

## Future Integrations

Potential integrations include:

- Slack
- Email
- Calendar
- Zoom
- GitHub / Git
- Linear

Integrations should always be:

- Optional
- Transparent
- User-controlled

Their purpose is recall—not monitoring.

---

## UI Philosophy

GhostNote should remain utility-focused.

Prioritize:

- Speed
- Readability
- Timeline view
- Search
- Filtering
- Quick editing
- Fast capture

Avoid dashboard-style interfaces.

---

## Monetization

The free version should always remain genuinely useful.

Likely free:

- Capture
- Viewer
- Search
- Filtering
- Export

Likely paid:

- AI summaries
- Integrations
- Advanced reporting
- Promotion evidence
- Resume generation

Paid features should build on captured data rather than restrict capture itself.

---

## Explicitly Deferred

- AI summaries
- AI capture assistance
- Screenshot attachments
- Advanced tagging
- Resume exports
- Promotion exports
- Deep integrations

---

## Rejected

GhostNote intentionally avoids:

- Accounts
- Cloud-first design
- Electron
- Web applications
- Multi-user architecture
- Productivity scoring
- Employee monitoring
- Hidden data collection

---

## Privacy

GhostNote should never collect data that would make it feel like spyware.

Avoid:

- Keystroke logging
- Screen recording
- Password capture
- Clipboard history by default
- Browser history by default
- Email contents by default
- Employee metrics

Future context collection must always be user-controlled and transparent.

---

## Product Loop

```
Capture
      ↓
Visibility
      ↓
Recognition
      ↓
More Capture
```

GhostNote should periodically prove its value back to users through summaries, reports, and evidence.

That positive feedback loop encourages continued capture.