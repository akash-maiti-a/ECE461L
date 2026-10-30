import { useState } from 'react';
import { createProject, getProject } from '../api';
import useProjectList, { ProjectOptions } from '../useProjectList';

// Figure 2, bottom half: start a new project or pick an existing one.
// The two forms are alternatives, so they sit side by side split by a rule.
function ProjectsPage({ userid, onOpen }) {
  return (
    <section className="page-section">
      <h1 className="page-title">Open a project</h1>
      <p className="lede">
        Kits are checked out to projects, not people. Start one for your crew, or open one
        that was shared with you.
      </p>
      <div className="picker">
        <CreateProjectForm onCreated={onOpen} />
        <JoinProjectForm userid={userid} onFound={onOpen} />
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

function JoinProjectForm({ userid, onFound }) {
  const { projects, failed, reload } = useProjectList();
  const [chosen, setChosen] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  // Until the user picks one, open their first project (it's listed first).
  const first = projects?.find((p) => p.ownerUserid === userid) ?? projects?.[0];
  const projectId = chosen || first?.projectId || '';

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      onFound(await getProject(projectId));
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  let field;
  if (failed) {
    field = (
      <>
        <p className="form-error" role="alert">
          The project list didn’t load.
        </p>
        <div>
          <button type="button" className="button-quiet" onClick={reload}>
            Try again
          </button>
        </div>
      </>
    );
  } else if (projects && projects.length === 0) {
    field = (
      <p className="field-hint">No projects yet. Start one, or ask a teammate to share theirs.</p>
    );
  } else {
    field = (
      <label>
        Project
        <select
          value={projectId}
          onChange={(e) => setChosen(e.target.value)}
          disabled={!projects}
          required
        >
          {projects ? (
            <ProjectOptions projects={projects} userid={userid} />
          ) : (
            <option value="">Loading projects…</option>
          )}
        </select>
      </label>
    );
  }

  return (
    <form className="form picker-option" onSubmit={handleSubmit} aria-labelledby="join-title">
      <h2 id="join-title">Join a project</h2>
      {field}
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <div>
        <button type="submit" className="button-primary" disabled={busy || !projectId}>
          {busy ? 'Opening project…' : 'Open project'}
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
