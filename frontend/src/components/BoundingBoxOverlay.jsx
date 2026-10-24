import React from 'react';

export default function BoundingBoxOverlay({ detection }) {
  if (!detection || !detection.bounding_box) return null;

  const { bounding_box: box, element_label, element_type, confidence } = detection;

  // Normalized [0, 1] to CSS percentage
  const top = `${box.top * 100}%`;
  const left = `${box.left * 100}%`;
  const width = `${(box.width ?? Math.max(0.01, box.right - box.left)) * 100}%`;
  const height = `${(box.height ?? Math.max(0.01, box.bottom - box.top)) * 100}%`;

  // Flip tag to bottom if element is at the very top edge of the image
  const flipTag = box.top < 0.08;

  return (
    <div className="bounding-overlay-layer" aria-hidden="true">
      <div
        className="highlight-box"
        style={{
          top,
          left,
          width,
          height,
        }}
      >
        {/* Pulsing Locator Beacon */}
        <div className="beacon-dot" />

        {/* Floating Label Badge */}
        <div className={`overlay-floating-tag ${flipTag ? 'tag-flip' : ''}`}>
          <span>{element_label}</span>
          {element_type && <span className="tag-badge">{element_type}</span>}
          {confidence && (
            <span className="tag-badge" style={{ color: 'var(--accent-emerald)' }}>
              {Math.round(confidence * 100)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
