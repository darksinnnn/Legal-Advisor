import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaGoogle, FaEye, FaEyeSlash, FaBalanceScale, FaExclamationTriangle } from 'react-icons/fa';
import { auth, googleProvider, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup } from './firebase';
import './SignIn.css';

export default function SignIn() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.');
      return;
    }
    setError('');
    setIsLoading(true);

    try {
      if (isSignUp) {
        await createUserWithEmailAndPassword(auth, email.trim(), password);
      } else {
        await signInWithEmailAndPassword(auth, email.trim(), password);
      }
      navigate('/home');
    } catch (err) {
      let msg = err.message || 'Authentication failed.';
      if (msg.includes('auth/invalid-credential') || msg.includes('auth/wrong-password') || msg.includes('auth/user-not-found')) {
        msg = 'Invalid email or password. Please verify your credentials.';
      } else if (msg.includes('auth/email-already-in-use')) {
        msg = 'An account with this email already exists. Try signing in instead.';
      } else if (msg.includes('auth/weak-password')) {
        msg = 'Password should be at least 6 characters long.';
      }
      setError(msg);
    }
    setIsLoading(false);
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setIsLoading(true);
    try {
      await signInWithPopup(auth, googleProvider);
      navigate('/home');
    } catch (err) {
      setError(err.message || 'Google Sign-In failed.');
    }
    setIsLoading(false);
  };

  return (
    <div className="auth-container">
      <nav className="auth-nav">
        <div className="nav-brand">
          <div className="brand-crest">
            <FaBalanceScale />
          </div>
          <div className="brand-text">
            <span className="brand-title">Juris</span>
            <span className="brand-subtitle">Your Legal Research Assistant</span>
          </div>
        </div>
      </nav>

      <main className="auth-main">
        <motion.div
          className="auth-card"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="auth-header">
            <div className="auth-logo-crest">
              <FaBalanceScale />
            </div>
            <h1 className="auth-title">
              {isSignUp ? 'Create Legal Account' : 'Sign in to Juris'}
            </h1>
            <p className="auth-subtitle">
              {isSignUp
                ? 'Register for your legal research workspace powered by IPC statutory logic.'
                : 'Access your legal research workspace and statutory intelligence.'}
            </p>
          </div>

          {error && (
            <div className="auth-error-banner">
              <FaExclamationTriangle />
              <span>{error}</span>
            </div>
          )}

          {/* Google Sign In */}
          <button
            type="button"
            className="btn-google"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
          >
            <FaGoogle style={{ color: '#ea4335' }} />
            <span>Continue with Google</span>
          </button>

          <div className="auth-divider">
            <span>Or continue with email</span>
          </div>

          {/* Email / Password Form */}
          <form onSubmit={handleEmailAuth} className="auth-form">
            <div className="form-group">
              <label className="form-label" htmlFor="auth-email">Email Address</label>
              <input
                id="auth-email"
                type="email"
                className="form-input"
                placeholder="name@lawfirm.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="auth-password">Password</label>
              <div className="form-input-wrapper">
                <input
                  id="auth-password"
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="btn-toggle-eye"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn-submit-auth"
              disabled={isLoading}
            >
              {isLoading ? 'Authenticating...' : isSignUp ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <div className="auth-toggle-mode">
            <span>
              {isSignUp ? 'Already have an account?' : "Don't have an account yet?"}
            </span>
            <button
              type="button"
              className="btn-switch-mode"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError('');
              }}
            >
              {isSignUp ? 'Sign In' : 'Create One'}
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
