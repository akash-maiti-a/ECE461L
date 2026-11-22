# Project Overview

Creator Equipment as a Service is a web application that helps students and campus organizations manage shared media equipment. Users can create an account and project, view available equipment, check out items for a project, and check them back in when finished.

For our proof of concept, HWSet1 represents camera kits and HWSet2 represents audio and lighting kits. The application will show each set's total capacity and current availability, with the option to add more equipment types later.

## Running Locally

The app has two parts, each with its own README:

- [`server/`](server/README.md): the Flask API and MongoDB data. Run it first, on port 5001.
- [`creator-eaas/`](creator-eaas/README.md): the React page. `npm start` serves it on port 3000 and forwards `/api` requests to the server.

## Deploying

The app deploys as **one service**: the `Dockerfile` builds the React page,
and Flask serves it next to the API at one URL. Keeping one URL means the
sign-in cookie always reaches the API (#37). Deploying needs a free MongoDB
Atlas cluster for the data and a free Render web service to run the app.

**1. MongoDB Atlas (the database)**

1. Create a free (M0) cluster.
2. Under **Database Access**, add a database user with a password.
3. Under **Network Access**, allow access from anywhere (`0.0.0.0/0`). Render's
   free plan has no fixed IP address to allow instead.
4. Under **Connect > Drivers**, copy the connection string
   (`mongodb+srv://...`) and put the user's password into it. Keep it private:
   it's the database password.

**2. Render (runs the app)**

1. Sign in to render.com with GitHub. Render needs access to this repository,
   which its owner grants.
2. Choose **New > Blueprint** and pick this repository. Render reads
   `render.yaml`.
3. When asked for `MONGO_URI`, paste the Atlas connection string. Render
   generates `SECRET_KEY` and `USERID_ENCRYPTION_KEY` itself. Never change
   them once accounts exist, or those accounts can't sign in.
4. When the deploy finishes, open the service's URL and check that
   `/api/health` returns `"status": "ok"`.

The free plan sleeps when nobody has used it for a while, so the first visit
afterward can take about a minute. Open the app before a demo or before
handing the URL to the TAs.

**3. After the first deploy**

Put the URL at the top of this README, run through the TA test cases on it,
then close #19 and #37.

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
| Cloud hosting | Make the app accessible to the instructor and TAs in a later phase. |

## Product Features



### User Stories

User Stories can be found in the Issues tab under this repository


### Technical Debt




### Research Items




## High Level Sketch
![Sketch](pics/sketch.png)
