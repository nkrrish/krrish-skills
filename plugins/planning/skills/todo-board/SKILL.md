---
name: todo-board
description: Use when the user types /todo-board, asks for a todo, task, or kanban board for the current project, or wants to add, move, list, review, finish, or reopen cards on a project's existing board.
---

# Todo Board

A three column board (Todo, Review, Done) published as a private Artifact with a shared database. One board per project. The page is a finished template with drag and drop, a card view, a header toolbar with live search, an owner filter and a tag filter; this skill only creates it and drives its cards.

## Column meaning

| Column | Means |
|---|---|
| `todo` | Agreed, not finished. |
| `review` | Built and believed complete. Waiting for a human to try it. |
| `done` | Tested, pushed, and deployed or tagged. Only the user decides this. |

## Where the board is recorded

`<project root>/.claude/todo-board.json`, committed to the repo:

```json
{ "title": "Acme Board", "subtitle": "Payments API work", "url": "https://claude.ai/code/artifact/…", "createdAt": "2026-09-02" }
```

When the session hook has already put the board URL in context, that is enough. Otherwise read this file. Either way, drive the board at that `url`. Do not publish again unless the user asks for a page change.

## Finding the board from a new chat

Artifacts belong to the person who published them, not to the chat that made them, so every chat that person opens can reach the board through its URL. Someone else can read the board only after the owner shares it from the page's share menu, and can never publish over it. Three things make finding it automatic:

1. **The record file** above. Every read and write passes its `url` to the Artifact tool. That works from any chat.
2. **The session hook.** `session-start-hook` in this skill's directory reads the record file when a session starts and puts the board title and URL into context. It is registered once per machine as a user level `SessionStart` command hook pointing at that script (see `README.md` in this skill's directory for the snippet). When a new chat starts in a project with a board and no such context arrived, the hook did not run on this machine (not registered, or `jq` or `git` missing). Say so once per chat, point to `README.md` in this skill's directory, do not edit `settings.json` yourself, and continue from the record file.
3. **The project note.** Creating a board appends a short section to the project's `CLAUDE.md` naming the board and its record file, so machines without the hook still learn about it.

When the record file is missing, run the Artifact tool with `action: "list"` and `scope: "all"` before creating anything, and look for a title `<project name> Board`. One marked mine: rewrite the record file from it and continue. One marked shared: rewrite the record file, read it, and tell the user only the owner can change the page. None: create the board. A `read_db` or `write_db` that fails with a permission or not found error on a recorded URL means the board exists and is not shared with this person. Report that and ask them to get it shared. Never create a second board because the first could not be read.

## Creating a board

1. **Title** is `<project name> Board`. Project name, in order: the name the user used in the request, then the product's own name (README heading, app display name, package name), then the folder name with hyphens as spaces and each word capitalised. **Subtitle** is one short phrase for what the board tracks, from the request; when the request gives nothing, `Project work`. **Slug** is the project name lowercased with hyphens.
2. Copy `board.html` from this skill's directory to the scratchpad and replace every `{{TITLE}}`, `{{SUBTITLE}}`, and `{{SLUG}}`. Change nothing else. The lime board mark, palette, Instrument Serif title, system body font, and layout are final, so skip the `artifact-design` skill.
3. Read the copied file in full (the Artifact tool requires it for a file you did not write) and load the `artifact-capabilities` skill once (the tool requires it before passing `capabilities`).
4. Publish with the Artifact tool: `capabilities: {"db": {}}`, `favicon: "🟢"`, a one sentence `description`. Omit `contract`.
5. Write `.claude/todo-board.json` with the returned URL.
6. Append this section to the project's `CLAUDE.md` (create the file if absent), with the title filled in:

   ```markdown
   ## Todo board

   This project has a todo board, "<title>". Its link is in `.claude/todo-board.json`. Use the todo-board skill to show it or change cards. Never publish a second board for this project.
   ```
7. Seed the cards the user asked for. A brand new board is empty, so skip the read and start numbering at 1.
8. Reply with the card table (see Output) and the link.

## Card schema

Collection `cards`. The document key is the card number as a string, and the `id` field always equals it.

```json
{
  "id": "3", "number": 3,
  "title": "Export a note as PDF",
  "summary": "One line shown on the card face.",
  "blockedBy": "1, 2",
  "owner": "agent",
  "tags": ["Product", "UX"],
  "details": "## Heading\n\nParagraph.\n\n- bullet\n- **bold** and `code`",
  "column": "todo", "order": 30,
  "createdAt": "2026-09-02T10:00:00.000Z", "updatedAt": "2026-09-02T10:00:00.000Z"
}
```

- `title`: the user's words, trimmed to one line and put in the imperative ("exporting a note as PDF" becomes "Export a note as PDF").
- `summary` and `details` hold what the user said and what the conversation established. When the user gave only a title, `summary` and `details` are empty strings. Do not invent scope.
- `details` renders only `##` headings, `-` bullets, `**bold**`, and `` `code` ``.
- `blockedBy`: comma separated card numbers or an empty string. Never edited by a move. The page shows the chip green by itself once the blocker is in `done`.
- `owner`: `agent` or `user`. `agent` is work Claude does in the codebase. `user` is work only the person can do: testing, deciding, deploying, writing copy, talking to someone. A card the user says they will handle themselves is `user`. When nothing says otherwise, `agent`. Always write the field. The page shows it as an icon on the card face and in the card view (a person for User, a sparkle for Agent), and the header filter (All, User, Agent) hides the other kind.
- `tags`: an array of short labels, usually one, at most three. Always write the field, `[]` when none fits. Use this vocabulary unless the user names another tag: `Infra` (servers, deploys, backups, monitoring, CI), `Product` (features inside the app), `UX` (flows, copy and polish inside the app, onboarding), `Website` (marketing site, SEO pages, pricing page), `Marketing` (launch, content, comparison pages, waitlist), `Compliance` (Meta App Review, policies, legal pages), `Business` (entity, bank, email, trademark, support, pricing decisions), `Billing` (Stripe, plans, caps, dunning). Same spelling every time; the page's dropdown lists each distinct spelling separately. The page shows tags as chips on the card face, edits them in the card view and the new card form as a comma separated field, and filters on one tag from the toolbar dropdown alongside the owner filter.
- `order`: sorts within a column, ascending.
- Timestamps come from `date -u +%Y-%m-%dT%H:%M:%S.000Z`, one value per user message that writes, shared by every write in it. A read only message needs none.

## Driving the board

One `read_db` `list` on `cards` per user message with `query: {"limit": 1000}`, following `next_cursor` until it is exhausted. Later operations in the same message account for earlier ones in memory, including columns emptied or filled by an earlier move. A card named in prose is matched by title; when two cards match or none does, ask before writing. Then:

| Request | Action |
|---|---|
| `/todo-board`, "show the board" | Output the card table and the link. |
| `add <title>`, "add a card for …" | `set` with `number` = highest existing + 1, `column` `todo`, `order` = highest order in `todo` + 10, or 10 when empty. A prerequisite that is not on the board goes in as its own card first, and the dependent card names it in `blockedBy`. |
| `review <n>`, `todo <n>`, "move 3 to review" | `update` on `cards/<n>` with `column`, `order` = highest order in the target column + 10 (10 when empty), and a fresh `updatedAt`. |
| `done <n>` | Same as a move. Only the literal request moves a card to `done`. "Finished", "pushed", "shipped", or "move it along" go to `review`, and a card already in `review` stays there. The reply says Done is theirs to call and names any card it would unblock. Take the user's word for what was pushed; do not check git. When a blocker reaches `done`, name the cards it unblocks. |
| `edit <n>`, "update card 3 to say …" | `update` with only the changed fields plus `updatedAt`. |
| `mine <n>`, "that one is on me", "assign 3 to me" | `update` with `owner` `user` and `updatedAt`. "Give 3 back to you" or `agent <n>` sets `owner` `agent`. |
| "show my tasks", "what is on me" | The card table filtered to `owner` `user`. "Your tasks" or "agent tasks" filters to `agent`. |
| `tag <n> Infra`, "tag 3 as Product and UX" | `update` with the full new `tags` array (existing tags plus the named ones, deduplicated) and `updatedAt`. "Untag 3 Infra" removes one. "Retag 3 as Billing" replaces the array. |
| "show Infra cards", "what is left on the website" | The card table filtered to cards whose `tags` include that tag, case insensitive. Combines with an owner filter when both are named. |
| "tag the board", "add tags to every card" | Read every card, choose tags from the vocabulary by title, summary and details, and write them in batches of 50. Reply with the table so the user can correct any. |
| `delete <n>` | Confirm with the user, then `delete`. |
| `open`, "link" | The URL from `.claude/todo-board.json`. |

Two or more writes in one message go in a single `batch`.

## Output

After any change: one line per card changed, saying what happened. Then a markdown table with number, title, tags (comma separated, blank when none), owner (User or Agent), column (Todo, Review, Done), and blocked by (blank when none), rows ordered by column Todo, Review, Done and then by `order`. Then the link. Copy in cards and replies uses periods and commas, never em or en dashes.

## Changing the page

A page change is a change to `board.html` in this skill, then a publish per board with `url` from that project's `.claude/todo-board.json`, omitting `favicon` and `capabilities` so the icon and database are kept. Read the artifact with `action: "read"` and that `url` first: the Artifact tool refuses to publish over a page this chat has not read. Publishing without `url` from a chat that did not create the board makes a second artifact.

## Common mistakes

- Numbering from a partial list. A page of results is not the whole collection.
- Using a column count for `order`. Orders are never compacted, so a count collides after a move. Use highest order plus 10.
- Moving your own finished work to `done`. It goes to `review`.
- Writing markdown the page does not render (tables, links, numbered lists, `###`). Use bullets.
- Inventing a tag when one in the vocabulary fits, or varying the spelling (`infra`, `Infrastructure`). The dropdown treats each spelling as its own tag.
- Putting the board URL in memory instead of `.claude/todo-board.json`. Memory is per user, the file is per project.
- Publishing from a new chat without `url`, or without reading the artifact first. Either one produces a second board or a refused publish.
