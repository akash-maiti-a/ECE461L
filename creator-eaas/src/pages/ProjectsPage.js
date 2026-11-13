import { useState } from 'react';
import { createProject, joinProject } from '../api';

// Figure 2, bottom half: start a new project or join an existing one.
// The two forms are alternatives, so they sit side by side split by a rule.
function ProjectsPage({ onOpen }) {
  return (
    <section className="page-section">
      <h1 className="page-title">Open a project</h1>
      <p className="lede">
        Kits are checked out to projects, not people. Start one for your crew, or join one
        by entering its project ID.
      </p>
      <div className="picker">
        <CreateProjectForm onCreated={onOpen} />
        <JoinProjectForm onJoined={onOpen} />
      </div>
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
