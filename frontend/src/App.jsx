import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import InstructionForm from './components/InstructionForm';
import ScreenshotViewer from './components/ScreenshotViewer';
import ExplanationCard from './components/ExplanationCard';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState('');
  const [instruction, setInstruction] = useState('where do I download this?');
  const [detection, setDetection] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [providerInfo, setProviderInfo] = useState({
    online: true,
    display: 'Connecting...',
    provider: 'mock',
  });

  // Check backend health and active AI provider on mount
  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        setProviderInfo({
          online: true,
          display: data.provider_display || 'Connected',
          provider: data.provider || 'mock',
        });
      })
      .catch(() => {
        fetch('http://127.0.0.1:8000/health')
          .then((res) => res.json())
          .then((data) => {
            setProviderInfo({
              online: true,
              display: data.provider_display || 'Connected',
              provider: data.provider || 'mock',
            });
          })
          .catch(() => {
            setProviderInfo({
              online: false,
              display: 'Backend Offline',
              provider: 'none',
            });
          });
      });
  }, []);

  // Handle global paste event for screenshot (Ctrl + V)
  useEffect(() => {
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            handleFileSelect(file);
            break;
          }
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    setDetection(null);

    // Create object URL for preview
    if (imagePreviewUrl && imagePreviewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(imagePreviewUrl);
    }
    const url = URL.createObjectURL(file);
    setImagePreviewUrl(url);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please upload or select a screenshot first.');
      return;
    }
    if (!instruction.trim()) {
      setError('Please enter a natural-language instruction.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('instruction', instruction.trim());

      // Attempt endpoint via proxy, fallback to direct port 8000 if needed
      let res;
      try {
        res = await fetch('/api/locate', {
          method: 'POST',
          body: formData,
        });
      } catch (networkErr) {
        // Fallback direct request
        res = await fetch('http://127.0.0.1:8000/api/locate', {
          method: 'POST',
          body: formData,
        });
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server responded with error status ${res.status}`);
      }

      const data = await res.json();
      setDetection(data);
    } catch (err) {
      console.error('Locate API Error:', err);
      setError(err.message || 'Failed to analyze interface. Please check backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header providerInfo={providerInfo} />

      <main className="main-layout">
        <InstructionForm
          selectedFile={selectedFile}
          onFileSelect={handleFileSelect}
          instruction={instruction}
          onInstructionChange={setInstruction}
          onSubmit={handleSubmit}
          isLoading={isLoading}
          error={error}
        />

        <div className="viewer-panel">
          <ScreenshotViewer
            imageSrc={imagePreviewUrl}
            detection={detection}
            imageName={selectedFile?.name}
          />

          {detection && <ExplanationCard detection={detection} />}
        </div>
      </main>

      <footer className="app-footer">
        <p>LookDo • Multimodal UI Navigation Assistant • Hackathon MVP</p>
      </footer>
    </div>
  );
}
