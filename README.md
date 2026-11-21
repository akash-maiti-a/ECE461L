# Project Overview

Creator Equipment as a Service is a web application that helps students and campus organizations manage shared media equipment. Users can create an account and project, view available equipment, check out items for a project, and check them back in when finished.

For our proof of concept, HWSet1 represents camera kits and HWSet2 represents audio and lighting kits. The application will show each set's total capacity and current availability, with the option to add more equipment types later.

## Running Locally

The app has two parts, each with its own README:

- [`server/`](server/README.md): the Flask API and MongoDB data. Run it first, on port 5001.
- [`creator-eaas/`](creator-eaas/README.md): the React page. `npm start` serves it on port 3000 and forwards `/api` requests to the server.

## Live App

**URL:** _add the Render (or Heroku) URL here once deployed_

The deployed app is one service: Flask serves both the API and the React build, so the page and the API share one URL and the sign-in cookie always works.

### Deploying (Render, free plan)

1. In MongoDB Atlas, under **Network Access**, allow `0.0.0.0/0` (Render's free plan has no fixed outbound IP).
2. On [render.com](https://render.com), choose **New > Blueprint** and pick this repo. Render reads `render.yaml`.
3. When asked for `MONGO_URI`, paste the Atlas connection string. Render generates `SECRET_KEY` and `USERID_ENCRYPTION_KEY`; never change them after accounts exist, or those accounts can't sign in.
4. When the deploy finishes, open the `onrender.com` URL and check `/api/health`. Put the URL above and share it with the instructor and TAs.

Render's free plan sleeps after 15 idle minutes, so the first visit after a break takes about a minute.

**Heroku instead:** `heroku create`, `heroku stack:set container`, `heroku config:set MONGO_URI=... SECRET_KEY=... USERID_ENCRYPTION_KEY=...`, then `git push heroku main`. Heroku builds the same `Dockerfile` (see `heroku.yml`).

**Locally, the way the cloud runs it:** `docker build -t creator-eaas .` then `docker run -p 8000:8000 -e USE_MOCK_DB=1 -e SESSION_COOKIE_SECURE=0 creator-eaas`, and open http://localhost:8000.

## Project Plan

### Team Members

Kavi Daliparti, Akash Maiti, Shreyas Kumar, Saharsh Lavu, Sanjay Senthil

### Sprint Cadence

We plan to work in one-week sprints. At the beginning of each sprint, we will choose tasks from our GitHub Project board and assign them to team members. At the end of each sprint, we will review completed work and plan the next sprint.

Our initial estimated velocity is 6–8 story points per sprint. We will adjust this estimate after the first sprint based on how much work we actually complete.

### Collaboration and methodology

We will use an Agile approach. GitHub will hold our shared code and documentation, and a GitHub Project board will track planned work. We will use GitHub Issues to track bugs and improvements. Team members will review each other's changes through pull requests and meet regularly to discuss progress and blockers.

### Collaboration Tools

We will use Github, Google Docs, and iMessage as the main forms of collaboration, secondary collaboration tools include Gmail and other Google or Microsoft Suite technologies if needed.

### Implementation Methodology

The React frontend will send requests to the Flask API. The API will read and update information in MongoDB. We will organize account, project, and equipment functions separately so we can add more hardware sets later.

We will first build the required features for two hardware sets: HWSet1 (camera kits) and HWSet2 (audio and lighting kits). Users will be able to sign in, access a project, see equipment availability, and check equipment out and back in.

### Toolchain

| Tool | Planned use |
|---|---|
| React | Build the account, project, and equipment screens. |
| Python and Flask | Create an API for users, projects, equipment status, checkouts, and returns. |
| MongoDB | Store user, project, hardware, and checkout information. |
| PyTest | Test API functions and equipment availability updates. |
| GitHub | Store code and documents, review changes, and track tasks. |
| Docker, Render, and MongoDB Atlas | Host the app on the cloud at one public URL for the instructor and TAs. |

## Product Features

| Feature | Where it lives | Requirements |
|---|---|---|
| Sign in, and a New User pop-up for creating an account | `AuthDialog.js`, `routes/auth.py` | SR1 |
| User IDs encrypted and passwords hashed before storage | `userid_crypto.py`, `models/user.py` | SR2 |
| Create a project with a name, description, and project ID | `ProjectsPage.js`, `routes/projects.py` | SR3 |
| Use an existing project by entering its project ID | `ProjectsPage.js`, `routes/projects.py` | SR4 |
| Capacity and availability of HWSet1 and HWSet2, read from the database | `ShelfBoard.js`, `ProjectPage.js`, `routes/hardware.py` | SR5 |
| Enter how many kits to check out or check in | `ProjectPage.js` | SR6 |
| Check out and check in kits, with availability updated in the database | `routes/hardware.py`, `models/hardware.py` | SR7, SR8 |
| Users, projects, hardware, and checkout history in MongoDB behind a REST API | `server/models/`, `server/routes/` | SR9 |
| PyTest and Jest test suites | `server/tests/`, `creator-eaas/src/*.test.js` | SR10 |
| Hosted on the cloud at a public URL | `Dockerfile`, `render.yaml` | R2-3 |

### User Stories

User stories are GitHub Issues #5–#14 on the **Creator Equipment as a Service** project board. Bugs and needed improvements are tracked separately on the **Issues / Bugs** board.

### Technical Debt

- **Checkout and check-in aren't one transaction.** Each updates the hardware set and then the project in two steps, so a crash between them could make the counts drift. MongoDB transactions (available on Atlas) would fix this.
- **No way to leave a project or remove a member.** Anyone with a project's ID can join it, and membership is permanent.
- **CORS allows every origin.** Since the deployed app is served from one origin, CORS could be limited to the local dev server.
- **Hardware sets are seeded from code.** Adding HWSet3 means editing `Hardware.DEFAULT_SETS`; an admin page would be friendlier.

### Research Items

- **Cloud hosting (#19):** We chose one Docker image on Render, with Flask serving the React build. This keeps one URL and avoids cross-site cookie problems (#37). Heroku can build the same image.
- **Encrypting user IDs (#35):** A keyed HMAC lets sign-in look up an account, and Fernet encryption keeps the ID recoverable for admins. The database never holds the ID as typed.
- **Concurrent checkouts:** A conditional `update_one` (`available >= quantity`) makes sure two people can't both take the last kit.


## High Level Sketch
![Sketch](pics/sketch.png)
