import { useState } from 'react';
import { createProject, joinProject } from '../api';
import useProjectList from '../useProjectList';

// Figure 2, bottom half: reopen one of your projects, start a new one, or
// join an existing one. The two forms are alternatives, so they sit side by
// side split by a rule.
function ProjectsPage({ userid, onOpen, onOpenById }) {
  return (
    <section className="page-section">
      <h1 className="page-title">Open a project</h1>
      <p className="lede">
        Kits are checked out to projects, not people. Start one for your crew, or join one
        by entering its project ID.
      </p>
      <YourProjects userid={userid} onOpenById={onOpenById} />
      <div className="picker">
        <CreateProjectForm onCreated={onOpen} />
        <JoinProjectForm onJoined={onOpen} />
      </div>
    </section>
  );
}

// The projects you started or joined, so coming back after signing in is one
// click instead of retyping an ID. Hidden until it loads, and when you have
// none yet: then the two forms below are the place to start.
function YourProjects({ userid, onOpenById }) {
  const { projects, failed, reload } = useProjectList();
  const [openingId, setOpeningId] = useState(null);
  const [error, setError] = useState('');

  if (failed) {
    return (
      <div className="your-projects">
        <p className="field-hint">
          Your projects didn’t load.{' '}
          <button type="button" className="button-link" onClick={reload}>
            Try again
          </button>
        </p>
      </div>
    );
  }
  if (!projects || projects.length === 0) {
    return null;
  }

  async function open(projectId) {
    setOpeningId(projectId);
    setError('');
    try {
      await onOpenById(projectId);
    } catch (err) {
      setError(err.message);
      setOpeningId(null);
    }
  }

  return (
    <section className="your-projects" aria-labelledby="your-projects-title">
      <h2 id="your-projects-title">Your projects</h2>
      <ul className="project-list">
        {projects.map((p) => (
          <li key={p.projectId}>
            <div className="project-list-name">
              <strong>{p.name}</strong>
              <span className="tape tape-note tape-id" aria-label={`Project ID ${p.projectId}`}>
                {p.projectId}
              </span>
            </div>
            <p className="project-list-meta">
              {p.ownerUserid === userid ? 'Started by you' : `Joined, started by ${p.ownerUserid}`}
              {p.members.length > 1 && `. ${p.members.length} on the crew`}
            </p>
            <button
              type="button"
              className="button-quiet"
              onClick={() => open(p.projectId)}
              disabled={openingId !== null}
              aria-label={`Open ${p.name}`}
            >
              {openingId === p.projectId ? 'Opening…' : 'Open'}
            </button>
          </li>
        ))}
      </ul>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}

function CreateProjectForm({ onCreated }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectId, setProjectId] = useState('');
  // The ID follows the name until the user types their own.
  const [idEdited, setIdEdited] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  function changeName(value) {
    setName(value);
    if (!idEdited) {
      setProjectId(slugify(value));
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      const project = await createProject({
        projectId: projectId.trim(),
        name: name.trim(),
        description: description.trim(),
      });
      onCreated(project);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <form className="form picker-option" onSubmit={handleSubmit} aria-labelledby="create-title">
      <h2 id="create-title">Start a new project</h2>
      <label>
        Project name
        <input value={name} onChange={(e) => changeName(e.target.value)} required />
      </label>
      <label>
        Description
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          required
        />
      </label>
      <label>
        Project ID
        <input
          value={projectId}
          onChange={(e) => {
            setProjectId(e.target.value);
            setIdEdited(true);
          }}
          aria-describedby="project-id-hint"
          autoCapitalize="off"
          spellCheck="false"
          required
        />
      </label>
      <p id="project-id-hint" className="field-hint">
        Filled in from the name. Change it if you like; it has to be unique.
      </p>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <div>
        <button type="submit" className="button-primary" disabled={busy}>
          {busy ? 'Creating project…' : 'Create project'}
        </button>
      </div>
    </form>
  );
}

// Type a project's ID to join it. If the ID matches a project, you're on its
// crew and it opens; otherwise the server's message says no project has it.
function JoinProjectForm({ onJoined }) {
  const [projectId, setProjectId] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      onJoined(await joinProject(projectId.trim()));
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <form className="form picker-option" onSubmit={handleSubmit} aria-labelledby="join-title">
      <h2 id="join-title">Join a project</h2>
      <label>
        Project ID
        <input
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          aria-describedby="join-id-hint"
          autoCapitalize="off"
          spellCheck="false"
          required
        />
      </label>
      <p id="join-id-hint" className="field-hint">
        Ask whoever started the project for its ID. It has to match exactly.
      </p>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <div>
        <button type="submit" className="button-primary" disabled={busy || !projectId.trim()}>
          {busy ? 'Joining project…' : 'Join project'}
        </button>
      </div>
    </form>
  );
}

// "Spring Short Film!" -> "spring-short-film".
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export default ProjectsPage;
