import React from 'react';

export default function EmptyState({ title = 'Nothing here yet', message, action }) {
  return (
    <div className="sanad-empty-state">
      <h3>{title}</h3>
      {message && <p>{message}</p>}
      {action}
    </div>
  );
}
