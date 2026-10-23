import { useCallback, useEffect, useState } from 'react';
import { checkIn, checkOut, getHardware, getProject } from '../api';
import { ShelfUnavailable, Slots } from '../components/ShelfBoard';
import useProjectList, { ProjectOptions } from '../useProjectList';

// One project's page: who the project is, and a shelf per hardware set
// showing what's on the shelf, what this project has, and what other
// projects have.
function ProjectPage({ project: openedProject, userid, onBack, onSwitch }) {
  const projectId = openedProject.projectId;
  const [project, setProject] = useState(openedProject);
  const [hardware, setHardware] = useState(null);
  const [failed, setFailed] = useState(false);
  const [busySetId, setBusySetId] = useState(null);
  // The latest result, shown in the row it belongs to: { setId, type, text }.
  const [message, setMessage] = useState(null);

  // Re-fetch the project too, so its checkedOut tally is current even if a
  // teammate changed it since the picker loaded it.
  const load = useCallback(() => {
    setFailed(false);
    Promise.all([getHardware(), getProject(projectId)])
      .then(([latestHardware, latestProject]) => {
        setHardware(latestHardware);
        setProject(latestProject);
      })
      .catch(() => setFailed(true));
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  async function moveKits(action, set, quantity) {
    setBusySetId(set.setId);
    setMessage(null);
    try {
      const send = action === 'checkout' ? checkOut : checkIn;
      setHardware(await send(projectId, set.setId, quantity));
      setProject(await getProject(projectId));
      const verb = action === 'checkout' ? 'Checked out' : 'Checked in';
      setMessage({ setId: set.setId, type: 'success', text: `${verb} ${kitCount(quantity, set.name)}.` });
      return true;
    } catch (err) {
      setMessage({ setId: set.setId, type: 'error', text: err.message });
      return false;
    } finally {
      setBusySetId(null);
    }
  }

  return (
    <section className="page-section">
      <div className="project-nav">
        <button className="button-link" onClick={onBack}>
          Back to projects
        </button>
        <ProjectSwitcher projectId={projectId} userid={userid} onSwitch={onSwitch} />
      </div>
      <div className="project-heading">
        <h1 className="page-title">{project.name}</h1>
        <span className="tape tape-note tape-id" aria-label={`Project ID ${project.projectId}`}>
          {project.projectId}
        </span>
      </div>
      <p className="lede">{project.description}</p>
      <p className="project-owner">Created by {project.ownerUserid}</p>

      <div className="project-shelf">
        {failed ? (
          <ShelfUnavailable onRetry={load} />
        ) : (
          <figure className="shelf" aria-label="Kits for this project">
            {hardware ? (
              hardware.map((set) => (
                <ProjectShelfRow
                  key={set.setId}
                  set={set}
                  yours={project.checkedOut?.[set.setId] ?? 0}
                  busy={busySetId === set.setId}
                  message={message?.setId === set.setId ? message : null}
                  onMove={(action, quantity) => moveKits(action, set, quantity)}
                />
              ))
            ) : (
              <p className="shelf-loading">Counting the shelf…</p>
            )}
            <figcaption className="shelf-legend">
              <span>
                <span className="slot slot-full legend-swatch tape-HWSet1" aria-hidden="true" />
                On the shelf
              </span>
              <span>
                <span className="slot slot-yours legend-swatch tape-HWSet1" aria-hidden="true" />
                With this project
              </span>
              <span>
                <span className="slot legend-swatch" aria-hidden="true" />
                With other projects
              </span>
            </figcaption>
          </figure>
        )}
      </div>
    </section>
  );
}

// A dropdown for jumping straight to another project. Hidden until the list
// loads, and when there's no other project to switch to.
function ProjectSwitcher({ projectId, userid, onSwitch }) {
  const { projects } = useProjectList();
  const [switching, setSwitching] = useState(false);
  const [error, setError] = useState('');

  if (!projects || !projects.some((p) => p.projectId !== projectId)) {
    return null;
  }

  async function handleChange(event) {
    setSwitching(true);
    setError('');
    try {
      await onSwitch(event.target.value);
    } catch (err) {
      setError(err.message);
      setSwitching(false);
    }
  }

  return (
    <div className="project-switcher">
      <label>
        Switch project
        <select value={projectId} onChange={handleChange} disabled={switching}>
          <ProjectOptions projects={projects} userid={userid} />
        </select>
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

// "1 camera kit", "3 camera kits".
function kitCount(quantity, setName) {
  const name = setName.toLowerCase();
  return `${quantity} ${quantity === 1 ? name.replace(/s$/, '') : name}`;
}

function ProjectShelfRow({ set, yours, busy, message, onMove }) {
  const [quantity, setQuantity] = useState('');
  const [inputError, setInputError] = useState('');
  const inputId = `quantity-${set.setId}`;

  async function handle(action) {
    const amount = Number(quantity);
    if (!Number.isInteger(amount) || amount <= 0) {
      setInputError('Enter a whole number of kits, like 2.');
      return;
    }
    setInputError('');
    if (await onMove(action, amount)) {
      setQuantity('');
    }
  }

  const note = inputError ? { type: 'error', text: inputError } : message;

  return (
    <div className={`shelf-row tape-${set.setId}`}>
      <span className="tape">{set.name}</span>
      <Slots capacity={set.capacity} available={set.available} yours={yours} />
      <div className="shelf-counts">
        <p className="shelf-count">
          <strong>{set.available}</strong> of {set.capacity} on the shelf
        </p>
        <p className="shelf-count">
          <strong>{yours}</strong> with this project
        </p>
      </div>
      <form
        className="kit-controls"
        aria-label={`Check ${set.name.toLowerCase()} out or in`}
        onSubmit={(event) => {
          event.preventDefault();
          handle('checkout');
        }}
      >
        <label htmlFor={inputId}>Kits</label>
        <input
          id={inputId}
          // Both rows say "Kits" visibly; the set name tells screen readers which.
          aria-label={set.name}
          type="number"
          inputMode="numeric"
          min="1"
          step="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
        <button type="submit" className="button-primary" disabled={busy || set.available === 0}>
          Check out
        </button>
        <button
          type="button"
          className="button-quiet"
          disabled={busy || yours === 0}
          onClick={() => handle('checkin')}
        >
          Check in
        </button>
      </form>
      {note && (
        <p
          className={note.type === 'error' ? 'form-error kit-note' : 'kit-note kit-note-success'}
          role={note.type === 'error' ? 'alert' : 'status'}
        >
          {note.text}
        </p>
      )}
    </div>
  );
}

export default ProjectPage;
