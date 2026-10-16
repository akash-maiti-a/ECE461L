import { checkIn, checkOut, createProject, getHardware, getProject, signIn, signUp } from '.';

// These tests replace the browser's fetch with a Jest mock, so they check
// exactly what each function sends and how it handles the reply, without a
// running backend.

function reply(status, body) {
  global.fetch = jest.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  });
}

function sentRequest() {
  const [url, options = {}] = global.fetch.mock.calls[0];
  return {
    url,
    method: options.method || 'GET',
    body: options.body ? JSON.parse(options.body) : undefined,
    contentType: options.headers?.['Content-Type'],
  };
}

afterEach(() => {
  delete global.fetch;
});

describe('requests match the backend contract', () => {
  test('signUp', async () => {
    reply(201, { userid: 'alice' });
    await expect(signUp('alice', 'pw')).resolves.toEqual({ userid: 'alice' });
    expect(sentRequest()).toEqual({
      url: '/api/auth/signup',
      method: 'POST',
      body: { userid: 'alice', password: 'pw' },
      contentType: 'application/json',
    });
  });

  test('signIn', async () => {
    reply(200, { userid: 'alice' });
    await signIn('alice', 'pw');
    expect(sentRequest()).toMatchObject({
      url: '/api/auth/signin',
      method: 'POST',
      body: { userid: 'alice', password: 'pw' },
    });
  });

  test('createProject', async () => {
    const project = { projectId: 'doc-07', name: 'Doc', description: 'Short doc', ownerUserid: 'alice' };
    reply(201, { ...project, checkedOut: {} });
    await createProject(project);
    expect(sentRequest()).toMatchObject({ url: '/api/projects', method: 'POST', body: project });
  });

  test('getProject encodes the project ID in the URL', async () => {
    reply(200, {});
    await getProject('film club/01');
    expect(sentRequest()).toMatchObject({ url: '/api/projects/film%20club%2F01', method: 'GET' });
  });

  test('getHardware', async () => {
    const hardware = [{ setId: 'HWSet1', name: 'Camera kits', capacity: 10, available: 10 }];
    reply(200, hardware);
    await expect(getHardware()).resolves.toEqual(hardware);
    expect(sentRequest()).toMatchObject({ url: '/api/hardware', method: 'GET' });
  });

  test('checkOut and checkIn', async () => {
    reply(200, []);
    await checkOut('film-01', 'HWSet1', 3);
    expect(sentRequest()).toMatchObject({
      url: '/api/hardware/checkout',
      method: 'POST',
      body: { projectId: 'film-01', setId: 'HWSet1', quantity: 3 },
    });

    reply(200, []);
    await checkIn('film-01', 'HWSet1', 2);
    expect(sentRequest()).toMatchObject({
      url: '/api/hardware/checkin',
      method: 'POST',
      body: { projectId: 'film-01', setId: 'HWSet1', quantity: 2 },
    });
  });
});

describe('errors', () => {
  test('passes along the server’s error message', async () => {
    reply(409, { error: 'Only 2 camera kits are on the shelf.' });
    await expect(checkOut('film-01', 'HWSet1', 5)).rejects.toThrow(
      'Only 2 camera kits are on the shelf.'
    );
  });

  test('falls back to a generic message when the reply has none', async () => {
    reply(500, {});
    await expect(getHardware()).rejects.toThrow('Something went wrong (error 500). Try again.');
  });

  test('explains when the server can’t be reached', async () => {
    global.fetch = jest.fn().mockRejectedValue(new TypeError('Failed to fetch'));
    await expect(getHardware()).rejects.toThrow('Can’t reach the server.');
  });
});
