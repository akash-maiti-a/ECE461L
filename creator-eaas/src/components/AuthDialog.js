import { useEffect, useState } from 'react';
import { signIn, signUp } from '../api';

// Sign-in form and the "New user" pop-up from the project brief (Figure 2),
// as one dialog that switches between the two.
function AuthDialog({ mode, onModeChange, onClose, onSignedIn }) {
  const [userid, setUserid] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const isNewUser = mode === 'signup';
  const title = isNewUser ? 'Create an account' : 'Sign in';

  useEffect(() => {
    function handleKey(event) {
      if (event.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  function switchMode() {
    setError('');
    setConfirm('');
    onModeChange(isNewUser ? 'signin' : 'signup');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    if (isNewUser && password !== confirm) {
      setError('The passwords don’t match. Type the same password in both fields.');
      return;
    }
    setBusy(true);
    try {
      const id = userid.trim();
      await (isNewUser ? signUp(id, password) : signIn(id, password));
      onSignedIn(id);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="dialog-backdrop" onMouseDown={onClose}>
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <h2 id="auth-title">{title}</h2>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            User ID
            <input
              value={userid}
              onChange={(e) => setUserid(e.target.value)}
              autoComplete="username"
              autoFocus
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isNewUser ? 'new-password' : 'current-password'}
              required
            />
          </label>
          {isNewUser && (
            <label>
              Confirm password
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                autoComplete="new-password"
                required
              />
            </label>
          )}
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          <div className="dialog-actions">
            <button type="button" className="button-quiet" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="button-primary" disabled={busy}>
              {busy ? (isNewUser ? 'Creating account…' : 'Signing in…') : title}
            </button>
          </div>
        </form>
        <p className="dialog-switch">
          {isNewUser ? 'Already have an account?' : 'New user?'}{' '}
          <button type="button" className="button-link" onClick={switchMode}>
            {isNewUser ? 'Sign in' : 'Create an account'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default AuthDialog;
