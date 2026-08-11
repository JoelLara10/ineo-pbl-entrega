import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { FiUser, FiLock, FiEye, FiEyeOff, FiArrowRight } from 'react-icons/fi';
import { MdLocalHospital } from 'react-icons/md';
import './LoginScreen.css';

const LoginScreen = () => {
  const { t, i18n } = useTranslation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const { login } = useAuth();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('@ineo_lang', lng);
  };

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      setErrorMsg(t('login.errorEmptyFields'));
      return;
    }
    setLoading(true);
    setErrorMsg('');
    const result = await login(username, password);
    setLoading(false);
    if (!result.success) setErrorMsg(result.error || t('login.errorCredentials'));
  };

  const currentLang = i18n.language;

  return (
    <div className="login-container">
      {/* Language Switcher */}
      <div className="lang-switcher">
        <button
          className={`lang-btn ${currentLang === 'es' ? 'lang-btn-active' : ''}`}
          onClick={() => changeLanguage('es')}
          type="button"
        >
          ES
        </button>
        <button
          className={`lang-btn ${currentLang === 'en' ? 'lang-btn-active' : ''}`}
          onClick={() => changeLanguage('en')}
          type="button"
        >
          EN
        </button>
      </div>

      {/* Brand */}
      <div className="brand-container">
        <div className="icon-container">
          <MdLocalHospital size={70} color="#fff" />
        </div>
        <h1 className="brand-title">INEO</h1>
        <p className="brand-subtitle">{t('login.brandSubtitle')}</p>
      </div>

      {/* Form */}
      <div className="form-container">
        <div className="input-group">
          <FiUser size={22} color="#667eea" />
          <input
            className="input"
            placeholder={t('login.username')}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            autoComplete="username"
            disabled={loading}
          />
        </div>

        <div className="input-group">
          <FiLock size={22} color="#667eea" />
          <input
            className="input"
            placeholder={t('login.password')}
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            autoComplete="current-password"
            disabled={loading}
          />
          <button className="eye-btn" onClick={() => setShowPassword(!showPassword)} type="button">
            {showPassword ? <FiEyeOff size={22} color="#a0aec0" /> : <FiEye size={22} color="#a0aec0" />}
          </button>
        </div>

        {errorMsg && <p className="error-text">{errorMsg}</p>}

        <button className={`login-btn ${loading ? 'disabled' : ''}`} onClick={handleLogin} disabled={loading}>
          {loading ? (
            <span className="spinner" />
          ) : (
            <>
              <span>{t('login.loginButton')}</span>
              <FiArrowRight size={22} color="#fff" />
            </>
          )}
        </button>
      </div>

      <p className="footer-text">{t('login.footer')}</p>
    </div>
  );
};

export default LoginScreen;
