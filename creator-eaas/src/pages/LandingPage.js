import { useCallback, useEffect, useState } from 'react';
import { getHardware } from '../api';
import ShelfBoard from '../components/ShelfBoard';

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

// The public front page: what the service is, the live shelf, how
// borrowing works, and what's in each kit.
function LandingPage({ userid, onCreateAccount, onSignIn }) {
  const [hardware, setHardware] = useState(null);
  const [hardwareFailed, setHardwareFailed] = useState(false);

  const loadHardware = useCallback(() => {
    setHardwareFailed(false);
    setHardware(null);
    getHardware()
      .then(setHardware)
      .catch(() => setHardwareFailed(true));
  }, []);

  useEffect(() => {
    loadHardware();
  }, [loadHardware]);

  return (
    <>
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
              <button className="button-primary" onClick={onCreateAccount}>
                Create an account
              </button>
              <button className="button-quiet" onClick={onSignIn}>
                Sign in
              </button>
            </div>
          )}
        </div>
        <ShelfBoard hardware={hardware} failed={hardwareFailed} onRetry={loadHardware} />
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
    </>
  );
}

export default LandingPage;
