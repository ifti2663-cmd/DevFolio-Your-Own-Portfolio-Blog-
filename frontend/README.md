# DevFolio frontend

The React + Vite client for a single-owner developer portfolio and Markdown blog. It has a Developer Terminal design direction: Space Grotesk headings, DM Mono interface text, deep neutral surfaces, and a green accent.

## Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

`VITE_API_URL` must point to the deployed API's `/api` base path. Run `npm run build` before deployment.

## Routes

Public: `/`, `/about`, `/projects`, `/projects/:slug`, `/blog`, `/blog/:slug`, `/contact`, and the intentionally unlinked `/login`.

Owner-only: `/dashboard`, `/dashboard/posts`, `/dashboard/posts/new`, `/dashboard/posts/:slug/edit`, `/dashboard/projects`, `/dashboard/skills`, `/dashboard/experience`, `/dashboard/taxonomy`, `/dashboard/comments`, `/dashboard/messages`, and `/dashboard/profile`.

## Design tokens

| Token family | Choice |
| --- | --- |
| Fonts | Space Grotesk, DM Mono |
| Accent | `--accent` green, with a dedicated dark-mode value |
| Spacing | 8 / 16 / 24 / 32 / 48 / 64 / 96 px |
| Radii | 8 / 16 / 24 px |
| Surface and type | Defined once in `src/styles/tokens.css` |

All portfolio content comes from the API through React Query; no identity, project, skill, post, or social data is bundled in source code. Axios centrally attaches JWT and visitor identity headers, and refreshes a token once after a 401.

## Screenshots

Capture and add real screenshots after your actual profile content is entered: home in light and dark modes, blog list, post detail, and dashboard.

## With more time

Add richer dashboard table search, chart visualisation, API test coverage, and deployment automation. Replace this repository-relative backend link with your public backend repository URL before submitting: `../backend`.
