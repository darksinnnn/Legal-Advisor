import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaPaperPlane, FaSignOutAlt, FaRobot } from 'react-icons/fa';
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
  const chatEndRef = useRef(null);
  const navigate = useNavigate();

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
    setIsInlineRagLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/analyze_rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: problemInput, history: [] }),
      });
      const data = await res.json();
      if (data.success) {
        setInlineRagResponse(data.message);
      } else {
        setInlineRagResponse("Error: " + data.message);
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

    const userMessage = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsChatLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:5000/analyze_rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, history: chatHistory }),
      });
      const data = await res.json();
      if (data.success) {
        setChatHistory(prev => [...prev, { role: 'assistant', content: data.message }]);
      } else {
        setChatHistory(prev => [...prev, { role: 'assistant', content: "⚠️ Error: " + data.message }]);
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

                       <p style={{fontSize:'0.9rem', fontWeight:600}}>
                         Advice: For a deeper analysis of this nuanced scenario, we strongly recommend giving this same query to our RAG AI model.
                       </p>
                       
                       <motion.button 
                         type="button" 
                         onClick={submitInlineRag} 
                         style={{...styles.button, ...styles.ragButton}}
                         whileHover={{scale:1.02}}
                         disabled={isInlineRagLoading}
                       >
                         {isInlineRagLoading ? <span style={styles.spinner}/> : <><FaRobot/> Analyze with RAG Model</>}
                       </motion.button>

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
            <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '1rem'}}>
              Interact directly with the Generative AI referencing the FAISS database.
            </p>

            <div style={styles.chatContainer}>
              {chatHistory.map((msg, i) => (
                <div key={i} style={{...styles.chatMessage, ...(msg.role === 'user' ? styles.userMessage : styles.botMessage)}}>
                  <strong style={{display:'block', fontSize:'0.8rem', color:'#555', marginBottom:'0.2rem'}}>
                    {msg.role === 'user' ? 'You' : 'AI Assistant'}
                  </strong>
                  <span style={{whiteSpace:'pre-wrap', fontSize: '0.95rem'}}>{msg.content}</span>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            <form onSubmit={submitChat} style={styles.chatInputRow}>
              <input
                type="text"
                placeholder="Ask about a section or punishment..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                style={styles.chatInput}
              />
              <motion.button type="submit" disabled={isChatLoading} style={{...styles.button, ...styles.submitButton, flex: '0 0 auto'}} whileHover={{scale:1.05}}>
                {isChatLoading ? <span style={styles.spinner}/> : <FaPaperPlane/>}
              </motion.button>
            </form>
          </div>
          )}
        </div>
      </main>
    </div>
  );
}