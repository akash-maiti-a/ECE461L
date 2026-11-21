# Tools and Approach

| Tool | Planned use |
|---|---|
| React | Build the account, project, and equipment screens. |
| Python and Flask | Create an API for users, projects, equipment status, checkouts, and returns. |
| MongoDB | Store user, project, hardware, and checkout information. |
| PyTest | Test API functions and equipment availability updates. |
| GitHub | Store code and documents, review changes, and track tasks. |
| Docker, Render, and MongoDB Atlas | Host the app on the cloud at one public URL for the instructor and TAs. |

## Application Approach

The React frontend will send requests to the Flask API. The API will read and update information in MongoDB. We will organize account, project, and equipment functions separately so we can add more hardware sets later.

We will first build the required features for two hardware sets: HWSet1 (camera kits) and HWSet2 (audio and lighting kits). Users will be able to sign in, access a project, see equipment availability, and check equipment out and back in.

## Hosting

The app is deployed as one Docker image (see `Dockerfile`). The image builds the React page, and Flask serves it alongside the API, so the instructor and TAs use one URL and the sign-in cookie is never blocked as cross-site. Render runs the image from `render.yaml`. User, project, and hardware data live in MongoDB Atlas.
