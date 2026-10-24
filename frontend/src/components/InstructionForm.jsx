import React, { useRef, useState } from 'react';
import { UploadCloud, Sparkles, Image as ImageIcon, CornerDownLeft } from 'lucide-react';
import { createSampleImageBlob } from '../utils/samples';

const QUICK_PROMPTS = [
  'Open settings',
  'Where do I download this?',
  'click the second blue button',
  'how do I change my password?',
  'I mean that option on the right',
];

export default function InstructionForm({
  selectedFile,
  onFileSelect,
  instruction,
  onInstructionChange,
  onSubmit,
  isLoading,
  error,
}) {
  const fileInputRef = useRef(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  const handleLoadSample = async (type, defaultPrompt) => {
    const file = await createSampleImageBlob(type);
    onFileSelect(file);
    if (defaultPrompt) {
      onInstructionChange(defaultPrompt);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isLoading && selectedFile && instruction.trim()) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="control-panel">
      {/* Upload Card */}
      <div className="card">
        <h2 className="card-title">
          <UploadCloud size={20} className="text-cyan" />
          <span>1. Upload Screenshot</span>
        </h2>

        <div
          className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          role="button"
          tabIndex={0}
          aria-label="Upload interface screenshot file or drop image here"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              fileInputRef.current?.click();
            }
          }}
        >
          <input
            type="file"
            ref={fileInputRef}
            className="file-input"
            accept="image/png, image/jpeg, image/webp"
            onChange={handleFileInputChange}
          />
          <UploadCloud className="dropzone-icon" />
          <p className="dropzone-text">
            {selectedFile ? (
              <strong style={{ color: 'var(--accent-cyan)' }}>{selectedFile.name}</strong>
            ) : (
              'Click to browse or drop screenshot here'
            )}
          </p>
          <p className="dropzone-hint">Supports PNG, JPG, WebP • Or paste with Ctrl+V</p>
        </div>

        {/* Quick Sample Buttons */}
        <div className="samples-container">
          <span className="samples-label">Or try a sample interface:</span>
          <div className="sample-buttons-grid">
            <button
              type="button"
              className="btn-sample"
              onClick={() => handleLoadSample('software-portal', 'Open settings')}
            >
              <ImageIcon size={14} />
              <span>Software Portal</span>
            </button>
            <button
              type="button"
              className="btn-sample"
              onClick={() => handleLoadSample('account-settings', 'how do I change my password?')}
            >
              <ImageIcon size={14} />
              <span>Settings Console</span>
            </button>
          </div>
        </div>
      </div>

      {/* Instruction Card */}
      <div className="card">
        <h2 className="card-title">
          <Sparkles size={20} className="text-cyan" />
          <span>2. What would you like to do?</span>
        </h2>

        <div className="instruction-section">
          <div className="instruction-input-wrap">
            <input
              type="text"
              id="instruction-input"
              className="instruction-input"
              value={instruction}
              onChange={(e) => onInstructionChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. open settings, click the blue button..."
              aria-label="Natural language instruction for UI element"
              autoComplete="off"
            />
          </div>

          <span className="quick-prompts-label">Quick suggestions:</span>
          <div className="quick-prompts-list" role="list">
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                className="prompt-chip"
                onClick={() => onInstructionChange(prompt)}
              >
                "{prompt}"
              </button>
            ))}
          </div>

          {error && (
            <div className="error-alert" role="alert">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <button
            type="button"
            className="btn-primary"
            onClick={onSubmit}
            disabled={!selectedFile || !instruction.trim() || isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <div className="spinner" aria-hidden="true" />
                <span>Analyzing Interface...</span>
              </>
            ) : (
              <>
                <Sparkles size={18} />
                <span>Locate Element</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
