// The hero's shelf board: one slot per kit. A filled slot is a kit on the
// shelf; an outlined slot is a kit that's checked out. Each set gets its own
// spike-tape color, the way gear rooms label shelves.
function ShelfBoard({ hardware }) {
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

function ShelfRow({ set }) {
  const slots = Array.from({ length: set.capacity }, (_, i) => i < set.available);
  return (
    <div className={`shelf-row tape-${set.setId}`}>
      <span className="tape">{set.name}</span>
      <div className="slots" aria-hidden="true">
        {slots.map((onShelf, i) => (
          <span
            key={i}
            className={onShelf ? 'slot slot-full' : 'slot'}
            style={{ '--i': i }}
          />
        ))}
      </div>
      <p className="shelf-count">
        <strong>{set.available}</strong> of {set.capacity} on the shelf
      </p>
    </div>
  );
}

export default ShelfBoard;
