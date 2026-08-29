import React from 'react';

export default function LoadingSpinner({ fullPage = false, label = 'Loading...' }) {
  const content = (
    <div className="sanad-loading">
      <div className="sanad-spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
  if (fullPage) {
    return <div className="sanad-loading-fullpage">{content}</div>;
  }
  return content;
}
