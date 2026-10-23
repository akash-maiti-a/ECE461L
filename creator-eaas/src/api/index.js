// The only place the frontend talks to the backend.
//
// Each function sends one request to the Flask API (see server/README.md for
// the full contract) and returns the parsed JSON. Components never deal with
// URLs, headers, or status codes: on success they get data, on failure they
// get an Error whose message is ready to show the user.
//
// In development, npm start forwards /api requests to Flask on port 5001
// (see src/setupProxy.js), so BASE_URL is empty. For a
// deployed build, set REACT_APP_API_URL to the backend's public URL.
const BASE_URL = process.env.REACT_APP_API_URL || '';

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    });
  } catch {
    throw new Error('Can’t reach the server. Check your connection and try again.');
  }

  // Every reply from our Flask code is JSON. A reply that isn't came from
  // something in between (the dev proxy when Flask is stopped, a hosting
  // gateway, or a crash page), so the API itself isn't answering.
  let data;
  try {
    data = await response.json();
  } catch {
    if (process.env.NODE_ENV === 'development') {
      console.error(`${path} returned a non-JSON reply. Is the Flask API running on port 5001?`);
    }
    throw new Error('The server isn’t responding right now. Try again in a minute.');
  }

  // Errors from Flask look like {"error": "..."}; pass that message along.
  if (!response.ok) {
    throw new Error(data.error || `Something went wrong (error ${response.status}). Try again.`);
  }
  return data;
}

function post(path, body) {
  return request(path, { method: 'POST', body: JSON.stringify(body) });
}

// POST /api/auth/signup  { userid, password }
//   201 { userid }  |  409 if the user ID is taken
export function signUp(userid, password) {
  return post('/api/auth/signup', { userid, password });
}

// POST /api/auth/signin  { userid, password }
//   200 { userid }  |  401 if the user ID or password is wrong
export function signIn(userid, password) {
  return post('/api/auth/signin', { userid, password });
}

// GET /api/projects
//   200 [{ projectId, name, ownerUserid }], sorted by name
export function listProjects() {
  return request('/api/projects');
}

// POST /api/projects  { projectId, name, description, ownerUserid }
//   201 project  |  409 if the project ID is taken
export function createProject({ projectId, name, description, ownerUserid }) {
  return post('/api/projects', { projectId, name, description, ownerUserid });
}

// GET /api/projects/:projectId
//   200 project (including checkedOut, e.g. { HWSet1: 3 })  |  404 if no project has that ID
export function getProject(projectId) {
  return request(`/api/projects/${encodeURIComponent(projectId)}`);
}

// GET /api/hardware
//   200 [{ setId, name, capacity, available, contents }]
export function getHardware() {
  return request('/api/hardware');
}

// POST /api/hardware/checkout  { projectId, setId, quantity }
//   200 updated hardware list  |  409 if not enough kits are on the shelf
export function checkOut(projectId, setId, quantity) {
  return post('/api/hardware/checkout', { projectId, setId, quantity });
}

// POST /api/hardware/checkin  { projectId, setId, quantity }
//   200 updated hardware list  |  409 if returning more than the project has out
export function checkIn(projectId, setId, quantity) {
  return post('/api/hardware/checkin', { projectId, setId, quantity });
}
