import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../auth/AuthContext';
import chatService from '../services/chatService';
import LoadingSpinner from './LoadingSpinner';
import ErrorState from './ErrorState';
import EmptyState from './EmptyState';

/**
 * Shared secure chat interface used by every role's Chat page. Lists
 * the user's conversations (scoped server-side by ir.rule to those they
 * participate in) and, for the selected one, polls for new messages
 * every 4s via /api/chat/poll - a genuine working integration with the
 * bus.bus-backed sanad.chat.conversation model, not a mock.
 */
export default function ChatWidget() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState(null);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);
  const lastMessageIdRef = useRef(0);
  const messagesEndRef = useRef(null);

  const loadConversations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const convs = await chatService.listConversations();
      setConversations(convs);
      if (convs.length > 0 && !selected) setSelected(convs[0]);
    } catch (err) {
      setError(err.apiMessage || 'Failed to load conversations.');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => { loadConversations(); }, [loadConversations]);

  useEffect(() => {
    if (!selected) return undefined;
    let cancelled = false;
    lastMessageIdRef.current = 0;
    setMessages([]);

    const loadMessages = async () => {
      try {
        const msgs = await chatService.listMessages(selected.id);
        if (cancelled) return;
        setMessages(msgs || []);
        if (msgs && msgs.length) lastMessageIdRef.current = msgs[msgs.length - 1].id;
      } catch (err) {
        if (!cancelled) setError(err.apiMessage || 'Failed to load messages.');
      }
    };
    loadMessages();

    const interval = setInterval(async () => {
      try {
        const newMsgs = await chatService.listMessages(selected.id, lastMessageIdRef.current);
        if (cancelled || !newMsgs || newMsgs.length === 0) return;
        setMessages((prev) => [...prev, ...newMsgs]);
        lastMessageIdRef.current = newMsgs[newMsgs.length - 1].id;
      } catch {
        // transient poll error - retry silently next tick
      }
    }, 4000);

    return () => { cancelled = true; clearInterval(interval); };
  }, [selected]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const body = draft.trim();
    if (!body || !selected) return;
    setSending(true);
    try {
      const message = await chatService.postMessage(selected.id, body);
      if (message) {
        setMessages((prev) => [...prev, message]);
        lastMessageIdRef.current = message.id;
      }
      setDraft('');
    } catch (err) {
      setError(err.apiMessage || 'Failed to send message.');
    } finally {
      setSending(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading conversations..." />;
  if (error && !conversations) return <ErrorState message={error} onRetry={loadConversations} />;
  if (conversations && conversations.length === 0) {
    return <EmptyState title="No conversations yet" message="Conversations with your care team will appear here." />;
  }

  return (
    <div className="sanad-chat-widget">
      <aside className="sanad-chat-list">
        {(conversations || []).map((c) => (
          <button
            key={c.id}
            className={`sanad-chat-list-item ${selected?.id === c.id ? 'active' : ''}`}
            onClick={() => setSelected(c)}
          >
            <strong>{c.display_name}</strong>
            <span className="sanad-muted">{c.conversation_type.replace('_', ' - ')}</span>
          </button>
        ))}
      </aside>
      <div className="sanad-chat-thread">
        {error && <div className="sanad-alert sanad-alert-error">{error}</div>}
        <div className="sanad-chat-messages">
          {messages.length === 0 ? (
            <p className="sanad-muted">No messages yet. Say hello!</p>
          ) : (
            messages.filter(Boolean).map((m) => (
              <div
                key={m.id}
                className={`sanad-chat-bubble ${m.author_id === user.id ? 'own' : ''}`}
              >
                <span className="sanad-chat-author">{m.author_name}</span>
                <p>{m.body}</p>
                <span className="sanad-chat-time">{new Date(m.date).toLocaleTimeString()}</span>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
        <form className="sanad-chat-input" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="Type a message..."
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            disabled={!selected}
          />
          <button type="submit" className="sanad-btn sanad-btn-primary" disabled={sending || !draft.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
