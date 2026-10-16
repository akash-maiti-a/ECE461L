// The hero's shelf board: one slot per kit. A filled slot is a kit on the
// shelf; an outlined slot is a kit that's checked out. Each set gets its own
// spike-tape color, the way gear rooms label shelves.
function ShelfBoard({ hardware, failed, onRetry }) {
  if (failed) {
    return <ShelfUnavailable onRetry={onRetry} />;
  }
  return (
    <figure className="shelf" aria-label="Kits on the shelf right now">
      {hardware ? (
        hardware.map((set) => <ShelfRow key={set.setId} set={set} />)
      ) : (
        <p className="shelf-loading">Counting the shelf…</p>
      )}
      <figcaption className="shelf-caption">
        Filled slots are on the shelf. Outlined slots are checked out.
      </figcaption>
    </figure>
  );
}

// Shown when the counts can't be loaded. It deliberately draws no slots:
// outlined slots mean "checked out", so empty ones would claim every kit
// is gone. A gray note on the shelf says what happened instead.
function ShelfUnavailable({ onRetry }) {
  return (
    <figure className="shelf" aria-label="Kits on the shelf right now">
      <span className="tape tape-note">Count unavailable</span>
      <p className="shelf-unavailable" role="alert">
        The equipment server didn’t answer, so kit counts can’t be shown right now.
      </p>
      <button className="button-quiet" onClick={onRetry}>
        Try again
      </button>
    </figure>
  );
}

function ShelfRow({ set }) {
  return (
    <div className={`shelf-row tape-${set.setId}`}>
      <span className="tape">{set.name}</span>
      <Slots capacity={set.capacity} available={set.available} />
      <p className="shelf-count">
        <strong>{set.available}</strong> of {set.capacity} on the shelf
      </p>
    </div>
  );
}

// One slot per kit, in order: on the shelf, then with this project (if
// `yours` is given), then with other projects. Decorative only; the counts
// next to it are what screen readers read.
export function Slots({ capacity, available, yours = 0 }) {
  const slots = Array.from({ length: capacity }, (_, i) => {
    if (i < available) return 'slot slot-full';
    if (i < available + yours) return 'slot slot-yours';
    return 'slot';
  });
  return (
    <div className="slots" aria-hidden="true">
      {slots.map((className, i) => (
        <span key={i} className={className} style={{ '--i': i }} />
      ))}
    </div>
  );
}

export { ShelfUnavailable };
export default ShelfBoard;
