import { fireEvent, render, screen, within } from '@testing-library/react';
import App from './App';
import * as api from './api';

// The page tests replace src/api with Jest mocks, so they don't depend on a
// running backend or on any built-in data. Each test says what the "server"
// returns. The real request code has its own tests in src/api/index.test.js.
jest.mock('./api');

const HARDWARE = [
  { setId: 'HWSet1', name: 'Camera kits', capacity: 10, available: 7, contents: ['Camera body'] },
  { setId: 'HWSet2', name: 'Audio and lighting kits', capacity: 8, available: 8, contents: ['Field recorder'] },
];

// Create React App resets mocks before every test, so set the default
// responses here rather than once at the top.
beforeEach(() => {
  api.getHardware.mockResolvedValue(HARDWARE);
});

// Renders the page and waits for the shelf to load, so no state updates
// land after a test has finished.
async function renderApp() {
  render(<App />);
  const shelf = screen.getByRole('figure', { name: 'Kits on the shelf right now' });
  await within(shelf).findByText('Camera kits');
  return shelf;
}

function fillIn(label, value) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

function openSignIn() {
  fireEvent.click(screen.getAllByRole('button', { name: 'Sign in' })[0]);
}

function submitDialog(buttonName) {
  fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: buttonName }));
}

const PROJECT = {
  projectId: 'film-01',
  name: 'Spring short film',
  description: 'Five-minute short for the showcase.',
  ownerUserid: 'alice',
  checkedOut: {},
};

// Signs in as alice and waits for the project picker.
async function signInToProjects() {
  api.signIn.mockResolvedValue({ userid: 'alice' });
  await renderApp();
  openSignIn();
  fillIn('User ID', 'alice');
  fillIn('Password', 'pw-123');
  submitDialog('Sign in');
  await screen.findByRole('heading', { name: 'Open a project', level: 1 });
}

function form(name) {
  return screen.getByRole('form', { name });
}

test('shelf board shows kit counts from the API', async () => {
  const shelf = await renderApp();
  expect(shelf).toHaveTextContent('7 of 10 on the shelf');
  expect(shelf).toHaveTextContent('8 of 8 on the shelf');
});

test('when the shelf count fails to load, Try again loads it', async () => {
  api.getHardware.mockRejectedValueOnce(new Error('The server isn’t responding right now.'));
  render(<App />);

  expect(await screen.findByRole('alert')).toHaveTextContent('kit counts can’t be shown right now');

  fireEvent.click(screen.getByRole('button', { name: 'Try again' }));

  const shelf = screen.getByRole('figure', { name: 'Kits on the shelf right now' });
  await within(shelf).findByText('Camera kits');
  expect(shelf).toHaveTextContent('7 of 10 on the shelf');
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(api.getHardware).toHaveBeenCalledTimes(2);
});

test('signing in opens the project picker', async () => {
  api.signIn.mockResolvedValue({ userid: 'alice' });
  await renderApp();

  openSignIn();
  fillIn('User ID', 'alice');
  fillIn('Password', 'pw-123');
  submitDialog('Sign in');

  expect(await screen.findByRole('heading', { name: 'Open a project', level: 1 })).toBeInTheDocument();
  expect(screen.getByRole('banner')).toHaveTextContent('Signed in as alice');
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(api.signIn).toHaveBeenCalledWith('alice', 'pw-123');
});

test('a rejected sign-in shows the server’s message and keeps the dialog open', async () => {
  api.signIn.mockRejectedValue(new Error('User ID or password is incorrect.'));
  await renderApp();

  openSignIn();
  fillIn('User ID', 'alice');
  fillIn('Password', 'not-it');
  submitDialog('Sign in');

  expect(await screen.findByRole('alert')).toHaveTextContent('User ID or password is incorrect.');
  expect(screen.getByRole('dialog')).toBeInTheDocument();
});

test('creating an account signs the new user in', async () => {
  api.signUp.mockResolvedValue({ userid: 'new-crew' });
  await renderApp();

  fireEvent.click(screen.getByRole('button', { name: 'Create an account' }));
  fillIn('User ID', 'new-crew');
  fillIn('Password', 'pw-123');
  fillIn('Confirm password', 'pw-123');
  submitDialog('Create an account');

  expect(await screen.findByRole('heading', { name: 'Open a project', level: 1 })).toBeInTheDocument();
  expect(screen.getByRole('banner')).toHaveTextContent('Signed in as new-crew');
  expect(api.signUp).toHaveBeenCalledWith('new-crew', 'pw-123');
});

test('mismatched passwords are caught before anything is sent', async () => {
  await renderApp();

  fireEvent.click(screen.getByRole('button', { name: 'Create an account' }));
  fillIn('User ID', 'typo-crew');
  fillIn('Password', 'one');
  fillIn('Confirm password', 'two');
  submitDialog('Create an account');

  expect(screen.getByRole('alert')).toHaveTextContent('The passwords don’t match.');
  expect(api.signUp).not.toHaveBeenCalled();
});

test('the dialog switches between sign in and new user', async () => {
  await renderApp();

  openSignIn();
  const dialog = screen.getByRole('dialog');
  expect(within(dialog).queryByLabelText('Confirm password')).not.toBeInTheDocument();

  fireEvent.click(within(dialog).getByRole('button', { name: 'Create an account' }));
  expect(within(dialog).getByLabelText('Confirm password')).toBeInTheDocument();
});

test('creating a project opens it', async () => {
  api.createProject.mockResolvedValue(PROJECT);
  await signInToProjects();

  const create = form('Start a new project');
  fireEvent.change(within(create).getByLabelText('Project name'), { target: { value: 'Spring short film' } });
  fireEvent.change(within(create).getByLabelText('Description'), { target: { value: 'Five-minute short for the showcase.' } });
  fireEvent.change(within(create).getByLabelText('Project ID'), { target: { value: ' film-01 ' } });
  fireEvent.click(within(create).getByRole('button', { name: 'Create project' }));

  expect(await screen.findByRole('heading', { name: 'Spring short film' })).toBeInTheDocument();
  expect(api.createProject).toHaveBeenCalledWith({
    projectId: 'film-01',
    name: 'Spring short film',
    description: 'Five-minute short for the showcase.',
    ownerUserid: 'alice',
  });
});

test('joining a project by ID opens it', async () => {
  api.getProject.mockResolvedValue(PROJECT);
  await signInToProjects();

  const join = form('Join a project');
  fireEvent.change(within(join).getByLabelText('Project ID'), { target: { value: 'film-01' } });
  fireEvent.click(within(join).getByRole('button', { name: 'Open project' }));

  expect(await screen.findByRole('heading', { name: 'Spring short film' })).toBeInTheDocument();
  expect(api.getProject).toHaveBeenCalledWith('film-01');
});

test('joining an unknown project shows the server’s message', async () => {
  api.getProject.mockRejectedValue(new Error('No project has the ID "nope".'));
  await signInToProjects();

  const join = form('Join a project');
  fireEvent.change(within(join).getByLabelText('Project ID'), { target: { value: 'nope' } });
  fireEvent.click(within(join).getByRole('button', { name: 'Open project' }));

  expect(await within(join).findByRole('alert')).toHaveTextContent('No project has the ID "nope".');
});

test('signing out returns to the landing page', async () => {
  await signInToProjects();

  fireEvent.click(screen.getByRole('button', { name: 'Sign out' }));

  expect(await screen.findByRole('heading', { name: /Camera, audio, and lighting kits/ })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Create an account' })).toBeInTheDocument();
});
