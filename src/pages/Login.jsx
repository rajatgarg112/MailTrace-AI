import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, ArrowRight, CheckCircle2, Server, Eye, EyeOff } from 'lucide-react';
import './Login.css';

export const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('alex.dev@mailtrace.local');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      navigate('/inbox');
    }, 600);
  };

  return (
    <div className="login-page-container">
      <div className="login-backdrop-glow"></div>
      
      <div className="login-card-grid">
        {/* Left Side: Brand & Gateway Capabilities */}
        <div className="login-brand-panel">
          <div className="login-logo-header">
            <div className="brand-logo-icon">
              <Shield size={28} />
            </div>
            <div className="brand-logo-text">
              <h2>MailTrace <span>AI</span></h2>
              <p>Pre-Delivery Security Gateway</p>
            </div>
          </div>

          <div className="login-hero-tagline">
            <h1>Autonomous Email Security Before Delivery</h1>
            <p>
              Protect enterprise mailboxes with real-time heuristic NLP, zero-day attachment sandboxing, and autonomous quarantine decisions.
            </p>
          </div>

          <div className="login-features-list">
            <div className="feature-item">
              <CheckCircle2 className="feature-icon text-cyan" size={18} />
              <div>
                <h4>Zero-Trust Intercept Barrier</h4>
                <p>Emails scanned and classified prior to inbox landing.</p>
              </div>
            </div>

            <div className="feature-item">
              <Server className="feature-icon text-emerald" size={18} />
              <div>
                <h4>Standalone MTA Architecture</h4>
                <p>Independent mail gateway requiring no external APIs.</p>
              </div>
            </div>

            <div className="feature-item">
              <Lock className="feature-icon text-purple" size={18} />
              <div>
                <h4>Active Quarantine Enforcement</h4>
                <p>Isolate phishing and credential harvesting threats automatically.</p>
              </div>
            </div>
          </div>

          <div className="login-footer-note">
            <span>SIH 2026 Evaluation Prototype • v1.0.0 Foundation</span>
          </div>
        </div>

        {/* Right Side: Auth Form */}
        <div className="login-form-panel">
          <div className="login-form-header">
            <h3>Gateway Sign In</h3>
            <p>Enter your MailTrace security credentials</p>
          </div>

          <form onSubmit={handleLogin} className="auth-form">
            <div className="auth-input-group">
              <label>SecOps Account Email</label>
              <div className="input-wrapper">
                <Mail className="field-icon" size={18} />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@mailtrace.local"
                  required
                />
              </div>
            </div>

            <div className="auth-input-group">
              <label>Password</label>
              <div className="input-wrapper">
                <Lock className="field-icon" size={18} />
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button 
                  type="button" 
                  className="btn-toggle-eye" 
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="auth-options">
              <label className="remember-me">
                <input type="checkbox" defaultChecked />
                <span>Remember MTA Session</span>
              </label>
              <span className="security-policy-link">SEC-2026 Policy</span>
            </div>

            <button type="submit" className="btn-login-submit" disabled={isLoading}>
              {isLoading ? (
                <span>Authenticating Gateway...</span>
              ) : (
                <>
                  <span>Access SecOps Gateway</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="demo-credentials-box">
            <div className="demo-badge">SIH Demo Credentials</div>
            <p>Logged in as: <strong>Alex Dev (SecOps Analyst)</strong></p>
            <button 
              type="button" 
              className="btn-quick-demo"
              onClick={() => navigate('/inbox')}
            >
              ⚡ Instant Demo Launch
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
