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
// "Spring short film (film-01)". Projects someone else owns show up only
// when that person shared them (members includes the signed-in user).
export function ProjectOptions({ projects, userid }) {
  const option = (p) => (
    <option key={p.projectId} value={p.projectId}>
      {p.name} ({p.projectId})
    </option>
  );
  const yours = projects.filter((p) => p.ownerUserid === userid);
  const shared = projects.filter(
    (p) => p.ownerUserid !== userid && (p.members || []).includes(userid)
  );
  const others = projects.filter(
    (p) => p.ownerUserid !== userid && !(p.members || []).includes(userid)
  );
  const groups = [
    ['Your projects', yours],
    ['Shared with you', shared],
    ['Other projects', others],
  ].filter(([, list]) => list.length > 0);
  if (groups.length <= 1) {
    return projects.map(option);
  }
  return groups.map(([label, list]) => (
    <optgroup key={label} label={label}>
      {list.map(option)}
    </optgroup>
  ));
}

export default useProjectList;
