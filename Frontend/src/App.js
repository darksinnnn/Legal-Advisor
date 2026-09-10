import React, { useEffect } from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import SignIn from './SignIn';
import Home from './Home';
import { auth } from './firebase';
import { useAuthState } from 'react-firebase-hooks/auth';

// Animation variants
const pageVariants = {
  initial: {
    opacity: 0,
    y: 20
  },
  in: {
    opacity: 1,
    y: 0
  },
  out: {
    opacity: 0,
    y: -20
  }
};

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.5
};

// Animated page wrapper component
const AnimatedPage = ({ children }) => {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      style={{ width: '100%', height: '100%' }}
    >
      {children}
    </motion.div>
  );
};

// Global styles
const globalStyles = `
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    margin: 0;
    padding: 0;
    font-family: 'Poppins', 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
  }
  
  a {
    text-decoration: none;
  }
  
  button {
    cursor: pointer;
  }
`;

function App() {
  const [user, loading] = useAuthState(auth);
  const location = useLocation();

  // Inject global styles
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = globalStyles;
    document.head.appendChild(style);
    
    // Add Google Fonts
    const link = document.createElement('link');
    link.href = "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap";
    link.rel = "stylesheet";
    document.head.appendChild(link);
    
    return () => {
      document.head.removeChild(style);
      document.head.removeChild(link);
    };
  }, []);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5',
        fontSize: '1.5rem',
        color: '#333'
      }}>
        <div style={{
          padding: '2rem',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 5px 15px rgba(0, 0, 0, 0.1)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '5px solid #f3f3f3',
            borderTop: '5px solid #3498db',
            borderRadius: '50%',
            margin: '0 auto 1rem',
            animation: 'spin 1s linear infinite'
          }}></div>
          Loading...
        </div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Redirect root ("/") to "/signin" */}
        <Route path="/" element={<Navigate to="/signin" replace />} />

        <Route path="/signin" element={
          user ? <Navigate to="/home" replace /> : (
            <AnimatedPage>
              <SignIn />
            </AnimatedPage>
          )
        } />

        {/* Protected Route */}
        <Route path="/home" element={
          user ? (
            <AnimatedPage>
              <Home />
            </AnimatedPage>
          ) : (
            <Navigate to="/signin" replace />
          )
        } />

        {/* Catch-all Route */}
        <Route path="*" element={<Navigate to="/signin" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default App;
