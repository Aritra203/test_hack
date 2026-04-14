import { useState } from 'react';

import FIRGenerator from '../components/FIRGenerator';
import ResultDisplay from '../components/ResultDisplay';
import UploadForm from '../components/UploadForm';
import {
  analyzeImage,
  analyzeText,
  downloadFIR,
  generateFIR,
} from '../services/api';

function toErrorMessage(error) {
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (typeof error?.message === 'string') {
    return error.message;
  }
  return 'Unexpected error occurred. Please try again.';
}

export default function HomePage() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [firResult, setFirResult] = useState(null);

  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [firLoading, setFirLoading] = useState(false);

  const [analysisError, setAnalysisError] = useState('');
  const [firError, setFirError] = useState('');

  const handleAnalyzeText = async (text) => {
    setAnalysisLoading(true);
    setAnalysisError('');
    setFirResult(null);

    try {
      const response = await analyzeText(text);
      setAnalysisResult(response);
    } catch (error) {
      setAnalysisError(toErrorMessage(error));
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleAnalyzeImage = async (file) => {
    setAnalysisLoading(true);
    setAnalysisError('');
    setFirResult(null);

    try {
      const response = await analyzeImage(file);
      setAnalysisResult(response);
    } catch (error) {
      setAnalysisError(toErrorMessage(error));
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleGenerateFIR = async (payload) => {
    setFirLoading(true);
    setFirError('');

    try {
      const response = await generateFIR(payload);
      setFirResult(response);
    } catch (error) {
      setFirError(toErrorMessage(error));
    } finally {
      setFirLoading(false);
    }
  };

  const handleDownloadFIR = async (firId, filename) => {
    setFirError('');

    try {
      const response = await downloadFIR(firId);
      const fileBlob = new Blob([response.data], { type: 'application/pdf' });
      const fileUrl = URL.createObjectURL(fileBlob);

      const anchor = document.createElement('a');
      anchor.href = fileUrl;
      anchor.download = filename || 'fir_report.pdf';
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      URL.revokeObjectURL(fileUrl);
    } catch (error) {
      setFirError(toErrorMessage(error));
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-8 md:px-8 md:py-12">
      <div className="bg-orb-coral" aria-hidden="true" />
      <div className="bg-orb-teal" aria-hidden="true" />

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header className="glass-card rounded-2xl p-6 md:p-8">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">AI Safety & Smart FIR Platform</p>
          <h1 className="mt-3 text-3xl font-black leading-tight text-ink md:text-4xl">
            Detect Toxic Content, Protect Victims, and Generate FIRs Instantly
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-700 md:text-base">
            This platform analyzes harmful text and image content, assigns risk levels, and prepares structured cyber-crime FIR PDFs using cloud-hosted evidence links.
          </p>
        </header>

        <UploadForm
          onAnalyzeText={handleAnalyzeText}
          onAnalyzeImage={handleAnalyzeImage}
          isLoading={analysisLoading}
          error={analysisError}
        />

        <ResultDisplay result={analysisResult} />

        <FIRGenerator
          analysisResult={analysisResult}
          onGenerate={handleGenerateFIR}
          onDownload={handleDownloadFIR}
          isGenerating={firLoading}
          firResult={firResult}
          error={firError}
        />
      </div>
    </main>
  );
}
