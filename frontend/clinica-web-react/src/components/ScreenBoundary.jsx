import { Component } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

class ScreenErrorBoundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidUpdate(previous) {
    if (this.state.failed && previous.resetKey !== this.props.resetKey) this.setState({ failed: false });
  }
  render() {
    if (!this.state.failed) return this.props.children;
    return <section role="alert" style={{ margin: 24, padding: 24, borderRadius: 16, background: '#fff7ed' }}>
      <p>{this.props.message}</p>
      <button type="button" onClick={() => window.location.reload()}>{this.props.retry}</button>
    </section>;
  }
}

export default function ScreenBoundary({ children }) {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  return <ScreenErrorBoundary resetKey={pathname} message={t('common.screenLoadError')} retry={t('common.reloadPage')}>
    {children}
  </ScreenErrorBoundary>;
}
