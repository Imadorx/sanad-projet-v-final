import React, { useState, useCallback } from 'react';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import laboratoryService from '../../services/laboratoryService';
import aiService from '../../services/aiService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';

const LANGUAGES = { ar: 'Arabic', fr: 'French', en: 'English' };

/**
 * Patient-facing AI assistant (PRD 5.3 / 15.2): search authorized data,
 * explain a consultation or lab result in plain language, translate the
 * explanation, and hear it read aloud. Every action here calls the real
 * sanad_ai backend (/api/ai/*) - PHI anonymization, safety filtering,
 * and audit logging all happen server-side before any response reaches
 * this page. TTS uses the browser's native Web Speech API (no server
 * audio generation is faked) - see sanad_ai's request_tts() docstring
 * for why 'browser' mode was chosen as the honest default.
 */
export default function PatientAiAssistant() {
  const fetchContext = useCallback(async () => {
    const profile = await patientService.me();
    const [consultations, labResults] = await Promise.all([
      medicalService.listConsultations(profile.id),
      laboratoryService.listResults({ patient_id: profile.id }),
    ]);
    return { profile, consultations, labResults };
  }, []);
  const { data, loading, error, refetch } = useApiData(fetchContext, []);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [searchBusy, setSearchBusy] = useState(false);
  const [searchError, setSearchError] = useState(null);

  const [selectedRecord, setSelectedRecord] = useState('');
  const [explanation, setExplanation] = useState(null);
  const [explainBusy, setExplainBusy] = useState(false);
  const [explainError, setExplainError] = useState(null);

  const [targetLang, setTargetLang] = useState('ar');
  const [translation, setTranslation] = useState(null);
  const [translateBusy, setTranslateBusy] = useState(false);

  const [speaking, setSpeaking] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setSearchError(null);
    setSearchBusy(true);
    try {
      const result = await aiService.search(searchQuery, data.profile.id);
      setSearchResult(result);
    } catch (err) {
      setSearchError(err.apiMessage || 'Search failed.');
    } finally {
      setSearchBusy(false);
    }
  };

  const handleExplain = async () => {
    if (!selectedRecord) return;
    const [model, id] = selectedRecord.split(':');
    setExplainError(null);
    setExplainBusy(true);
    setTranslation(null);
    try {
      const result = await aiService.explain(model, parseInt(id, 10));
      setExplanation(result);
    } catch (err) {
      setExplainError(err.apiMessage || 'Explanation failed.');
    } finally {
      setExplainBusy(false);
    }
  };

  const handleTranslate = async () => {
    if (!explanation?.explanation) return;
    setTranslateBusy(true);
    try {
      const result = await aiService.translate(explanation.explanation, targetLang);
      setTranslation(result);
    } finally {
      setTranslateBusy(false);
    }
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setSpeaking(false);
  };

  const handleSpeak = async () => {
    if (speaking) { stopSpeaking(); return; }
    const textToSpeak = translation?.translation || explanation?.explanation;
    if (!textToSpeak) return;
    const { text } = await aiService.tts(textToSpeak);
    if (!window.speechSynthesis) {
      alert('Text-to-speech is not supported in this browser.');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = targetLang === 'ar' ? 'ar-SA' : targetLang === 'fr' ? 'fr-FR' : 'en-US';
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  if (loading) return <LoadingSpinner fullPage label="Loading AI assistant..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div className="sanad-page">
      <h1>AI Assistant</h1>
      <p className="sanad-muted">
        This assistant explains, translates, and helps you find your own authorized
        medical information. It never diagnoses, prescribes, or replaces your doctor.
      </p>

      <section className="sanad-card">
        <h2>Search My Records</h2>
        <form className="sanad-form-inline" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="e.g. glucose, consultation, ibuprofen..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button className="sanad-btn sanad-btn-primary" type="submit" disabled={searchBusy || !searchQuery.trim()}>
            {searchBusy ? 'Searching...' : 'Search'}
          </button>
        </form>
        {searchError && <div className="sanad-alert sanad-alert-error">{searchError}</div>}
        {searchResult && (
          <div className="sanad-ai-response">
            <p>{searchResult.summary}</p>
            {searchResult.matches?.length > 0 && (
              <ul className="sanad-list">
                {searchResult.matches.map((m, i) => (
                  <li key={i}>{m.type}: {m.reason || m.medication || m.analysis_name}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>

      <section className="sanad-card">
        <h2>Explain a Record</h2>
        <select value={selectedRecord} onChange={(e) => setSelectedRecord(e.target.value)}>
          <option value="">Select a consultation or lab result...</option>
          {data.consultations.map((c) => (
            <option key={`c-${c.id}`} value={`sanad.consultation:${c.id}`}>
              Consultation: {c.reason} ({new Date(c.date).toLocaleDateString()})
            </option>
          ))}
          {data.labResults.map((r) => (
            <option key={`r-${r.id}`} value={`sanad.lab.result:${r.id}`}>
              Lab Result: {r.analysis_name} ({new Date(r.date).toLocaleDateString()})
            </option>
          ))}
        </select>
        <button className="sanad-btn sanad-btn-primary" onClick={handleExplain} disabled={!selectedRecord || explainBusy}>
          {explainBusy ? 'Explaining...' : 'Explain in Plain Language'}
        </button>
        {explainError && <div className="sanad-alert sanad-alert-error">{explainError}</div>}
        {explanation && (
          <div className="sanad-ai-response">
            <p>{explanation.explanation}</p>

            <div className="sanad-form-inline">
              <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
                {Object.entries(LANGUAGES).map(([code, label]) => (
                  <option key={code} value={code}>{label}</option>
                ))}
              </select>
              <button className="sanad-btn sanad-btn-secondary" onClick={handleTranslate} disabled={translateBusy}>
                {translateBusy ? 'Translating...' : 'Translate'}
              </button>
              <button className={`sanad-btn ${speaking ? 'sanad-btn-danger' : 'sanad-btn-secondary'}`} onClick={handleSpeak}>
                {speaking ? '⏹ Stop' : '🔊 Read Aloud'}
              </button>
            </div>

            {translation && (
              <div className="sanad-ai-response sanad-ai-translation">
                <strong>{LANGUAGES[translation.target_lang]}:</strong>
                <p>{translation.translation}</p>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
