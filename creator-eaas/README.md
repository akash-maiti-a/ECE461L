# Frontend (React)

The Creator EaaS web page. It gets all of its data from the Flask API in
`../server`.

## Run

Start the API first, in its own terminal. See `../server/README.md` for
setup. `USE_MOCK_DB=1` runs it without installing MongoDB:

```bash
cd server
USE_MOCK_DB=1 .venv/bin/python app.py
```

Then start the page:

```bash
cd creator-eaas
npm install
npm start
```

Open http://localhost:3000. The dev server forwards every `/api/...` request
to Flask on port 5001 (the `proxy` setting in `package.json`).

If the shelf says "Count unavailable", the API isn't running. The browser
console says which request failed.

## Test

```bash
npm test
```

The tests don't need the API running:

- `src/App.test.js` replaces `src/api` with Jest mocks and checks what the
  page shows for each kind of reply.
- `src/api/index.test.js` replaces `fetch` and checks the exact request
  each API function sends, plus how errors are reported.

## How it's organized

| File | Job |
|---|---|
| `src/api/index.js` | The only code that talks to the backend. One function per endpoint. |
| `src/App.js` | The shell: header, footer, sign-in dialog. Tracks who's signed in, which page is showing, and the open project. |
| `src/pages/LandingPage.js` | The front page: hero with the live shelf, how borrowing works, kit contents. |
| `src/pages/ProjectsPage.js` | Start a new project or join one by ID. |
| `src/pages/ProjectPage.js` | One project: its shelf per kit, and check-out and check-in controls. |
| `src/components/ShelfBoard.js` | The shelf drawing (`Slots`), the landing page's shelf board, and the "Count unavailable" state. |
| `src/components/AuthDialog.js` | The sign-in and new-user dialog. |
| `src/useSessionState.js` | Keeps sign-in and the current page across a refresh (per browser tab). |
| `src/App.css` | All styles. Colors and fonts are variables at the top, with a dark-mode set. |

## Deploying

Build with the backend's public URL so the page knows where to send requests:

```bash
REACT_APP_API_URL=https://your-api.example.com npm run build
```

The `build/` folder can then be served by any static host, such as Vercel or
Netlify.
