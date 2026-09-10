import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaGoogle, FaMicrosoft, FaEye, FaEyeSlash } from 'react-icons/fa';
import logo from './images/logo.png';
import { auth, googleProvider, signInWithEmailAndPassword, signInWithPopup } from './firebase';

// SignIn component styles
const styles = {
  container: {
    minHeight: '100vh',
    width: '100%',
    background: 'linear-gradient(135deg, #6e8efb, #a777e3)',
    backgroundSize: '200% 200%',
    animation: 'gradientShift 15s ease infinite',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: "'Poppins', 'Segoe UI', sans-serif",
  },
  
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.2rem 2rem',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  
  headerTitle: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: 600,
    letterSpacing: '1px',
    color: 'white',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  
  headerButtons: {
    display: 'flex',
    gap: '1.2rem',
  },
  
  headerButton: {
    padding: '0.7rem 1.2rem',
    background: 'rgba(255, 255, 255, 0.2)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    fontWeight: 500,
    letterSpacing: '0.5px',
  },
  
  mainContent: {
    flexGrow: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '3rem 2rem',
  },
  
  logoContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  
  logoCircle: {
    width: '180px',
    height: '180px',
    backgroundColor: 'white',
    borderRadius: '50%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.08)',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
  
  logoImage: {
    width: '85%',
    height: 'auto',
    objectFit: 'contain',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
  
  subtitle: {
    fontSize: '1.2rem',
    color: 'white',
    marginBottom: '3rem',
    textAlign: 'center',
    fontWeight: 500,
    letterSpacing: '3px',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  
  signInForm: {
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    padding: '3rem',
    borderRadius: '16px',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.08)',
    width: '100%',
    maxWidth: '400px',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    border: '1px solid rgba(255, 255, 255, 0.18)',
  },
  
  formTitle: {
    textAlign: 'center',
    marginBottom: '2rem',
    color: '#333',
    fontSize: '1.8rem',
    fontWeight: 600,
  },
  
  errorMessage: {
    color: '#d32f2f',
    textAlign: 'center',
    margin: '0 0 1.5rem',
    padding: '0.75rem',
    backgroundColor: 'rgba(211, 47, 47, 0.1)',
    borderRadius: '8px',
    fontSize: '0.9rem',
  },
  
  inputGroup: {
    position: 'relative',
    marginBottom: '1.8rem',
  },
  
  input: {
    width: '100%',
    padding: '1rem 1.2rem',
    border: '1px solid rgba(0, 0, 0, 0.1)',
    borderRadius: '8px',
    fontSize: '1rem',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  
  inputFocus: {
    borderColor: '#4a6fdc',
    boxShadow: '0 0 0 3px rgba(74, 111, 220, 0.2)',
    outline: 'none',
  },
  
  visibilityButton: {
    position: 'absolute',
    right: '1rem',
    top: '50%',
    transform: 'translateY(-50%)',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    color: '#666',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  
  signInButton: {
    width: '100%',
    padding: '1rem',
    backgroundColor: '#4a6fdc',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 600,
    letterSpacing: '0.5px',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  
  socialSignIn: {
    marginTop: '2.5rem',
    textAlign: 'center',
  },
  
  socialText: {
    color: '#555',
    marginBottom: '1rem',
    fontSize: '0.9rem',
  },
  
  socialButtons: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1.2rem',
    marginTop: '1rem',
  },
  
  socialButton: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.8rem 1.2rem',
    borderRadius: '8px',
    border: '1px solid rgba(0, 0, 0, 0.1)',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    fontSize: '0.9rem',
    fontWeight: 500,
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
  },
  
  googleButton: {
    color: '#db4437',
  },
  
  microsoftButton: {
    color: '#00a4ef',
  },
  
  icon: {
    fontSize: '1.2rem',
    marginRight: '0.8rem',
  },
  
  forgotPassword: {
    display: 'block',
    textAlign: 'center',
    marginTop: '2rem',
    color: '#4a6fdc',
    background: 'none',
    border: 'none',
    fontSize: '0.9rem',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
  
  footer: {
    textAlign: 'center',
    padding: '1.5rem',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(5px)',
    WebkitBackdropFilter: 'blur(5px)',
    color: 'white',
    fontSize: '0.9rem',
    marginTop: 'auto',
  },
  
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    backdropFilter: 'blur(5px)',
    WebkitBackdropFilter: 'blur(5px)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  
  modalContent: {
    background: 'white',
    padding: '2.5rem',
    borderRadius: '16px',
    width: '90%',
    maxWidth: '600px',
    boxShadow: '0 25px 50px rgba(0, 0, 0, 0.1)',
  },
  
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
  },
  
  modalTitle: {
    fontSize: '1.8rem',
    color: '#333',
    margin: 0,
  },
  
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '1.8rem',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    color: '#666',
    height: '40px',
    width: '40px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '50%',
  },
  
  modalBody: {
    height: '500px',
    overflowY: 'auto',
  },

  // Media query styles - applied conditionally
  responsive: {
    header: {
      padding: '1rem',
      flexDirection: 'column',
      gap: '1rem',
    },
    signInForm: {
      padding: '2rem',
      width: '90%',
    },
    logoCircle: {
      width: '150px',
      height: '150px',
    }
  }
};

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { 
      staggerChildren: 0.2,
      when: "beforeChildren" 
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1,
    transition: { 
      type: "spring", 
      stiffness: 50
    }
  }
};

// CSS keyframes as a string to be injected
const keyframes = `
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.03); }
    100% { transform: scale(1); }
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
    20%, 40%, 60%, 80% { transform: translateX(10px); }
  }

  .shake {
    animation: shake 0.5s ease-in-out;
  }
`;

const SignIn = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showContactForm, setShowContactForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isInputFocused, setIsInputFocused] = useState({ email: false, password: false });
  const navigate = useNavigate();
  const isMobile = window.innerWidth <= 768;

  // Inject keyframes into document
  React.useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = keyframes;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  const handleEmailSignIn = async (e) => {
    e.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
      // Redirect to Home upon successful login
      navigate('/home');
    } catch (err) {
      setError(err.message);
      // Add a shake animation to the form
      const form = document.querySelector('.sign-in-form');
      form.classList.add('shake');
      setTimeout(() => form.classList.remove('shake'), 500);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
      // Redirect to Home upon successful login
      navigate('/home');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFocus = (field) => {
    setIsInputFocused(prev => ({ ...prev, [field]: true }));
  };

  const handleBlur = (field) => {
    setIsInputFocused(prev => ({ ...prev, [field]: false }));
  };

  return (
    <div style={styles.container}>
      {/* Style with CSS keyframes injected in useEffect */}
      
      <header style={isMobile ? {...styles.header, ...styles.responsive.header} : styles.header}>
        <motion.h1 
          style={styles.headerTitle}
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, type: "spring", stiffness: 100 }}
        >
          LEGAL RESEARCH ASSISTANT
        </motion.h1>
        
        <motion.div 
          style={styles.headerButtons}
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.8, type: "spring", stiffness: 100 }}
        >
          <button 
            style={styles.headerButton} 
            onClick={() => setShowContactForm(true)}
          >
            Contact Us
          </button>
          <button style={styles.headerButton}>Sign Up</button>
        </motion.div>
      </header>

      <main style={styles.mainContent}>
        <motion.div 
          style={styles.logoContainer}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <motion.div 
            style={isMobile ? {...styles.logoCircle, ...styles.responsive.logoCircle} : styles.logoCircle}
            whileHover={{ scale: 1.05, rotate: 5 }}
            animate={{ scale: [1, 1.03, 1], transition: { duration: 3, repeat: Infinity } }}
          >
            <img src={logo} alt="Logo" style={styles.logoImage} />
          </motion.div>
        </motion.div>

        <motion.p 
          style={styles.subtitle}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.4 }}
        >
          JUSTICE SIMPLIFIED
        </motion.p>

        <motion.div 
          className="sign-in-form"
          style={isMobile ? {...styles.signInForm, ...styles.responsive.signInForm} : styles.signInForm}
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          whileHover={{ 
            y: -5, 
            boxShadow: '0 15px 35px rgba(0, 0, 0, 0.1)'
          }}
        >
          <motion.h2 style={styles.formTitle} variants={itemVariants}>Sign In</motion.h2>
          
          {error && (
            <motion.p 
              style={styles.errorMessage}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {error}
            </motion.p>
          )}

          <motion.form onSubmit={handleEmailSignIn} variants={containerVariants}>
            <motion.div style={styles.inputGroup} variants={itemVariants}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => handleFocus('email')}
                onBlur={() => handleBlur('email')}
                required
                style={isInputFocused.email ? 
                  {...styles.input, ...styles.inputFocus} : 
                  styles.input
                }
              />
            </motion.div>

            <motion.div style={styles.inputGroup} variants={itemVariants}>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => handleFocus('password')}
                onBlur={() => handleBlur('password')}
                required
                style={isInputFocused.password ? 
                  {...styles.input, ...styles.inputFocus} : 
                  styles.input
                }
              />
              <button 
                type="button" 
                onClick={() => setShowPassword(!showPassword)}
                style={styles.visibilityButton}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </button>
            </motion.div>

            <motion.button 
              type="submit" 
              style={styles.signInButton}
              variants={itemVariants}
              whileHover={{ 
                scale: 1.03, 
                backgroundColor: '#3a5fc8',
                y: -3,
                boxShadow: '0 7px 14px rgba(0, 0, 0, 0.15)'
              }}
              whileTap={{ scale: 0.98 }}
            >
              Sign In
            </motion.button>
          </motion.form>

          <motion.div style={styles.socialSignIn} variants={containerVariants}>
            <motion.p style={styles.socialText} variants={itemVariants}>Sign in with</motion.p>
            <motion.div style={styles.socialButtons} variants={containerVariants}>
              <motion.button 
                style={{...styles.socialButton, ...styles.googleButton}}
                onClick={handleGoogleSignIn}
                variants={itemVariants}
                whileHover={{ 
                  scale: 1.05, 
                  y: -3,
                  boxShadow: '0 7px 14px rgba(0, 0, 0, 0.1)',
                  backgroundColor: 'rgba(219, 68, 55, 0.05)',
                  borderColor: 'rgba(219, 68, 55, 0.3)'
                }}
                whileTap={{ scale: 0.98 }}
              >
                <FaGoogle style={styles.icon} />
                <span>Google</span>
              </motion.button>
              <motion.button 
                style={{...styles.socialButton, ...styles.microsoftButton}}
                variants={itemVariants}
                whileHover={{ 
                  scale: 1.05,
                  y: -3,
                  boxShadow: '0 7px 14px rgba(0, 0, 0, 0.1)',
                  backgroundColor: 'rgba(0, 164, 239, 0.05)',
                  borderColor: 'rgba(0, 164, 239, 0.3)'
                }}
                whileTap={{ scale: 0.98 }}
              >
                <FaMicrosoft style={styles.icon} />
                <span>Microsoft</span>
              </motion.button>
            </motion.div>
          </motion.div>

          <motion.button 
            onClick={() => {/* Handle the forgot password action here */}} 
            style={styles.forgotPassword}
            variants={itemVariants}
            whileHover={{ 
              scale: 1.05,
              color: '#3a5fc8',
              textDecoration: 'underline'
            }}
          >
            Forgot password?
          </motion.button>
        </motion.div>
      </main>

      <motion.footer
        style={styles.footer}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1 }}
      >
        <p>🔒 Secure & Confidential</p>
        <p>© {new Date().getFullYear()} Legal Research Assistant. All rights reserved.</p>
      </motion.footer>

      {showContactForm && (
        <motion.div 
          style={styles.modal}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div 
            style={styles.modalContent}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          >
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>Contact Us</h2>
              <button 
                onClick={() => setShowContactForm(false)} 
                style={styles.closeButton}
                onMouseOver={(e) => {
                  e.currentTarget.style.color = '#4a6fdc';
                  e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
                  e.currentTarget.style.transform = 'rotate(90deg)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.color = '#666';
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.transform = 'rotate(0deg)';
                }}
              >
                ×
              </button>
            </div>
            <div style={styles.modalBody}>
              <iframe
                src="https://forms.gle/iHUy593GKuAa98K78"
                width="100%"
                height="500"
                frameBorder="0"
                marginHeight="0"
                marginWidth="0"
                title="Contact Form"
              >
                Loading form...
              </iframe>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default SignIn;
