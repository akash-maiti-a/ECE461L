import { useCallback, useEffect, useState } from 'react';
import { listProjects } from './api';

// Loads every project for the project dropdowns. projects is null while
// loading; failed is true if the request didn't work, and reload tries again.
function useProjectList() {
  const [projects, setProjects] = useState(null);
  const [failed, setFailed] = useState(false);

  const reload = useCallback(() => {
    setFailed(false);
    setProjects(null);
    listProjects()
      .then(setProjects)
      .catch(() => setFailed(true));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return { projects, failed, reload };
}

// The dropdown's options, the signed-in user's projects first:
// "Spring short film (film-01)".
export function ProjectOptions({ projects, userid }) {
  const option = (p) => (
    <option key={p.projectId} value={p.projectId}>
      {p.name} ({p.projectId})
    </option>
  );
  const yours = projects.filter((p) => p.ownerUserid === userid);
  const others = projects.filter((p) => p.ownerUserid !== userid);
  if (yours.length === 0 || others.length === 0) {
    return projects.map(option);
  }
  return (
    <>
      <optgroup label="Your projects">{yours.map(option)}</optgroup>
      <optgroup label="Other projects">{others.map(option)}</optgroup>
    </>
  );
}

export default useProjectList;
