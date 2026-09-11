import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaPaperPlane, FaSignOutAlt, FaRobot, FaEnvelope, FaBolt, FaExclamationTriangle } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { auth } from './firebase';
import './Home.css';

// Home component styles inline to keep previous patterns intact
const styles = {
  container: (offset) => ({
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: `linear-gradient(
      ${offset}deg,
      rgba(75, 75, 212, 0.9),
      rgba(79, 41, 89, 0.95),
      rgba(138, 43, 226, 0.9)
    )`,
    backgroundSize: '200% 200%',
    color: '#ffffff',
    fontFamily: "'Poppins', 'Segoe UI', sans-serif",
  }),
  navbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.2rem 2.5rem',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },
  logoTitle: {
    fontSize: '1.5rem',
    fontWeight: 600,
    letterSpacing: '1px',
    margin: 0,
    background: 'linear-gradient(45deg, #ffffff, #e0f7fa)',
    WebkitBackgroundClip: 'text',
    backgroundClip: 'text',
    color: 'transparent',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  logoutButton: {
    padding: '0.7rem 1.5rem',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  mainContent: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '2rem 1rem',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
  },
  heroSection: {
    textAlign: 'center',
    marginBottom: '2rem',
  },
  heroTitle: {
    fontSize: '2.5rem',
    marginBottom: '0.5rem',
    background: 'linear-gradient(45deg, #ffffff, #b3e5fc)',
    WebkitBackgroundClip: 'text',
    backgroundClip: 'text',
    color: 'transparent',
  },
  twoColumnContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
    alignItems: 'center',
    width: '100%',
    maxWidth: '800px',
    margin: '0 auto',
  },
  tabsContainer: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1rem',
    marginBottom: '2rem',
  },
  tabButton: (isActive) => ({
    padding: '1rem 2rem',
    background: isActive ? 'rgba(255, 255, 255, 0.95)' : 'rgba(255, 255, 255, 0.2)',
    color: isActive ? '#008080' : 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1.1rem',
    fontWeight: 600,
    transition: 'all 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    boxShadow: isActive ? '0 4px 15px rgba(0, 0, 0, 0.1)' : 'none',
  }),
  card: {
    background: 'rgba(255, 255, 255, 0.95)',
    padding: '2.5rem',
    borderRadius: '16px',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
    color: '#333',
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  cardTitle: {
    fontSize: '1.5rem',
    marginBottom: '1rem',
    color: '#008080',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  textarea: {
    width: '100%',
    padding: '1rem',
    border: '1px solid #ccc',
    borderRadius: '8px',
    resize: 'vertical',
    fontFamily: 'inherit',
    fontSize: '1rem',
    minHeight: '120px',
    marginBottom: '1rem',
  },
  buttonGroup: {
    display: 'flex',
    gap: '1rem',
    flexWrap: 'wrap',
  },
  button: {
    padding: '0.8rem 1.5rem',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    flex: 1,
    color: 'white',
  },
  submitButton: {
    backgroundColor: '#008080',
  },
  speechButton: {
    backgroundColor: '#4a90e2',
  },
  listeningButton: {
    backgroundColor: '#dc3545',
  },
  ragButton: {
    backgroundColor: '#8a2be2',
    marginTop: '1rem',
    width: '100%',
  },
  boxStyle: {
    padding: '1rem',
    borderRadius: '8px',
    marginBottom: '1rem',
    border: '1px solid #ddd',
  },
  perfectMatch: {
    backgroundColor: '#e6ffe6',
    borderLeft: '4px solid #28a745',
  },
  partialMatchNote: {
    backgroundColor: '#fff3cd',
    borderLeft: '4px solid #ffc107',
  },
  chatContainer: {
    flex: 1,
    overflowY: 'auto',
    maxHeight: '400px',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    marginBottom: '1rem',
    paddingRight: '0.5rem',
  },
  chatMessage: {
    padding: '1rem',
    borderRadius: '12px',
    maxWidth: '85%',
  },
  userMessage: {
    backgroundColor: '#e0f7fa',
    alignSelf: 'flex-end',
    borderBottomRightRadius: 0,
  },
  botMessage: {
    backgroundColor: '#f1f3f5',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 0,
  },
  chatInputRow: {
    display: 'flex',
    gap: '0.5rem',
  },
  chatInput: {
    flex: 1,
    padding: '0.8rem',
    borderRadius: '8px',
    border: '1px solid #ccc',
  },
  spinner: {
    display: 'inline-block',
    width: '16px',
    height: '16px',
    border: '2px solid rgba(255,255,255,.3)',
    borderRadius: '50%',
    borderTopColor: 'white',
    animation: 'spin 1s ease-in-out infinite',
  },
  quotaBadge: (remaining) => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.4rem',
    padding: '0.35rem 0.8rem',
    borderRadius: '20px',
    fontSize: '0.82rem',
    fontWeight: 600,
    background: remaining > 2 ? 'rgba(40, 167, 69, 0.15)' : remaining > 0 ? 'rgba(255, 193, 7, 0.2)' : 'rgba(220, 53, 69, 0.2)',
    color: remaining > 2 ? '#28a745' : remaining > 0 ? '#b58105' : '#dc3545',
    border: `1px solid ${remaining > 2 ? 'rgba(40, 167, 69, 0.3)' : remaining > 0 ? 'rgba(255, 193, 7, 0.4)' : 'rgba(220, 53, 69, 0.4)'}`,
  }),
  contactBanner: {
    marginTop: '1rem',
    padding: '1.1rem',
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '10px',
    border: '1px solid #ffc107',
    borderLeft: '5px solid #dc3545',
    color: '#333',
    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)',
  },
  mailButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.6rem 1.2rem',
    backgroundColor: '#6c5ce7',
    color: 'white',
    borderRadius: '8px',
    fontWeight: 600,
    fontSize: '0.9rem',
    textDecoration: 'none',
    marginTop: '0.6rem',
    cursor: 'pointer',
    border: 'none',
    boxShadow: '0 2px 8px rgba(108, 92, 231, 0.3)',
  },
  footerClause: {
    marginTop: 'auto',
    textAlign: 'center',
    padding: '2.5rem 1rem 1rem',
    color: 'rgba(255, 255, 255, 0.85)',
    fontSize: '0.9rem',
  },
  footerMailLink: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.55rem 1.2rem',
    background: 'rgba(255, 255, 255, 0.15)',
    color: 'white',
    borderRadius: '8px',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    textDecoration: 'none',
    fontWeight: 500,
    marginTop: '0.5rem',
    backdropFilter: 'blur(5px)',
  },
  responsive: {
    grid: {
      gridTemplateColumns: '1fr',
    }
  }
};

const keyframes = `
  @keyframes spin { to { transform: rotate(360deg); } }
  .listening-indicator::before { content: '●'; color: white; margin-right: 0.5rem; animation: pulse 1.5s infinite; }
`;

export default function Home() {
  const [offset, setOffset] = useState(0);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 968);
  const [activeTab, setActiveTab] = useState('expert'); // 'expert' | 'chat'
  
  // Rule-Based State
  const [problemInput, setProblemInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [expertResults, setExpertResults] = useState(null);
  const [inlineRagResponse, setInlineRagResponse] = useState('');
  const [isInlineRagLoading, setIsInlineRagLoading] = useState(false);
  const [showPartial, setShowPartial] = useState(false);

  // Conversational AI (RAG) State
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Hello! Ask me any specific question about the Indian Penal Code, or chat about an incident.' }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [quotaRemaining, setQuotaRemaining] = useState(5);
  const [dailyLimit, setDailyLimit] = useState(5);
  const [isRateLimited, setIsRateLimited] = useState(false);
  const chatEndRef = useRef(null);
  const navigate = useNavigate();

  // Fetch initial user quota
  useEffect(() => {
    const fetchQuota = async () => {
      const user = auth.currentUser;
      if (user?.uid) {
        try {
          const res = await fetch(`http://127.0.0.1:5000/user_quota?user_id=${encodeURIComponent(user.uid)}`);
          const data = await res.json();
          if (data.success) {
            setQuotaRemaining(data.remaining);
            setDailyLimit(data.daily_limit);
            setIsRateLimited(data.remaining <= 0);
          }
        } catch (e) {
          console.log("Could not fetch user quota:", e);
        }
      }
    };
    fetchQuota();
  }, []);

  // Init
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 968);
    window.addEventListener('resize', handleResize);
    
    const style = document.createElement('style');
    style.innerHTML = keyframes;
    document.head.appendChild(style);

    if (window.webkitSpeechRecognition) {
      const recognitionInstance = new window.webkitSpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(r => r[0].transcript).join('');
        setProblemInput(transcript);
      };
      recognitionInstance.onerror = () => setIsListening(false);
      setRecognition(recognitionInstance);
    }

    const intervalId = setInterval(() => setOffset(prev => (prev + 1) % 360), 50);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      document.head.removeChild(style);
      clearInterval(intervalId);
    };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleLogout = async () => {
    await auth.signOut();
    navigate('/signin');
  };

  const handleSpeech = () => {
    if (!recognition) return alert('Speech recognition not supported.');
    if (!isListening) { recognition.start(); setIsListening(true); }
    else { recognition.stop(); setIsListening(false); }
  };

  // 1. Submit for Expert System Analysis
  const submitExpertAnalysis = async (e) => {
    e.preventDefault();
    if (!problemInput.trim()) return;
    
    setIsAnalyzing(true);
    setExpertResults(null);
    setInlineRagResponse('');
    
    try {
      const res = await fetch('http://127.0.0.1:5000/analyze_rule_based', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: problemInput }),
      });
      const data = await res.json();
      if (data.success) {
        setExpertResults(data);
      } else {
        alert("Error: " + data.message);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to connect to backend server.");
    }
    setIsAnalyzing(false);
  };

  // 2. Submit Inline RAG Query (when partial match occurs)
  const submitInlineRag = async () => {
    const user = auth.currentUser;
    if (!user) {
      alert("🔒 Authentication Required: Please log in to query the AI RAG model.");
      navigate('/signin');
      return;
    }

    if (quotaRemaining <= 0) {
      alert("⚠️ Daily Limit Reached: You have used your 5 free AI queries for today. Contact ashishsingh67788@gmail.com for extended access.");
      setIsRateLimited(true);
      return;
    }

    setIsInlineRagLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/analyze_rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: problemInput,
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

  // 3. Submit Chat Message to pure RAG
  const submitChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || isChatLoading) return;

    const user = auth.currentUser;
    if (!user) {
      alert("🔒 Authentication Required: Please log in to chat with the AI assistant.");
      navigate('/signin');
      return;
    }

    if (quotaRemaining <= 0) {
      setChatHistory(prev => [
        ...prev,
        {
          role: 'assistant',
          content: "⚠️ Daily Limit Reached: You have used your 5 free AI queries for today. Please contact ashishsingh67788@gmail.com for extended access.",
          rateLimited: true
        }
      ]);
      setIsRateLimited(true);
      return;
    }

    const userMessage = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsChatLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:5000/analyze_rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          history: chatHistory,
          user_id: user.uid,
          user_email: user.email
        }),
      });
      const data = await res.json();
      if (data.success) {
        setChatHistory(prev => [...prev, { role: 'assistant', content: data.message }]);
        if (typeof data.remaining === 'number') {
          setQuotaRemaining(data.remaining);
          setIsRateLimited(data.remaining <= 0);
        }
      } else {
        setChatHistory(prev => [
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
      setChatHistory(prev => [...prev, { role: 'assistant', content: "⚠️ Warning: Failed to reach backend." }]);
    }
    setIsChatLoading(false);
  };

  return (
    <div style={styles.container(offset)}>
      <nav style={styles.navbar}>
        <h1 style={styles.logoTitle}>⚖️ LEGAL RESEARCH ASSISTANT</h1>
        <motion.button onClick={handleLogout} style={styles.logoutButton} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <FaSignOutAlt /> Logout
        </motion.button>
      </nav>

      <main style={styles.mainContent}>
        <div style={styles.heroSection}>
          <h2 style={styles.heroTitle}>Dual-Engine Legal Assistant</h2>
          <p>Analyze incidents deterministically via rules, or chat dynamically via Generative AI.</p>
        </div>

        {/* TOP COMPONENT TAB NAVIGATION */}
        <div style={styles.tabsContainer}>
          <button 
            style={styles.tabButton(activeTab === 'expert')} 
            onClick={() => setActiveTab('expert')}
          >
            🏛️ Expert System
          </button>
          <button 
            style={styles.tabButton(activeTab === 'chat')} 
            onClick={() => setActiveTab('chat')}
          >
            💬 Conversational AI
          </button>
        </div>

        <div style={styles.twoColumnContainer}>
          
          {/* TAB 1: RULE BASED SYSTEM */}
          {activeTab === 'expert' && (
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>🏛️ Expert System Analysis</h3>
            <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '1rem'}}>
              Strict, rule-based inference for finding exact IPC matches.
            </p>
            
            <form onSubmit={submitExpertAnalysis}>
              <textarea
                value={problemInput}
                onChange={(e) => setProblemInput(e.target.value)}
                placeholder="Describe your incident (e.g. 'Someone broke into my house at night and took my laptop')..."
                style={styles.textarea}
              />
              <div style={styles.buttonGroup}>
                <motion.button type="button" onClick={handleSpeech} style={{...styles.button, ...styles.speechButton, ...(isListening && styles.listeningButton)}} whileHover={{scale:1.02}}>
                  {isListening ? <><FaStop/> Stop</> : <><FaMicrophone/> Dictate</>}
                </motion.button>
                <motion.button type="submit" disabled={isAnalyzing} style={{...styles.button, ...styles.submitButton}} whileHover={{scale:1.02}}>
                  {isAnalyzing ? <span style={styles.spinner}/> : <><FaPaperPlane/> Analyze</>}
                </motion.button>
              </div>
            </form>

            {/* Analysis Results Display */}
            <div style={{marginTop: '2rem', overflowY: 'auto'}}>
              {expertResults && (
                <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}}>
                  {expertResults.matched_sections.length > 0 ? (
                    <div>
                      <h4 style={{color:'#28a745', marginBottom:'0.5rem'}}>Perfect Matches Found:</h4>
                      {expertResults.matched_sections.map((m, i) => (
                        <div key={i} style={{...styles.boxStyle, ...styles.perfectMatch}}>
                          <strong>Section {m.section_id}</strong>: {m.description}
                        </div>
                      ))}
                    </div>
                  ) : expertResults.partial_matches.length > 0 ? (
                     <div style={{...styles.boxStyle, ...styles.partialMatchNote}}>
                       <h4 style={{color:'#856404', margin: '0 0 0.5rem 0'}}>⚠️ No Perfect Rule Matches</h4>
                       <p style={{fontSize:'0.9rem', marginBottom:'1rem', color:'#666'}}>
                         We found <strong>{expertResults.partial_matches.length} partial matches</strong>, but the facts are ambiguous or incomplete.
                       </p>

                       <button 
                         onClick={() => setShowPartial(!showPartial)}
                         style={{background:'none', border:'none', color:'#008080', cursor:'pointer', fontWeight:600, padding:0, marginBottom:'1rem', display:'block'}}
                       >
                         {showPartial ? '▲ Hide Partial Matches' : '▼ View Partial Matches'}
                       </button>

                       {showPartial && (
                         <div style={{background:'rgba(255,255,255,0.5)', padding:'1rem', borderRadius:'8px', marginBottom:'1rem', maxHeight: '200px', overflowY: 'auto'}}>
                           {expertResults.partial_matches.map((p, i) => (
                             <div key={i} style={{marginBottom:'1rem', paddingBottom:'0.5rem', borderBottom:'1px solid #ddd'}}>
                               <strong>Section {p.section_id}</strong>
                               <div style={{fontSize:'0.85rem', color:'#666'}}><span style={{color:'green'}}>✓ Matched:</span> {p.matched_conditions.join(', ')}</div>
                               <div style={{fontSize:'0.85rem', color:'#666'}}><span style={{color:'red'}}>✗ Missing:</span> {p.unmatched_conditions.join(', ')}</div>
                             </div>
                           ))}
                         </div>
                       )}

                       <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', margin: '0.8rem 0 0.4rem'}}>
                         <p style={{fontSize:'0.9rem', fontWeight:600, margin: 0}}>
                           Advice: For a deeper analysis of this nuanced scenario, we strongly recommend giving this same query to our RAG AI model.
                         </p>
                         <span style={styles.quotaBadge(quotaRemaining)}>
                           <FaBolt /> {quotaRemaining}/{dailyLimit} left
                         </span>
                       </div>
                       
                       <motion.button 
                         type="button" 
                         onClick={submitInlineRag} 
                         style={{
                           ...styles.button,
                           ...styles.ragButton,
                           opacity: quotaRemaining <= 0 ? 0.6 : 1,
                           cursor: quotaRemaining <= 0 ? 'not-allowed' : 'pointer'
                         }}
                         whileHover={{scale: quotaRemaining <= 0 ? 1 : 1.02}}
                         disabled={isInlineRagLoading || quotaRemaining <= 0}
                       >
                         {isInlineRagLoading ? <span style={styles.spinner}/> : <><FaRobot/> Analyze with RAG Model</>}
                       </motion.button>

                       {quotaRemaining <= 0 && (
                         <div style={{...styles.contactBanner, marginTop: '0.8rem'}}>
                           <div style={{color: '#c0392b', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem'}}>
                             <FaExclamationTriangle /> Daily AI Limit Reached (5/5)
                           </div>
                           <p style={{fontSize:'0.85rem', margin:'0.3rem 0', color:'#555'}}>
                             You have reached your 5 free AI queries for today. If you want to contact for higher quota or queries, email us below:
                           </p>
                           <a href="mailto:ashishsingh67788@gmail.com?subject=Legal%20Advisor%20Quota%20Inquiry" style={styles.mailButton}>
                             <FaEnvelope /> Contact: ashishsingh67788@gmail.com
                           </a>
                         </div>
                       )}

                       {/* Inline RAG Result Space */}
                       {inlineRagResponse && (
                         <motion.div initial={{opacity:0, height:0}} animate={{opacity:1, height:'auto'}} style={{marginTop: '1rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px', borderLeft: '4px solid #8a2be2', whiteSpace:'pre-wrap', fontSize:'0.9rem'}}>
                           <strong>RAG Response:</strong><br/><br/>
                           {inlineRagResponse}
                         </motion.div>
                       )}
                     </div>
                  ) : (
                    <div style={{...styles.boxStyle, backgroundColor:'#f8d7da', borderLeft: '4px solid #dc3545', color:'#721c24'}}>
                      Could not detect any relevant IPC crimes from your description.
                    </div>
                  )}
                </motion.div>
              )}
            </div>

          </div>
          )}

          {/* TAB 2: PURE RAG CONVERSATIONAL AI */}
          {activeTab === 'chat' && (
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>💬 Conversational AI</h3>
            
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'0.8rem', flexWrap:'wrap', gap:'0.5rem'}}>
              <p style={{fontSize: '0.9rem', color: '#666', margin: 0}}>
                Interact directly with the Generative AI referencing the FAISS database.
              </p>
              <div style={styles.quotaBadge(quotaRemaining)}>
                <FaBolt /> Daily Quota: {quotaRemaining} / {dailyLimit} left
              </div>
            </div>

            {quotaRemaining <= 0 && (
              <div style={{...styles.contactBanner, marginBottom: '1rem'}}>
                <div style={{color: '#c0392b', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem'}}>
                  <FaExclamationTriangle /> Daily AI Limit Reached (5/5)
                </div>
                <p style={{fontSize:'0.88rem', margin:'0.3rem 0', color:'#555'}}>
                  Logged-in accounts receive 5 free AI queries per day. If you want to contact for extended limits or questions, email us below:
                </p>
                <a href="mailto:ashishsingh67788@gmail.com?subject=Legal%20Advisor%20Quota%20Inquiry" style={styles.mailButton}>
                  <FaEnvelope /> Contact: ashishsingh67788@gmail.com
                </a>
              </div>
            )}

            <div style={styles.chatContainer}>
              {chatHistory.map((msg, i) => (
                <div key={i} style={{...styles.chatMessage, ...(msg.role === 'user' ? styles.userMessage : styles.botMessage)}}>
                  <strong style={{display:'block', fontSize:'0.8rem', color:'#555', marginBottom:'0.2rem'}}>
                    {msg.role === 'user' ? 'You' : 'AI Assistant'}
                  </strong>
                  <span style={{whiteSpace:'pre-wrap', fontSize: '0.95rem'}}>{msg.content}</span>
                  {msg.rateLimited && (
                    <div style={{marginTop: '0.6rem'}}>
                      <a href="mailto:ashishsingh67788@gmail.com?subject=Legal%20Advisor%20Quota%20Inquiry" style={styles.mailButton}>
                        <FaEnvelope /> Contact: ashishsingh67788@gmail.com
                      </a>
                    </div>
                  )}
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            <form onSubmit={submitChat} style={styles.chatInputRow}>
              <input
                type="text"
                placeholder={quotaRemaining <= 0 ? "Daily quota of 5 queries reached. Contact us for access." : "Ask about a section or punishment..."}
                value={chatInput}
                disabled={quotaRemaining <= 0 || isChatLoading}
                onChange={(e) => setChatInput(e.target.value)}
                style={{
                  ...styles.chatInput,
                  backgroundColor: quotaRemaining <= 0 ? '#f5f5f5' : 'white',
                  cursor: quotaRemaining <= 0 ? 'not-allowed' : 'text'
                }}
              />
              <motion.button 
                type="submit" 
                disabled={isChatLoading || quotaRemaining <= 0} 
                style={{
                  ...styles.button, 
                  ...styles.submitButton, 
                  flex: '0 0 auto',
                  opacity: quotaRemaining <= 0 ? 0.5 : 1,
                  cursor: quotaRemaining <= 0 ? 'not-allowed' : 'pointer'
                }} 
                whileHover={{scale: quotaRemaining <= 0 ? 1 : 1.05}}
              >
                {isChatLoading ? <span style={styles.spinner}/> : <FaPaperPlane/>}
              </motion.button>
            </form>
          </div>
          )}
        </div>

        {/* CONTACT CLAUSE FOOTER */}
        <footer style={styles.footerClause}>
          <p style={{margin: '0 0 0.4rem 0'}}>
            ⚖️ <strong>Legal Research Assistant</strong> • Daily limit: 5 AI queries per user.
          </p>
          <p style={{margin: '0 0 0.6rem 0', opacity: 0.9}}>
            If you want to contact for support, extended API limits, or general questions:
          </p>
          <a href="mailto:ashishsingh67788@gmail.com?subject=Legal%20Advisor%20Support%20Inquiry" style={styles.footerMailLink}>
            <FaEnvelope /> Contact: ashishsingh67788@gmail.com
          </a>
        </footer>
      </main>
    </div>
  );
}