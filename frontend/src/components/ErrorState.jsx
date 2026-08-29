import React from 'react';

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="sanad-error-state" role="alert">
      <p>{message || 'Something went wrong.'}</p>
      {onRetry && (
        <button className="sanad-btn sanad-btn-secondary" onClick={onRetry}>
          Try Again
        </button>
      )}
    </div>
  );
}
