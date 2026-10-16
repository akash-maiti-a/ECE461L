// One project's page. For now it shows who the project is; the shelf and
// checkout controls come next.
function ProjectPage({ project, onBack }) {
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
    </section>
  );
}

export default ProjectPage;
