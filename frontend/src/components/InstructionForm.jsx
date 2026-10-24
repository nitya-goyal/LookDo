import React, { useEffect, useRef, useState } from 'react';
import { UploadCloud, Sparkles, Image as ImageIcon, Mic } from 'lucide-react';
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
  mode,
  onModeChange,
  onSubmit,
  isLoading,
  error,
}) {
  const fileInputRef = useRef(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const [voiceMessage, setVoiceMessage] = useState('');
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  useEffect(() => () => {
    const recognition = recognitionRef.current;
    if (recognition) {
      recognition.onstart = recognition.onresult = recognition.onerror = recognition.onend = null;
      recognition.abort();
    }
  }, []);

  const handleVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }
    if (!SpeechRecognition) return;

    let receivedText = false;
    let failed = false;
    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.lang = 'en-US';
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.onstart = () => setVoiceMessage('Listening...');
      recognition.onresult = (event) => {
        const transcript = event.results[0]?.[0]?.transcript?.trim();
        if (transcript) {
          receivedText = true;
          onInstructionChange(transcript);
          setVoiceMessage('Voice captured. Click Locate Element when ready.');
        }
      };
      recognition.onerror = (event) => {
        failed = true;
        setIsListening(false);
        const messages = {
          'not-allowed': 'Microphone permission denied. Allow microphone access or type your instruction.',
          'service-not-allowed': 'Speech recognition is blocked by this browser. Please type your instruction.',
          'audio-capture': 'Microphone unavailable. Please type your instruction.',
          'no-speech': 'No speech detected. Try again or type your instruction.',
          network: 'Speech recognition connection failed. Try again or type your instruction.',
          aborted: 'Listening stopped. You can type or try again.',
        };
        setVoiceMessage(messages[event.error] || 'Speech recognition failed. Try again or type your instruction.');
      };
      recognition.onend = () => {
        recognitionRef.current = null;
        setIsListening(false);
        if (!receivedText && !failed) setVoiceMessage('Listening ended. Try again or type your instruction.');
      };
      setIsListening(true);
      setVoiceMessage('Listening...');
      // Starting from this click lets the browser request microphone permission.
      recognition.start();
    } catch {
      recognitionRef.current = null;
      setIsListening(false);
      setVoiceMessage('Unable to start speech recognition. Please type your instruction.');
    }
  };

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
    onFileSelect(file, type);
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
          <div className="sample-buttons-grid" role="group" aria-label="Navigation mode">
            <button type="button" className="btn-sample" aria-pressed={mode === 'locate'} disabled={isLoading} onClick={() => onModeChange('locate')}>Locate Element</button>
            <button type="button" className="btn-sample" aria-pressed={mode === 'guide'} disabled={isLoading} onClick={() => onModeChange('guide')}>Guide Me</button>
          </div>
          {mode === 'guide' && <span className="dropzone-hint">Describe a task. LookDo highlights only the next visible action.</span>}
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
            <button
              type="button"
              className="btn-sample voice-button"
              onClick={handleVoiceInput}
              disabled={!SpeechRecognition || isLoading}
              aria-label={isListening ? 'Stop listening' : 'Speak your instruction'}
              aria-pressed={isListening}
              title={SpeechRecognition ? 'Speak your instruction' : 'Speech recognition unavailable in this browser; type your instruction'}
            >
              <Mic size={18} aria-hidden="true" />
              {isListening && <span>Listening...</span>}
            </button>
          </div>
          {voiceMessage && <span className="dropzone-hint" role="status">{voiceMessage}</span>}

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
                <span>{mode === 'guide' ? 'Guide Me' : 'Locate Element'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
