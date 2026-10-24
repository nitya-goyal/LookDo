import React from 'react';
import { Eye, Sparkles } from 'lucide-react';

export default function Header({ providerInfo }) {
  const isOnline = providerInfo?.online ?? true;
  const isGemini = providerInfo?.provider === 'gemini';
  const label = providerInfo?.display || (isOnline ? 'Mock AI Active' : 'Connecting...');

  return (
    <header className="app-header" role="banner">
      <div className="brand-section">
        <div className="brand-logo" aria-hidden="true">
          <Eye size={24} />
        </div>
        <div className="brand-text">
          <h1>LookDo</h1>
          <p className="brand-tagline">
            Multimodal UI Navigation & Element Locator
          </p>
        </div>
      </div>

      <div className="header-status">
        <div 
          className="status-badge" 
          role="status" 
          aria-label="System status"
          style={isGemini ? { background: 'rgba(56, 189, 248, 0.15)', borderColor: 'rgba(56, 189, 248, 0.35)', color: 'var(--accent-cyan)' } : {}}
        >
          <span 
            className="status-dot" 
            aria-hidden="true"
            style={isGemini ? { background: 'var(--accent-cyan)', boxShadow: '0 0 8px var(--accent-cyan)' } : {}}
          />
          <span>{label}</span>
        </div>
      </div>
    </header>
  );
}
