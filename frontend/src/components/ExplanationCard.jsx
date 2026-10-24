import React from 'react';
import { CheckCircle2, MousePointerClick, Info, Compass } from 'lucide-react';

export default function ExplanationCard({ detection }) {
  if (!detection) return null;

  const {
    element_label,
    element_type,
    confidence,
    explanation,
    suggested_action,
    bounding_box,
  } = detection;

  const confidencePct = Math.round((confidence || 0) * 100);

  return (
    <section className="explanation-card" aria-labelledby="explanation-heading">
      <div className="explanation-header">
        <div className="explanation-title-group">
          <CheckCircle2 size={24} color="var(--accent-cyan)" />
          <h3 id="explanation-heading" className="element-label-name">
            {element_label}
          </h3>
          <span className="element-type-badge">{element_type}</span>
        </div>

        <div className="confidence-meter">
          <span>Confidence:</span>
          <span className="confidence-val">{confidencePct}%</span>
        </div>
      </div>

      <p className="explanation-body">{explanation}</p>

      {suggested_action && (
        <div className="action-box">
          <div className="action-icon-wrap" aria-hidden="true">
            <MousePointerClick size={18} />
          </div>
          <div className="action-content">
            <span className="action-label">Suggested Action</span>
            <span className="action-text">{suggested_action}</span>
          </div>
        </div>
      )}

      {bounding_box && (
        <div className="coordinates-inspector" title="Normalized coordinates (0 to 1)">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Compass size={14} />
            <span>Normalized Coordinates:</span>
          </div>
          <div className="coord-item">
            Top: <span>{bounding_box.top.toFixed(3)}</span>
          </div>
          <div className="coord-item">
            Left: <span>{bounding_box.left.toFixed(3)}</span>
          </div>
          <div className="coord-item">
            Bottom: <span>{bounding_box.bottom.toFixed(3)}</span>
          </div>
          <div className="coord-item">
            Right: <span>{bounding_box.right.toFixed(3)}</span>
          </div>
        </div>
      )}
    </section>
  );
}
