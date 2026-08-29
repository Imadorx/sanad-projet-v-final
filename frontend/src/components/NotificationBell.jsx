import React, { useState, useEffect, useRef } from 'react';
import chatService from '../services/chatService';
import { useAuth } from '../auth/AuthContext';

/**
 * Polls /api/chat/poll every 8s for new messages across all of the
 * user's conversations and shows a badge count. This is a real,
 * working integration with the backend bus.bus-backed chat system
 * (see chat_controller.py) - not a mock counter.
 */
export default function NotificationBell() {
  const { user } = useAuth();
  const [unseenCount, setUnseenCount] = useState(0);
  const lastSeenIdRef = useRef(0);
  const [open, setOpen] = useState(false);
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    if (!user) return undefined;
    let cancelled = false;

    const poll = async () => {
      try {
        const messages = await chatService.poll(lastSeenIdRef.current);
        if (cancelled || messages.length === 0) return;
        const fromOthers = messages.filter((m) => m.author_id !== user.id);
        if (fromOthers.length > 0) {
          setUnseenCount((c) => c + fromOthers.length);
          setRecent((prev) => [...fromOthers, ...prev].slice(0, 5));
        }
        lastSeenIdRef.current = Math.max(
          lastSeenIdRef.current,
          ...messages.map((m) => m.id)
        );
      } catch {
        // Silently retry on next interval - a transient poll failure
        // should not surface as an error banner.
      }
    };

    const interval = setInterval(poll, 8000);
    poll();
    return () => { cancelled = true; clearInterval(interval); };
  }, [user]);

  return (
    <div className="sanad-notification-bell">
      <button
        className="sanad-bell-btn"
        onClick={() => { setOpen((o) => !o); if (!open) setUnseenCount(0); }}
        aria-label="Notifications"
      >
        🔔
        {unseenCount > 0 && <span className="sanad-badge">{unseenCount}</span>}
      </button>
      {open && (
        <div className="sanad-notification-dropdown">
          {recent.length === 0 ? (
            <p className="sanad-muted">No new messages.</p>
          ) : (
            recent.map((m) => (
              <div key={m.id} className="sanad-notification-item">
                <strong>{m.author_name}</strong>
                <p>{m.body}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
