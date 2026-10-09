import { fireEvent, render, screen, within } from '@testing-library/react';
import App from './App';

// These tests run against the backend stubs in src/api, so they cover the
// real components with fake data. The stubs keep state for the whole test
// file, so each test uses its own user ID.

function fillIn(label, value) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

test('shelf board shows kit counts from the API', async () => {
  render(<App />);

  const shelf = await screen.findByRole('figure', { name: 'Kits on the shelf right now' });
  expect(await within(shelf).findByText('Camera kits')).toBeInTheDocument();
  expect(shelf).toHaveTextContent('7 of 10 on the shelf');
  expect(shelf).toHaveTextContent('8 of 8 on the shelf');
});

test('signing in with the demo account shows who is signed in', async () => {
  render(<App />);

  fireEvent.click(screen.getAllByRole('button', { name: 'Sign in' })[0]);
  fillIn('User ID', 'demo');
  fillIn('Password', 'demo123');
  fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Sign in' }));

  expect(await screen.findByRole('status')).toHaveTextContent('signed in as demo');
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});

test('a wrong password shows an error and keeps the dialog open', async () => {
  render(<App />);

  fireEvent.click(screen.getAllByRole('button', { name: 'Sign in' })[0]);
  fillIn('User ID', 'demo');
  fillIn('Password', 'not-it');
  fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Sign in' }));

  expect(await screen.findByRole('alert')).toHaveTextContent('User ID or password is incorrect.');
  expect(screen.getByRole('dialog')).toBeInTheDocument();
});

test('creating an account signs the new user in', async () => {
  render(<App />);

  fireEvent.click(screen.getByRole('button', { name: 'Create an account' }));
  fillIn('User ID', 'new-crew');
  fillIn('Password', 'pw-123');
  fillIn('Confirm password', 'pw-123');
  fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Create an account' }));

  expect(await screen.findByRole('status')).toHaveTextContent('signed in as new-crew');
});

test('mismatched passwords are caught before anything is sent', () => {
  render(<App />);

  fireEvent.click(screen.getByRole('button', { name: 'Create an account' }));
  fillIn('User ID', 'typo-crew');
  fillIn('Password', 'one');
  fillIn('Confirm password', 'two');
  fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Create an account' }));

  expect(screen.getByRole('alert')).toHaveTextContent('The passwords don’t match.');
});

test('the dialog switches between sign in and new user', () => {
  render(<App />);

  fireEvent.click(screen.getAllByRole('button', { name: 'Sign in' })[0]);
  const dialog = screen.getByRole('dialog');
  expect(within(dialog).queryByLabelText('Confirm password')).not.toBeInTheDocument();

  fireEvent.click(within(dialog).getByRole('button', { name: 'Create an account' }));
  expect(within(dialog).getByLabelText('Confirm password')).toBeInTheDocument();
});
