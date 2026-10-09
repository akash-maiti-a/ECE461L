// Backend stubs.
//
// The real backend doesn't exist yet. Every function here returns fake data
// from memory after a short delay, so the UI behaves as if it were talking
// to a server. Each function's comment describes the endpoint we plan to
// build, so swapping in real fetch() calls later only touches this file.
//
// Data resets when the page reloads.

const FAKE_DELAY_MS = 300;

// Planned database: a "users" collection. The real backend must store a
// hashed password, never the plaintext (SR2). This stub keeps plaintext in
// memory only because it never leaves the browser.
const users = new Map([['demo', 'demo123']]);

// Planned database: a "projects" collection.
const projects = new Map([
  [
    'film-01',
    {
      projectId: 'film-01',
      name: 'Spring short film',
      description: 'Five-minute short for the Texas Film Club showcase.',
      ownerUserid: 'demo',
    },
  ],
]);

// Planned database: a "hardware" collection, one document per set.
// The kit contents are placeholders for the team to replace with real gear.
const hardware = [
  {
    setId: 'HWSet1',
    name: 'Camera kits',
    capacity: 10,
    available: 7,
    contents: ['Mirrorless camera body', '24–70mm zoom lens', 'Three batteries and a charger', 'Two 128 GB SD cards', 'Fluid-head tripod'],
  },
  {
    setId: 'HWSet2',
    name: 'Audio and lighting kits',
    capacity: 8,
    available: 8,
    contents: ['Shotgun mic with boom pole', 'Field recorder', 'Wired lav mic', 'Two LED panels with stands', 'Sandbags and gaffer tape'],
  },
];

function respond(value) {
  return new Promise((resolve) => setTimeout(() => resolve(JSON.parse(JSON.stringify(value))), FAKE_DELAY_MS));
}

function fail(message) {
  return new Promise((_, reject) => setTimeout(() => reject(new Error(message)), FAKE_DELAY_MS));
}

// Planned endpoint: POST /api/auth/signup  { userid, password }
//   201 { userid }  |  409 if the user ID is taken
export function signUp(userid, password) {
  if (users.has(userid)) {
    return fail('That user ID is taken. Try another one.');
  }
  users.set(userid, password);
  return respond({ userid });
}

// Planned endpoint: POST /api/auth/signin  { userid, password }
//   200 { userid }  |  401 if the user ID or password is wrong
export function signIn(userid, password) {
  if (users.get(userid) !== password) {
    return fail('User ID or password is incorrect.');
  }
  return respond({ userid });
}

// Planned endpoint: POST /api/projects  { projectId, name, description, ownerUserid }
//   201 project  |  409 if the project ID is taken
export function createProject(project) {
  if (projects.has(project.projectId)) {
    return fail('That project ID is taken. Pick a different one.');
  }
  projects.set(project.projectId, project);
  return respond(project);
}

// Planned endpoint: GET /api/projects/:projectId
//   200 project  |  404 if no project has that ID
export function getProject(projectId) {
  const project = projects.get(projectId);
  return project ? respond(project) : fail(`No project has the ID "${projectId}".`);
}

// Planned endpoint: GET /api/hardware
//   200 [{ setId, name, capacity, available, contents }]
export function getHardware() {
  return respond(hardware);
}

// Planned endpoint: POST /api/hardware/checkout  { projectId, setId, quantity }
//   200 updated hardware list  |  409 if not enough kits are on the shelf
// The real version must check and decrement in one database operation so
// two people can't check out the last kit at the same time.
export function checkOut(projectId, setId, quantity) {
  const set = hardware.find((hw) => hw.setId === setId);
  if (!set) return fail(`Unknown hardware set "${setId}".`);
  if (quantity > set.available) {
    return fail(`Only ${set.available} ${set.name.toLowerCase()} are on the shelf.`);
  }
  set.available -= quantity;
  return respond(hardware);
}

// Planned endpoint: POST /api/hardware/checkin  { projectId, setId, quantity }
//   200 updated hardware list  |  409 if returning more than the project has out
// The real version should track checkouts per project so a project can only
// return what it borrowed. This stub just caps availability at capacity.
export function checkIn(projectId, setId, quantity) {
  const set = hardware.find((hw) => hw.setId === setId);
  if (!set) return fail(`Unknown hardware set "${setId}".`);
  set.available = Math.min(set.capacity, set.available + quantity);
  return respond(hardware);
}
