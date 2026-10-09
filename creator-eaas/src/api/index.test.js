import { checkIn, checkOut, createProject, getHardware, getProject } from '.';

// Stub checks: these pin down the behavior we expect the real backend to
// match when it replaces the stubs.

function find(hardware, setId) {
  return hardware.find((hw) => hw.setId === setId);
}

test('checking out lowers availability, and checking in raises it', async () => {
  const before = find(await getHardware(), 'HWSet1').available;

  const afterOut = await checkOut('film-01', 'HWSet1', 2);
  expect(find(afterOut, 'HWSet1').available).toBe(before - 2);

  const afterIn = await checkIn('film-01', 'HWSet1', 2);
  expect(find(afterIn, 'HWSet1').available).toBe(before);
});

test('cannot check out more kits than are on the shelf', async () => {
  await expect(checkOut('film-01', 'HWSet2', 999)).rejects.toThrow('on the shelf');
});

test('checking in cannot push availability above capacity', async () => {
  const hardware = await checkIn('film-01', 'HWSet2', 999);
  const set = find(hardware, 'HWSet2');
  expect(set.available).toBe(set.capacity);
});

test('project IDs are unique', async () => {
  const project = { projectId: 'doc-07', name: 'Doc', description: 'Short doc', ownerUserid: 'demo' };
  await createProject(project);
  await expect(createProject(project)).rejects.toThrow('taken');
  await expect(getProject('doc-07')).resolves.toEqual(project);
});
