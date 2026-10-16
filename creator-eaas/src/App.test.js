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

test('shelf board shows kit counts from the API', async () => {
  const shelf = await renderApp();
  expect(shelf).toHaveTextContent('7 of 10 on the shelf');
  expect(shelf).toHaveTextContent('8 of 8 on the shelf');
});

test('shows a message when the shelf count fails to load', async () => {
  api.getHardware.mockRejectedValue(new Error('Could not reach the server.'));
  render(<App />);

  expect(await screen.findByRole('alert')).toHaveTextContent('The shelf count didn’t load.');
});

test('signing in shows who is signed in', async () => {
  api.signIn.mockResolvedValue({ userid: 'alice' });
  await renderApp();

  openSignIn();
  fillIn('User ID', 'alice');
  fillIn('Password', 'pw-123');
  submitDialog('Sign in');

  expect(await screen.findByRole('status')).toHaveTextContent('signed in as alice');
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

  expect(await screen.findByRole('status')).toHaveTextContent('signed in as new-crew');
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
