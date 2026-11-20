# Tombstone — Resurrect the Dead Web

Turn a vanished page into a searchable research card with dated, inspectable source evidence.

## Run on Windows, macOS, or Linux

Extract the ZIP, open its `tombstone` folder, run `python app.py` with Python 3.11+ and visit http://127.0.0.1:8000. No dependencies or API keys are required. Select **Try sample** to use the bundled fictional capture. Save it, reload, search for “moths,” and export the match to Markdown.

To use live mode, paste a public HTTP(S) URL or import a bookmarks HTML, TXT, or CSV file. Review the first five unique URLs and submit. The server optionally checks the original site, asks the Wayback Availability API for its closest capture, and attempts to extract readable text. An upstream restriction can result in a capture link with no excerpts. Capture dates and source-supplied publication dates have separate fields. Sample cards always carry an offline sample label.

To run the tests, use `python -m unittest discover -s tests -v`. JavaScript syntax checks use `node --check web/app.js` and `node --check extension/popup.js`.

## Architecture

The static browser interface calls a single Python JSON route. The runtime pipeline normalizes the URL, checks origin health, retrieves capture metadata, extracts normalized paragraphs, selects three excerpts, and returns numbered citations. The sample uses the same extraction and card construction code. The browser stores cards in localStorage and exports directly to a Markdown file. There are no accounts, server-side card storage, or model credentials.

| Method and path | Input | Response |
|---|---|---|
| GET /api/health | None | `{"ok":true}` |
| POST /api/restore | `{"url":"https://fieldnotes.example/urban-moths"}` | `{"state":"restored","health":"dead","demo":true,...}` |

Restore states include restored, partial, missing, unavailable, and blocked. Invalid JSON or URLs return 400, invalid size 413, wrong media type 415, and exhausted quota or capacity 429. The app accepts 15 attempts per minute per direct client IP and serves up to four in-flight restoration requests. Reverse proxies may share one quota.

Each card has a normalized original URL, status, title, optional author and publication date, capture date, source URL, and evidence items `{id, quote}`. Highlight IDs refer to evidence in the same card. The local library uses normalized original URL as its key. One saved version per URL is supported.

## Privacy and deployment

Bookmark files are parsed on-device. Submitting a live URL sends it to the archive provider and can disclose embedded query parameters. Use public links and remove credentials or sensitive parameters. Original-site checks resolve and pin public addresses and apply the same validation to redirects. The browser renders extracted content as text and opens source links separately. Remove cards from the library or clear site storage to delete local data.

For a prototype deployment, build the included Dockerfile and run it with port 8000 mapped locally. A Docker-capable host must allow outbound HTTPS to Internet Archive and expose the app over HTTPS. Use TLS, connection and request limits at the proxy, and outbound restrictions at the host. The built-in HTTP server is for local and prototype use. Server-side data backup is unnecessary; export local cards to keep a readable copy. Roll back deployment by redeploying the previous image.

Load `extension/` as an unpacked extension in Chromium Developer mode. With the app running locally, use its popup on a web page. The extension opens the desk with the URL prefilled for review.

## Hackathon materials

See [Kiroween guide](docs/kiroween-guide.md) and [Kiro specs](.kiro/specs/tombstone). Kiro configuration is prepared for use in the IDE. Record real Kiro sessions and other development evidence before writing the final submission.

### Vercel

Import the repository with the Other framework preset and repository root as the root directory. The checked-in build command publishes the web assets from `dist` and Vercel serves the Python endpoints in `api/`. No environment variables are required. Set `TOMBSTONE_CHECK_ORIGINS=0` to disable direct origin checks and do archive lookup only. The local server's in-memory quota is local-only. Configure request limits at the hosting layer for larger public usage.
