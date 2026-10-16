import { useCallback, useState } from 'react';
import './App.css';
import AuthDialog from './components/AuthDialog';
import LandingPage from './pages/LandingPage';

const TEAM = 'Kavi Daliparti, Akash Maiti, Shreyas Kumar, Saharsh Lavu, and Sanjay Senthil';

// The app shell: header, footer, the sign-in dialog, and whichever page is
// showing. App owns who is signed in; each page owns its own data.
function App() {
  const [userid, setUserid] = useState(null);
  const [dialogMode, setDialogMode] = useState(null); // 'signin' | 'signup' | null

  const closeDialog = useCallback(() => setDialogMode(null), []);

  function handleSignedIn(id) {
    setUserid(id);
    setDialogMode(null);
  }

  return (
    <div className="page">
      <header className="site-header">
        <a className="wordmark" href="/">
          Creator EaaS
        </a>
        {userid ? (
          <div className="session">
            <span>
              Signed in as <strong>{userid}</strong>
            </span>
            <button className="button-link" onClick={() => setUserid(null)}>
              Sign out
            </button>
          </div>
        ) : (
          <button className="button-quiet" onClick={() => setDialogMode('signin')}>
            Sign in
          </button>
        )}
      </header>

      <main>
        <LandingPage
          userid={userid}
          onCreateAccount={() => setDialogMode('signup')}
          onSignIn={() => setDialogMode('signin')}
        />
      </main>

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
