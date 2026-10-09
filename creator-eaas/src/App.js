import { useCallback, useEffect, useState } from 'react';
import './App.css';
import { getHardware } from './api';
import AuthDialog from './components/AuthDialog';
import ShelfBoard from './components/ShelfBoard';

const STEPS = [
  {
    title: 'Create an account',
    body: 'Pick a user ID and password.',
  },
  {
    title: 'Open a project',
    body: 'Start a new project or join one with its project ID. Kits are checked out to projects, not people, so your whole crew sees the same gear.',
  },
  {
    title: 'Check out kits',
    body: 'Choose how many camera or audio and lighting kits you need. The shelf count updates right away.',
  },
  {
    title: 'Check them back in',
    body: 'Return kits when you wrap so the next crew can use them.',
  },
];

const TEAM = 'Kavi Daliparti, Akash Maiti, Shreyas Kumar, Saharsh Lavu, and Sanjay Senthil';

function App() {
  const [hardware, setHardware] = useState(null);
  const [hardwareError, setHardwareError] = useState('');
  const [userid, setUserid] = useState(null);
  const [dialogMode, setDialogMode] = useState(null); // 'signin' | 'signup' | null

  useEffect(() => {
    getHardware()
      .then(setHardware)
      .catch(() => setHardwareError('The shelf count didn’t load. Refresh the page to try again.'));
  }, []);

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
        <section className="hero">
          <div className="hero-copy">
            <h1>Camera, audio, and lighting kits for your next project.</h1>
            <p className="lede">
              Borrow shared gear for your student org or class project. See what’s on the shelf,
              check kits out to your project, and bring them back when you wrap.
            </p>
            {userid ? (
              <p className="signed-in-note" role="status">
                You’re signed in as {userid}. Projects and checkout are the next screens we’re
                building.
              </p>
            ) : (
              <div className="hero-actions">
                <button className="button-primary" onClick={() => setDialogMode('signup')}>
                  Create an account
                </button>
                <button className="button-quiet" onClick={() => setDialogMode('signin')}>
                  Sign in
                </button>
              </div>
            )}
          </div>
          {hardwareError ? (
            <p className="form-error" role="alert">
              {hardwareError}
            </p>
          ) : (
            <ShelfBoard hardware={hardware} />
          )}
        </section>

        <section className="steps" aria-labelledby="steps-title">
          <h2 id="steps-title">How borrowing works</h2>
          <ol className="step-list">
            {STEPS.map((step) => (
              <li key={step.title}>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </li>
            ))}
          </ol>
        </section>

        {hardware && (
          <section className="kits" aria-labelledby="kits-title">
            <h2 id="kits-title">What’s in each kit</h2>
            <div className="kit-list">
              {hardware.map((set) => (
                <div key={set.setId} className={`kit tape-${set.setId}`}>
                  <h3 className="tape">{set.name}</h3>
                  <ul>
                    {set.contents.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        )}
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
