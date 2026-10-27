# The Voice of Becoming Studio website (voiceofbecoming.com)

Static site, no framework. Everything deployable is in `site/`. `build.py` (plain Python 3) writes every page, so the
header and footer stay identical everywhere.

## Add an article (Fathima sends text, Tab posts)
1. Copy `content/posts/the-articulation-gap.md` to `content/posts/<short-url-name>.md`.
2. Edit the header: title, date (YYYY-MM-DD), summary (1-2 sentences, shown on cards), tag. Add `draft: true` to hide it.
3. Write the body below the `---` line: blank line between paragraphs, `## Heading`, `1. ` / `- ` lists, `**bold**`, `[link text](url)`.
4. Run `python3 build.py`, then republish `site/`.
   Newest date shows first; the home page shows the latest 2. With zero posts the Articles page shows "First articles coming soon".

## Add a talk or event
Edit `data/events.json` (one object per event: date, time, title, place, format, description, link, link_label), run
`python3 build.py`, republish. Empty list = "Upcoming talks will be announced here". Past dates move to "Past talks" on
the next build and are hidden from Upcoming in the browser automatically the day after.

## Build targets
- Real domain:   `python3 build.py`   (canonical/og URLs = https://voiceofbecoming.com)
- Tab preview:   `SITE_URL=https://vob-site.sites.tab.bot python3 build.py`
Tests: `node --test test/site.test.js` (footer links, no prices, no em dashes, no placeholders, no client names Bhavna/Shenomics).

## Key links used
Kit signup (workbook + newsletter): https://becoming-her-again-4.kit.com/042d6cefac
Clarity Call: https://topmate.io/fathima_samreen/504857 · Teardown: https://topmate.io/fathima_samreen/2368492
