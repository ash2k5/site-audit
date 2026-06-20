# 2. the browser calls the api directly

- Status: accepted
- Date: 2026-06-20

## Context
A cold backend plus the scrape, PageSpeed, and LLM steps can run well past a minute. A Vercel server
action or route handler would hit the 60s function cap and return 504.

## Decision
The browser calls the API directly using `NEXT_PUBLIC_API_BASE_URL` (inlined at build), with a 150s
client-side fetch timeout. No server-side proxy.

## Consequences
The API base URL is public, which is fine for a public API. The API must allow CORS and expose
`Content-Disposition` for the PDF download. The only timeout ceiling is the client fetch.
