# Topic newsletter workflow

23 October 2026. In the local editor open **Source feed**, enter a topic such as “Latest developments in open-source AI models”, and refresh. This searches configured trusted RSS/Atom feeds only, not unrestricted internet search. Token matches rank headline evidence above descriptions; this is lexical relevance, not semantic proof. Current cached matches are reported, including zero results. Inspect publisher identity, URL and source dates, then select 1–8 stories and generate.

Generation uses the installed local `gemma4:e4b`, validates the existing structured schema, numeric/source references and attached provenance, and saves an unapproved DRAFT. Edits, previews, review and explicit approval are retained. Insufficient sources fail without fabricated news. `python tools/local_generate.py --topic "open-source models" --output PRIVATE_NEW_FILE.json` supports the same filtering; it never overwrites an existing draft.

Fresh actual verification: 47 configured-feed records, 29 topic matches, no collector errors; three Gemma items saved only to a separate private DRAFT database. [Recorded counts](portfolio-evidence/live-result.json). No real edition was reviewed, approved or published. Matching is bounded to the cached recent records and current feed metadata; dates/headlines can still be incomplete, and human factual review is required.
