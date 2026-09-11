import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaMicrophone,
  FaStop,
  FaPaperPlane,
  FaSignOutAlt,
  FaRobot,
  FaEnvelope,
  FaBolt,
  FaExclamationTriangle,
  FaBalanceScale,
  FaCheckCircle,
  FaChevronDown,
  FaChevronUp,
  FaInfoCircle,
  FaTrashAlt,
  FaGavel
} from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { auth } from './firebase';
import './Home.css';

// Curated legal scenario presets for instant 1-click testing
const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:5000'
    : 'https://legal-advisor-green.vercel.app');

const CASE_PRESETS = [
  {
    label: "🔪 Premeditated Murder",
    text: "A man planned the crime for weeks, entered his neighbor's house with a dagger, and stabbed him with the intention to cause death."
  },
  {
    label: "🚗 Fatal Rash Driving",
    text: "A drunk driver was speeding at 120 km/h on the highway and hit a pedestrian crossing the road, who died immediately from the impact."
  },
  {
    label: "📄 Forged Property Deed",
    text: "Someone forged my signature on a land deed and sold my ancestral property to a third party for unlawful financial gain."
  },
  {
    label: "💍 Dowry Harassment",
    text: "My husband and his parents have been constantly demanding cash and a car as dowry, torturing me physically and mentally."
  },
  {
    label: "🗡️ Armed Dacoity",
    text: "A gang of five men broke into our shop at night carrying firearms and knives, threatened the guard, and looted the cash safe."
  },
  {
    label: "🧪 Acid Attack",
    text: "An estranged stalker threw acid on a woman's face after she refused his proposal, inflicting permanent disfigurement and grievous burns."
  }
];

const SUGGESTED_CHAT_PROMPTS = [
  "What is the difference between Section 299 and Section 300 of the IPC?",
  "What are the legal requisites of Cheating under Section 415?",
  "When does the Right of Private Defense extend to causing death?",
  "Explain Section 34 (Common Intention) with illustrative examples."
];

export default function Home() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('expert'); // 'expert' | 'chat'

  // User & Quota State
  const [quotaRemaining, setQuotaRemaining] = useState(5);
  const [dailyLimit, setDailyLimit] = useState(5);
  const [isRateLimited, setIsRateLimited] = useState(false);
  const currentUser = auth.currentUser;

  // Rule-Based Expert System State
  const [problemInput, setProblemInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [expertResults, setExpertResults] = useState(null);
  const [showPartial, setShowPartial] = useState(false);
  const [expandedXaiId, setExpandedXaiId] = useState(null);
  const [inlineRagResponse, setInlineRagResponse] = useState('');
  const [isInlineRagLoading, setIsInlineRagLoading] = useState(false);

  // Conversational AI (RAG) State
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    {
      role: 'assistant',
      content: 'Welcome to Juris - Your Legal Research Assistant. I am powered by 158 statutory IPC expert rules and Groq vector retrieval. Ask a legal question or describe a factual dispute.'
    }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  // 1. Fetch user quota on mount or auth change
  useEffect(() => {
    const fetchQuota = async () => {
      const user = auth.currentUser;
      if (user?.uid) {
        try {
          const res = await fetch(`${API_BASE_URL}/user_quota?user_id=${encodeURIComponent(user.uid)}`);
          const data = await res.json();
          if (data.success) {
            setQuotaRemaining(data.remaining);
            setDailyLimit(data.daily_limit);
            setIsRateLimited(data.remaining <= 0);
          }
        } catch (e) {
          console.warn("Backend server offline or quota unreachable:", e);
        }
      }
    };
    fetchQuota();
  }, [currentUser]);

  // 2. Setup Speech Recognition
  useEffect(() => {
    if (window.webkitSpeechRecognition || window.SpeechRecognition) {
      const SpeechClass = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recog = new SpeechClass();
      recog.continuous = true;
      recog.interimResults = true;
      recog.lang = 'en-IN';

      recog.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((r) => r[0].transcript)
          .join(' ');
        setProblemInput((prev) => (prev ? prev + ' ' + transcript : transcript));
      };

      recog.onerror = () => setIsListening(false);
      recog.onend = () => setIsListening(false);
      setRecognition(recog);
    }
  }, []);

  // 3. Scroll to bottom of chat
  useEffect(() => {
    if (activeTab === 'chat') {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, activeTab]);

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate('/signin');
    } catch (e) {
      console.error("Logout error:", e);
    }
  };

  const toggleSpeech = () => {
    if (!recognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }
    if (!isListening) {
      try {
        recognition.start();
        setIsListening(true);
      } catch (err) {
        console.error(err);
      }
    } else {
      recognition.stop();
      setIsListening(false);
    }
  };

  const handleSelectPreset = (presetText) => {
    setProblemInput(presetText);
    setExpertResults(null);
    setInlineRagResponse('');
  };

  // Submit for Deterministic Rule-Based Expert System Analysis
  const submitExpertAnalysis = async (e) => {
    e.preventDefault();
    if (!problemInput.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setExpertResults(null);
    setInlineRagResponse('');
    setShowPartial(false);

    try {
      const res = await fetch(`${API_BASE_URL}/analyze_rule_based`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: problemInput.trim() }),
      });
      const data = await res.json();
      if (data.success) {
        setExpertResults(data);
      } else {
        alert("Inference Notice: " + (data.message || "Failed to analyze case."));
      }
    } catch (err) {
      console.error(err);
      alert(`Unable to reach backend inference server (${API_BASE_URL}). Ensure backend service is active.`);
    }
    setIsAnalyzing(false);
  };

  // Submit Inline RAG Query (Escalation from partial matches)
  const submitInlineRag = async () => {
    const user = auth.currentUser;
    if (!user) {
      alert("🔒 Authentication Required: Please sign in to access the RAG AI model.");
      navigate('/signin');
      return;
    }

    if (quotaRemaining <= 0) {
      alert("⚠️ Daily quota limit reached (5 queries/day). Please email ashishsingh67788@gmail.com for extended quota.");
      setIsRateLimited(true);
      return;
    }

    setIsInlineRagLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/analyze_rag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: problemInput.trim(),
          history: [],
          user_id: user.uid,
          user_email: user.email
        }),
      });
      const data = await res.json();
      if (data.success) {
        setInlineRagResponse(data.message);
        if (typeof data.remaining === 'number') {
          setQuotaRemaining(data.remaining);
          setIsRateLimited(data.remaining <= 0);
        }
      } else {
        setInlineRagResponse(data.message);
        if (data.rate_limited) {
          setIsRateLimited(true);
          setQuotaRemaining(0);
        }
      }
    } catch (err) {
      setInlineRagResponse("Failed to connect to the RAG LLM engine.");
    }
    setIsInlineRagLoading(false);
  };

  // Submit Chat Message to pure RAG
  const submitChat = async (e, promptOverride = null) => {
    if (e) e.preventDefault();
    const query = promptOverride || chatInput;
    if (!query.trim() || isChatLoading) return;

    const user = auth.currentUser;
    if (!user) {
      alert("🔒 Authentication Required: Please sign in to use the Conversational AI.");
      navigate('/signin');
      return;
    }

    if (quotaRemaining <= 0) {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: "⚠️ Daily Limit Reached: You have consumed your 5 free AI queries for today. Please contact ashishsingh67788@gmail.com for extended access.",
          rateLimited: true
        }
      ]);
      setIsRateLimited(true);
      return;
    }

    setChatInput('');
    setChatHistory((prev) => [...prev, { role: 'user', content: query }]);
    setIsChatLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/analyze_rag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          history: chatHistory,
          user_id: user.uid,
          user_email: user.email
        }),
      });
      const data = await res.json();
      if (data.success) {
        setChatHistory((prev) => [...prev, { role: 'assistant', content: data.message }]);
        if (typeof data.remaining === 'number') {
          setQuotaRemaining(data.remaining);
          setIsRateLimited(data.remaining <= 0);
        }
      } else {
        setChatHistory((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: data.message,
            rateLimited: Boolean(data.rate_limited)
          }
        ]);
        if (data.rate_limited) {
          setIsRateLimited(true);
          setQuotaRemaining(0);
        }
      }
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', content: "⚠️ Network Error: Unable to communicate with the legal research server." }
      ]);
    }
    setIsChatLoading(false);
  };

  const getQuotaClass = () => {
    if (quotaRemaining > 2) return 'plenty';
    if (quotaRemaining > 0) return 'warning';
    return 'exhausted';
  };

  return (
    <div className="home-container">
      {/* ── Top Navigation Bar ────────────────────────────────────────── */}
      <nav className="navbar">
        <div className="nav-brand">
          <div className="brand-crest">
            <FaBalanceScale />
          </div>
          <div className="brand-text">
            <span className="brand-title">Juris</span>
            <span className="brand-subtitle">Your Legal Research Assistant</span>
          </div>
        </div>

        <div className="nav-actions">
          <div className="system-status-pill">
            <span className="status-dot"></span>
            <span>158 Statutory IPC Rules</span>
          </div>

          <div className="user-profile-pill">
            <div className="user-avatar">
              {currentUser?.email ? currentUser.email.charAt(0).toUpperCase() : 'U'}
            </div>
            <span>{currentUser?.email || 'Authenticated User'}</span>
            <div className={`quota-counter-pill ${getQuotaClass()}`}>
              <FaBolt /> {quotaRemaining}/{dailyLimit} queries left
            </div>
          </div>

          <button onClick={handleLogout} className="btn-logout" title="Sign Out">
            <FaSignOutAlt /> Sign Out
          </button>
        </div>
      </nav>

      {/* ── Main Workspace ────────────────────────────────────────────── */}
      <main className="main-workspace">
        <div className="hero-header">
          <div className="hero-badge">
            <FaGavel /> Juris • Your Legal Research Assistant
          </div>
          <h1 className="hero-title">Indian Criminal Law Analysis</h1>
          <p className="hero-subtitle">
            Combines formal statutory knowledge engineering across 158 IPC sections with Groq semantic vector retrieval.
          </p>
        </div>

        {/* ── Segmented Control (Dual Engine Tabs) ──────────────────────── */}
        <div className="tab-switcher-wrapper">
          <div className="tab-switcher">
            <button
              className={`tab-btn ${activeTab === 'expert' ? 'active' : ''}`}
              onClick={() => setActiveTab('expert')}
            >
              <FaBalanceScale /> Statutory Expert Engine
            </button>
            <button
              className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <FaRobot /> Conversational AI Research
            </button>
          </div>
        </div>

        {/* ── TAB 1: STATUTORY EXPERT SYSTEM ───────────────────────────── */}
        {activeTab === 'expert' && (
          <div className="app-card">
            <div className="card-header-row">
              <div>
                <h2 className="card-title">
                  <FaGavel /> Statutory Forward-Chaining Analysis
                </h2>
                <p className="card-description">
                  Input factual case narrative. The symbolic reasoning engine parses legal facts, executes forward-chaining across all IPC sections, and generates explainable audit traces.
                </p>
              </div>
            </div>

            {/* Quick Presets */}
            <div className="case-chips-section">
              <div className="case-chips-label">Quick Scenario Presets</div>
              <div className="case-chips-grid">
                {CASE_PRESETS.map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="case-chip"
                    onClick={() => handleSelectPreset(preset.text)}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Incident Form */}
            <form onSubmit={submitExpertAnalysis} className="incident-form">
              <div className="textarea-container">
                <textarea
                  className="incident-textarea"
                  value={problemInput}
                  onChange={(e) => setProblemInput(e.target.value)}
                  placeholder="Describe the incident narrative in plain English (e.g., 'A group entered my house at night with knives, threatened my family, and stole gold ornaments')..."
                />
                <div className="textarea-footer">
                  <span>Characters: {problemInput.length} | Words: {problemInput.trim() ? problemInput.trim().split(/\s+/).length : 0}</span>
                  {isListening && <span style={{ color: '#dc2626', fontWeight: 600 }}>● Microphone listening...</span>}
                </div>
              </div>

              <div className="form-actions-row">
                <button
                  type="button"
                  onClick={toggleSpeech}
                  className={`btn-action btn-dictate ${isListening ? 'recording' : ''}`}
                >
                  {isListening ? <><FaStop /> Stop Dictating</> : <><FaMicrophone /> Speech Dictation</>}
                </button>

                <button
                  type="submit"
                  disabled={isAnalyzing || !problemInput.trim()}
                  className="btn-action btn-primary"
                >
                  {isAnalyzing ? (
                    <span>Evaluating 158 Rules...</span>
                  ) : (
                    <><FaPaperPlane /> Analyze Case Facts</>
                  )}
                </button>
              </div>
            </form>

            {/* Analysis Results View */}
            <AnimatePresence>
              {expertResults && (
                <motion.div
                  className="results-container"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                >
                  <div className="results-header">
                    <FaCheckCircle style={{ color: '#16a34a' }} />
                    <span>Inference Engine Evaluation Results</span>
                  </div>

                  {/* 1. Perfect Exact Matches */}
                  {expertResults.matched_sections && expertResults.matched_sections.length > 0 ? (
                    <div>
                      {expertResults.matched_sections.map((m, idx) => (
                        <div key={idx} className="match-card">
                          <div className="match-header">
                            <span className="section-badge">IPC Section {m.section_id}</span>
                            <span className="punishment-pill">
                              Specificity Score: {m.specificity || 1}
                            </span>
                          </div>
                          <div className="match-title">{m.description}</div>

                          {/* Explainable AI (XAI) Trace Toggle */}
                          <button
                            type="button"
                            className="xai-toggle-btn"
                            onClick={() =>
                              setExpandedXaiId(expandedXaiId === m.section_id ? null : m.section_id)
                            }
                          >
                            <FaInfoCircle />
                            {expandedXaiId === m.section_id ? 'Hide Reasoning Audit' : 'Audit Reasoning (Explainable AI)'}
                            {expandedXaiId === m.section_id ? <FaChevronUp /> : <FaChevronDown />}
                          </button>

                          {expandedXaiId === m.section_id && (
                            <motion.div
                              className="xai-audit-box"
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                            >
                              <strong>Rule Audit Trace:</strong> All necessary statutory conditions for Section {m.section_id} were satisfied by the extracted case facts. No statutory exceptions were triggered.
                            </motion.div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : expertResults.partial_matches && expertResults.partial_matches.length > 0 ? (
                    /* 2. Partial Matches & Intelligent Fallback */
                    <div className="partial-card">
                      <div className="partial-title">
                        <FaExclamationTriangle />
                        <span>Incomplete Factual Basis — Partial Statutory Matches</span>
                      </div>
                      <p className="partial-note">
                        We detected <strong>{expertResults.partial_matches.length} partial match(es)</strong>. Certain mandatory statutory legal elements are missing or ambiguous in your description.
                      </p>

                      <button
                        type="button"
                        className="xai-toggle-btn"
                        onClick={() => setShowPartial(!showPartial)}
                      >
                        {showPartial ? <><FaChevronUp /> Hide Missing Elements</> : <><FaChevronDown /> View Missing & Matched Elements</>}
                      </button>

                      {showPartial && (
                        <div style={{ marginTop: '0.8rem' }}>
                          {expertResults.partial_matches.map((p, pIdx) => (
                            <div key={pIdx} style={{ padding: '0.6rem 0', borderBottom: '1px solid rgba(217,119,6,0.15)' }}>
                              <strong>IPC Section {p.section_id}</strong>: {p.description}
                              <div style={{ marginTop: '0.3rem' }}>
                                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#166534', marginRight: '0.4rem' }}>Satisfied:</span>
                                {p.matched_conditions && p.matched_conditions.map((c, i) => (
                                  <span key={i} className="condition-tag matched">✓ {c}</span>
                                ))}
                              </div>
                              <div style={{ marginTop: '0.2rem' }}>
                                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#991b1b', marginRight: '0.4rem' }}>Unsatisfied/Missing:</span>
                                {p.unmatched_conditions && p.unmatched_conditions.map((c, i) => (
                                  <span key={i} className="condition-tag missing">✗ {c}</span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="partial-escalation-row">
                        <div>
                          <strong>Recommended Escalation:</strong>
                          <div style={{ fontSize: '0.85rem', color: '#4b5563' }}>
                            Synthesize this nuanced situation via our Groq RAG model.
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={submitInlineRag}
                          disabled={isInlineRagLoading || quotaRemaining <= 0}
                          className="btn-escalate-rag"
                        >
                          {isInlineRagLoading ? (
                            <span>Synthesizing Legal Corpus...</span>
                          ) : (
                            <><FaRobot /> Escalate to Groq RAG AI ({quotaRemaining} left)</>
                          )}
                        </button>
                      </div>

                      {/* If quota reached 0 */}
                      {quotaRemaining <= 0 && (
                        <div className="rate-limit-card" style={{ marginTop: '1rem' }}>
                          <div className="rate-limit-title">
                            <FaExclamationTriangle /> Daily Free AI Quota Reached (5/5)
                          </div>
                          <div className="rate-limit-text">
                            You have used your 5 free AI requests for today. To request higher quota, legal firm integration, or assistance:
                          </div>
                          <a
                            href="mailto:ashishsingh67788@gmail.com?subject=VidhiAI%20Quota%20Extension%20Inquiry"
                            className="btn-mail-contact"
                          >
                            <FaEnvelope /> Contact: ashishsingh67788@gmail.com
                          </a>
                        </div>
                      )}

                      {/* Inline RAG Response Space */}
                      {inlineRagResponse && (
                        <motion.div
                          className="inline-rag-box"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                        >
                          <div style={{ fontWeight: 700, color: '#6d28d9', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <FaRobot /> Generative RAG Analysis & Precedent Overview:
                          </div>
                          <div style={{ whiteSpace: 'pre-wrap' }}>{inlineRagResponse}</div>
                        </motion.div>
                      )}
                    </div>
                  ) : (
                    /* 3. No match found */
                    <div className="no-match-card">
                      <FaInfoCircle style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#64748b' }} />
                      <p>
                        No matching IPC statutory offenses detected from the provided facts. Try expanding key details (e.g. actions, intent, consequences) or inquire via the Conversational AI tab.
                      </p>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* ── TAB 2: CONVERSATIONAL AI RESEARCH ─────────────────────────── */}
        {activeTab === 'chat' && (
          <div className="app-card">
            <div className="card-header-row">
              <div>
                <h2 className="card-title">
                  <FaRobot /> Conversational Legal Assistant
                </h2>
                <p className="card-description">
                  Direct semantic interaction with the Indian Penal Code vector store via Groq high-speed inference.
                </p>
              </div>

              <div className={`quota-counter-pill ${getQuotaClass()}`}>
                <FaBolt /> Daily Free AI Quota: {quotaRemaining} / {dailyLimit} left
              </div>
            </div>

            {/* Rate limit banner if quota is exhausted */}
            {quotaRemaining <= 0 && (
              <div className="rate-limit-card">
                <div className="rate-limit-title">
                  <FaExclamationTriangle /> Daily Quota Limit Reached (5/5)
                </div>
                <div className="rate-limit-text">
                  Logged-in accounts receive 5 free AI queries per day. For extended quota, law firm licensing, or specific legal inquiries, contact the developer:
                </div>
                <a
                  href="mailto:ashishsingh67788@gmail.com?subject=VidhiAI%20Extended%20Quota%20Request"
                  className="btn-mail-contact"
                >
                  <FaEnvelope /> Contact Developer: ashishsingh67788@gmail.com
                </a>
              </div>
            )}

            {/* Chat Messages Window */}
            <div className="chat-window">
              <div className="chat-messages-area">
                {chatHistory.length === 1 ? (
                  <div className="chat-empty-state">
                    <FaBalanceScale className="chat-empty-icon" />
                    <h3 style={{ fontSize: '1.1rem', color: '#1e3a8a', marginBottom: '0.4rem' }}>
                      Start Your Indian Law Query
                    </h3>
                    <p style={{ fontSize: '0.88rem', maxWidth: '420px', lineHeight: 1.5 }}>
                      Ask questions regarding statutory IPC offenses, punishments, cognizable classifications, or case scenarios.
                    </p>

                    <div className="suggested-prompts-grid">
                      {SUGGESTED_CHAT_PROMPTS.map((promptText, i) => (
                        <button
                          key={i}
                          type="button"
                          className="suggested-prompt-btn"
                          onClick={(e) => submitChat(e, promptText)}
                          disabled={quotaRemaining <= 0 || isChatLoading}
                        >
                          → {promptText}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  chatHistory.map((msg, i) => (
                    <div key={i} className={`msg-row ${msg.role}`}>
                      <span className="msg-sender">{msg.role === 'user' ? 'You' : 'VidhiAI Assistant'}</span>
                      <div className="msg-bubble">
                        <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                        {msg.rateLimited && (
                          <div style={{ marginTop: '0.8rem' }}>
                            <a
                              href="mailto:ashishsingh67788@gmail.com?subject=VidhiAI%20Quota%20Inquiry"
                              className="btn-mail-contact"
                            >
                              <FaEnvelope /> Contact: ashishsingh67788@gmail.com
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                <div ref={chatEndRef} />
              </div>
            </div>

            {/* Chat Input Row */}
            <form onSubmit={submitChat} className="chat-input-form">
              <input
                type="text"
                className="chat-text-input"
                placeholder={
                  quotaRemaining <= 0
                    ? "Daily limit of 5 queries reached. Please contact us via email for access."
                    : "Ask about any IPC section, defense, or punishment..."
                }
                value={chatInput}
                disabled={quotaRemaining <= 0 || isChatLoading}
                onChange={(e) => setChatInput(e.target.value)}
              />

              <button
                type="submit"
                disabled={quotaRemaining <= 0 || isChatLoading || !chatInput.trim()}
                className="btn-action btn-send"
              >
                {isChatLoading ? <span>...</span> : <><FaPaperPlane /> Send</>}
              </button>

              {chatHistory.length > 1 && (
                <button
                  type="button"
                  onClick={() =>
                    setChatHistory([
                      {
                        role: 'assistant',
                        content: 'Chat cleared. How can I assist your Indian Penal Code research today?'
                      }
                    ])
                  }
                  className="btn-action btn-dictate"
                  title="Clear Chat History"
                >
                  <FaTrashAlt />
                </button>
              )}
            </form>
          </div>
        )}
      </main>

      {/* ── Persistent Editorial Footer & Contact Clause ─────────────── */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-brand-row">
            <FaBalanceScale style={{ color: 'var(--brand-bronze)' }} />
            <span>Juris - Your Legal Research Assistant</span>
          </div>

          <p className="footer-disclaimer">
            Juris is an intelligent statutory research engine for Indian Criminal Jurisprudence. It provides automated statutory references for educational and preparatory research and should always be verified against official court gazettes and qualified legal counsel.
          </p>

          <div className="footer-contact-clause">
            <span>Have questions, need enterprise law firm deployment, or require higher API quotas?</span>
          </div>

          <a
            href="mailto:ashishsingh67788@gmail.com?subject=Juris%20Legal%20Assistant%20Enterprise%20and%20Support%20Inquiry"
            className="footer-mail-link"
          >
            <FaEnvelope /> Contact: ashishsingh67788@gmail.com
          </a>
        </div>
      </footer>
    </div>
  );
}