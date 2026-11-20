# Kiroween 2026 | Tombstone

[Official rules](https://kiroween.devpost.com/rules) and [event page](https://kiroween.devpost.com/). New projects must be built from October 30 through December 4, 2026. The deadline is 10 p.m. UTC December 4, or 3:30 a.m. IST December 5. The 2026 video must be public on YouTube and under three minutes. Submit the application URL, public GitHub repository with an open-source license and tracked root .kiro directory, project description, category, and an honest Kiro write-up.

## Category and judging

Kiro is an AI development environment with an IDE, CLI, web app, and Crew. Its specs define requirements, steering supplies standing project rules, hooks run checks, and MCP adds external tools. Show how Kiro changed a concrete implementation decision and show the test that checks it.

| Category | Fit |
|---|---|
| Resurrection | Revive obsolete technology or a dead workflow. Tombstone revives access to disappeared web references. |
| Frankenstein | Join distinct technologies to solve a problem neither handles well alone. |
| Skeleton Crew | Demonstrate a reusable skeleton with two distinct applications. |
| Costume Contest | Build around a memorable spooky interface that improves the experience. |

Choose **Resurrection**. Researchers need traceable citations when a bookmark or bibliography link disappears. One restoration can show the original status, source capture, readable evidence, and reuse in a library. Show what happens when no snapshot exists or extraction is blocked. Avoid a video dominated by setup, vague AI claims, an unlabeled canned demo, or Kiro claims without concrete evidence.

## Product plan

| User | Problem | Outcome |
|---|---|---|
| Research student | A reference in a bibliography returns 404. | Recover a dated citation and keep it with research notes. |
| Journalist | A sourced article has changed or disappeared. | Inspect the dated capture and keep the relevant excerpt. |
| Developer | Old documentation moved and saved links broke. | Find a capture, verify the text, and save a searchable reference. |

The landing page opens directly on the restoration desk. Users paste URLs or import bookmarks, review the list, then see sequential progress and outcome cards. A restored card shows a capture date, publication date when known, source excerpts, and a source link. Saved cards can be filtered, exported, or removed. The extension opens the same desk for the active tab. The dark charcoal and violet theme uses bone text and amber accents, visible focus, a skip link, reduced-motion support, and status announcements. Success measures for a user trial include time to first source, restoration rate by failure class, and the percentage of citations users can reopen.

P0 implemented scope includes five-URL batches, origin classification, closest capture, extractive evidence, bookmark import, local search, Markdown export, and a sample. P1 priorities include a capture timeline, version diff, real browser testing in Kiro, and broader article extraction. P2 includes PDF import, semantic search, synchronized collections, sharing, and cited model synthesis. Capture histories and archived images should stay out of the demo until reliable. Prefer public or permissioned URLs and limit retained excerpts to what the workflow needs.

## Kiro sessions to run

| Role | Inputs and output | Guardrail and handoff |
|---|---|---|
| Archaeologist | Normalized URL → origin state, capture or lookup failure | Use public archive results and pass only validated capture data. |
| Restorer | Capture and URL → metadata and numbered text blocks | Treat HTML as untrusted. Return a partial result when text is unavailable. |
| Librarian | Metadata and numbered text → card and highlight IDs | Any future paraphrase requires linked evidence. |
| Verifier | Card and source excerpts → pass or reasons | Reject missing evidence references and date conflation. |
| Builder | Spec task and tests → changes and test output | Keep each change scoped and hand it to Reviewer. |
| Reviewer | Diff and acceptance tests → findings with severity | Check citations, accessibility, security, and regression behavior. |

The first four rows describe runtime responsibilities currently implemented as deterministic code. Use Builder and Reviewer as development sessions and give each a narrow task. Use Playwright MCP for the sample, narrow viewport, keyboard navigation, and export, with approval on any external action. Use GitHub MCP for read-only review or explicitly authorized pull requests. Keep MCP credentials out of the public repository. No Crew or MCP run is represented as completed here.

Prompts to use in Kiro

1. Compare the requirements, design, and tests and flag contradictions.
2. Add a mocked archive availability integration test covering a valid successful capture.
3. Review extraction on multilingual fixtures while preserving exact evidence.
4. Specify closest-capture ranking before adding timeline support.
5. Attach evidence to every proposed highlight and test that unresolved IDs fail.
6. Test keyboard navigation through import, restoration, and saving on a narrow viewport.
7. Review public-address validation and redirect handling defensively.
8. Evaluate bookmark import on realistic browser exports.
9. Run the restoration checks hook and capture its output with the relevant code change.
10. Review the final README and report only claims you can verify from code, logs, or a live run.

## Fourteen-day schedule

| Day | Goal |
|---|---|
| 1 | Review rules, open the repository in Kiro, and revise acceptance criteria. |
| 2 | Use Kiro to land a focused test-driven archive improvement. |
| 3 | Verify live captures from the intended deployment and log outcome classes. |
| 4 | Test redirects, malformed responses, missing captures, and extraction failures. |
| 5 | Improve readable evidence and metadata extraction on permitted fixtures. |
| 6 | Run mobile and keyboard checks with Playwright MCP. |
| 7 | Demonstrate one verified live capture plus the offline fixture, search, and export. |
| 8 | Cut timeline or diff if live restoration or accessibility still needs work. |
| 9 | Validate extension installation and public-bookmark handoff. |
| 10 | Run Reviewer session and reconcile findings. |
| 11 | Deploy a stable build, verify anonymous access, and document rollback. |
| 12 | Record the public YouTube demo using working flows. |
| 13 | Finish the description and Kiro write-up with evidence links. |
| 14 | Test all submission URLs from a signed-out browser and submit before cutoff. |

## Two-minute-thirty-second demo

| Time | Screen action | Narration |
|---|---|---|
| 0:00–0:20 | Show the restoration desk and a lost reference. | “A broken bookmark can take a source out of your research. Tombstone helps you recover what an archive captured and gives you a citation you can inspect.” |
| 0:20–0:50 | Click Try sample, then open the result. If a live URL has been verified, show it separately. | “I’m starting with a labeled fictional capture so you can see the workflow end to end. Tombstone takes the capture and builds a card with the original address and distinct publication and capture dates.” |
| 0:50–1:20 | Expand evidence, then open one source. | “Each highlight comes directly from the captured text and links back to the source. If the service finds a capture but can’t retrieve its text, Tombstone shows that partial result.” |
| 1:20–1:50 | Save the card, search for moths, and click Export Markdown. | “I can save this to my library on this device, find it again by searching its evidence, and export the citation and excerpts to my notes.” |
| 1:50–2:15 | Show one completed Kiro task and its test or hook output. | Describe the actual Kiro session and the behavior the resulting check verifies. |
| 2:15–2:30 | Return to the card and source link. | “When a link dies, the evidence can still be found, checked, and used. That’s Tombstone.” |

## Devpost copy and checklist

**Title** Tombstone — Resurrect the Dead Web  
**Tagline** Recover vanished links as searchable, source-cited research cards.

**Inspiration** A broken link in a bibliography can make a claim hard to verify. We wanted to make the archived evidence easier to find and reuse.

**What it does** Paste public links or import bookmarks. Tombstone checks the address, queries for a capture, and builds a card from the readable evidence. Save cards locally and export filtered results to Markdown.

**How it was built** Python, vanilla JavaScript and CSS, Wayback Availability API, localStorage, Chromium Manifest V3, and unittest. The app uses extractive highlights.

**How Kiro was used** Fill in the date, Kiro environment, task, code or spec change, and check output for each actual session. Capture a concrete example each for the tools you used. Add one sentence comparing free-form prompting and specs if both were used.

**Challenges** Archives can report a capture even when its text is inaccessible. We made a partial card with an explicit capture link so users can still inspect the source.

**Accomplishments** A repeatable demo, direct evidence links, dated provenance, import, searchable local storage, and Markdown export.

**What we learned** Capture availability and extractability are separate states, and publication and capture dates mean different things.

**What’s next** Capture comparisons, document import, and optional evidence-constrained synthesis.

Before submission verify anonymous app access, public GitHub, visible MIT license, tracked .kiro, public YouTube video under three minutes, selected Resurrection category, and a Kiro write-up backed by actual sessions. Blog outline: broken citation, design, real Kiro session, test evidence, limitations. Optional social draft begins with `#KiroweenHackathon26` and describes what actually changed during a Kiro session.

## Risks, scenarios, and alternatives

| Risk | Mitigation |
|---|---|
| Archive networking unavailable | Keep the offline fixture visible and verify a permissioned live URL from the deployed host. |
| Capture metadata exists without text | Return a partial card with a source link. |
| Extraction includes noise | Filter boilerplate and keep excerpts and source visible together. |
| Accidental private URL disclosure | Review imports before submission and explain third-party lookup. |
| Weak Kiro evidence | Keep meaningful specs and record actual edits, check output, and impact. |

Demo scenarios to rehearse include the sample, one confirmed 404 with capture, one live URL, one redirect, one no-snapshot case, one unreadable capture, two duplicate URLs, bookmark import review, a library search hit, and export of filtered cards. Live cases depend on the archive and should be verified shortly before recording.

Five details to show are date separation, numbered evidence, explicit partial results, on-device storage, and export with provenance. Alternate projects include a calendar and OCR inbox for Frankenstein, a media catalog starter with two small apps for Skeleton Crew, and an accessible haunted museum guide for Costume Contest.
