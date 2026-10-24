import React from 'react';
import { Eye, Crosshair } from 'lucide-react';
import BoundingBoxOverlay from './BoundingBoxOverlay';

export default function ScreenshotViewer({ imageSrc, detection, imageName }) {
  return (
    <div className="viewer-panel">
      <div className="viewer-header">
        <h2 className="card-title" style={{ margin: 0 }}>
          <Eye size={20} className="text-cyan" />
          <span>Interface Inspection Canvas</span>
        </h2>
        {detection && (
          <div className="viewer-badge">
            <Crosshair size={14} color="var(--accent-cyan)" />
            <span>Target Element Identified</span>
          </div>
        )}
      </div>

      <div className="screenshot-viewport" id="screenshot-viewport">
        {!imageSrc ? (
          <div className="empty-state">
            <Eye className="empty-icon" />
            <h3>No Screenshot Loaded</h3>
            <p>Upload an image from your computer, paste from clipboard, or click a sample interface on the left.</p>
          </div>
        ) : (
          <div className="image-overlay-wrapper">
            <img
              src={imageSrc}
              alt={imageName || 'User uploaded interface screenshot'}
              className="screenshot-img"
              id="target-screenshot"
            />
            {detection && <BoundingBoxOverlay detection={detection} />}
          </div>
        )}
      </div>
    </div>
  );
}
