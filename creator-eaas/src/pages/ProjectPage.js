import { useCallback, useEffect, useState } from 'react';
import { getHardware, getProject } from '../api';
import { ShelfUnavailable, Slots } from '../components/ShelfBoard';

// One project's page: who the project is, and a shelf per hardware set
// showing what's on the shelf, what this project has, and what other
// projects have.
function ProjectPage({ project: openedProject, onBack }) {
  const projectId = openedProject.projectId;
  const [project, setProject] = useState(openedProject);
  const [hardware, setHardware] = useState(null);
  const [failed, setFailed] = useState(false);

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

  return (
    <section className="page-section">
      <button className="button-link back-link" onClick={onBack}>
        Back to projects
      </button>
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

function ProjectShelfRow({ set, yours }) {
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
    </div>
  );
}

export default ProjectPage;
