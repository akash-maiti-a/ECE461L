import { useCallback, useState } from 'react';
import './App.css';
import AuthDialog from './components/AuthDialog';
import LandingPage from './pages/LandingPage';
import ProjectPage from './pages/ProjectPage';
import ProjectsPage from './pages/ProjectsPage';

const TEAM = 'Kavi Daliparti, Akash Maiti, Shreyas Kumar, Saharsh Lavu, and Sanjay Senthil';

// The app shell: header, footer, the sign-in dialog, and whichever page is
// showing. App owns who is signed in, which page is showing, and which
// project is open; each page owns its own data.
function App() {
  const [userid, setUserid] = useState(null);
  const [view, setView] = useState('home'); // 'home' | 'projects' | 'project'
  const [project, setProject] = useState(null);
  const [dialogMode, setDialogMode] = useState(null); // 'signin' | 'signup' | null

  const closeDialog = useCallback(() => setDialogMode(null), []);

  function handleSignedIn(id) {
    setUserid(id);
    setDialogMode(null);
    setView('projects');
  }

  function signOut() {
    setUserid(null);
    setProject(null);
    setView('home');
  }

  function openProject(openedProject) {
    setProject(openedProject);
    setView('project');
  }

  function goHome(event) {
    event.preventDefault();
    setView('home');
  }

  let content;
  if (userid && view === 'projects') {
    content = <ProjectsPage userid={userid} onOpen={openProject} />;
  } else if (userid && view === 'project' && project) {
    content = <ProjectPage project={project} onBack={() => setView('projects')} />;
  } else {
    content = (
      <LandingPage
        userid={userid}
        onCreateAccount={() => setDialogMode('signup')}
        onSignIn={() => setDialogMode('signin')}
        onOpenProjects={() => setView('projects')}
      />
    );
  }

  return (
    <div className="page">
      <header className="site-header">
        <a className="wordmark" href="/" onClick={goHome}>
          Creator EaaS
        </a>
        {userid ? (
          <div className="session">
            <span>
              Signed in as <strong>{userid}</strong>
            </span>
            {view !== 'projects' && (
              <button className="button-link" onClick={() => setView('projects')}>
                Projects
              </button>
            )}
            <button className="button-link" onClick={signOut}>
              Sign out
            </button>
          </div>
        ) : (
          <button className="button-quiet" onClick={() => setDialogMode('signin')}>
            Sign in
          </button>
        )}
      </header>

      <main>{content}</main>

      <footer className="site-footer">
        <p>An ECE 461L team project by {TEAM}.</p>
      </footer>

      {dialogMode && (
        <AuthDialog
          mode={dialogMode}
          onModeChange={setDialogMode}
          onClose={closeDialog}
          onSignedIn={handleSignedIn}
        />
      )}
    </div>
  );
}

export default App;
