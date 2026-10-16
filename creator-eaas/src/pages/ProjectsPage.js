import { useState } from 'react';
import { createProject, getProject } from '../api';

// Figure 2, bottom half: start a new project or join an existing one by ID.
// The two forms are alternatives, so they sit side by side split by a rule.
function ProjectsPage({ userid, onOpen }) {
  return (
    <section className="page-section">
      <h1 className="page-title">Open a project</h1>
      <p className="lede">
        Kits are checked out to projects, not people. Start one for your crew, or join one with
        the ID a teammate shared.
      </p>
      <div className="picker">
        <CreateProjectForm userid={userid} onCreated={onOpen} />
        <JoinProjectForm onFound={onOpen} />
      </div>
    </section>
  );
}

function CreateProjectForm({ userid, onCreated }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectId, setProjectId] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      const project = await createProject({
        projectId: projectId.trim(),
        name: name.trim(),
        description: description.trim(),
        ownerUserid: userid,
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
        <input value={name} onChange={(e) => setName(e.target.value)} required />
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
          onChange={(e) => setProjectId(e.target.value)}
          aria-describedby="project-id-hint"
          autoCapitalize="off"
          spellCheck="false"
          required
        />
      </label>
      <p id="project-id-hint" className="field-hint">
        Your crew types this ID to join the project.
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

function JoinProjectForm({ onFound }) {
  const [projectId, setProjectId] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      onFound(await getProject(projectId.trim()));
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
          autoCapitalize="off"
          spellCheck="false"
          required
        />
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <div>
        <button type="submit" className="button-primary" disabled={busy}>
          {busy ? 'Opening project…' : 'Open project'}
        </button>
      </div>
    </form>
  );
}

export default ProjectsPage;
