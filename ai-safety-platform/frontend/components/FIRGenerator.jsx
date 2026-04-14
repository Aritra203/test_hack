import { useEffect, useState } from 'react';

export default function FIRGenerator({
  analysisResult,
  onGenerate,
  onDownload,
  isGenerating,
  firResult,
  error,
}) {
  const [username, setUsername] = useState('');
  const [incidentDescription, setIncidentDescription] = useState('');
  const [evidenceNotes, setEvidenceNotes] = useState('');
  const [evidenceFile, setEvidenceFile] = useState(null);
  const [useAnalyzedEvidence, setUseAnalyzedEvidence] = useState(true);

  useEffect(() => {
    if (!analysisResult?.cloudinary_url) {
      setUseAnalyzedEvidence(false);
    }
  }, [analysisResult]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    await onGenerate({
      username,
      incidentDescription,
      evidenceNotes,
      evidenceFile,
      evidenceUrl: useAnalyzedEvidence ? analysisResult?.cloudinary_url : '',
      evidencePublicId: useAnalyzedEvidence ? analysisResult?.cloudinary_public_id : '',
    });
  };

  return (
    <section className="glass-card rounded-2xl p-6 md:p-8">
      <h2 className="mb-4 text-xl font-bold text-ink">Generate FIR</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-2 block text-sm font-semibold text-ink">Complainant Name</label>
          <input
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-white/80 px-4 py-3 text-sm outline-none transition focus:border-teal"
            placeholder="Enter full name"
            minLength={2}
            required
            disabled={isGenerating}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-ink">Incident Description</label>
          <textarea
            value={incidentDescription}
            onChange={(event) => setIncidentDescription(event.target.value)}
            rows={5}
            className="w-full rounded-xl border border-slate-200 bg-white/80 px-4 py-3 text-sm outline-none transition focus:border-teal"
            placeholder="Describe what happened, timeline, and affected platforms."
            minLength={10}
            required
            disabled={isGenerating}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-ink">Evidence Notes</label>
          <textarea
            value={evidenceNotes}
            onChange={(event) => setEvidenceNotes(event.target.value)}
            rows={3}
            className="w-full rounded-xl border border-slate-200 bg-white/80 px-4 py-3 text-sm outline-none transition focus:border-teal"
            placeholder="Add context such as account IDs, message timestamps, links, etc."
            disabled={isGenerating}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-ink">Additional Evidence File (Optional)</label>
          <input
            type="file"
            onChange={(event) => setEvidenceFile(event.target.files?.[0] || null)}
            className="w-full rounded-xl border border-dashed border-slate-300 bg-white/80 px-4 py-3 text-sm text-slate-700 file:mr-3 file:rounded-lg file:border-0 file:bg-ink file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-slate-700"
            disabled={isGenerating}
          />
        </div>

        {analysisResult?.cloudinary_url ? (
          <label className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white/80 p-3 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={useAnalyzedEvidence}
              onChange={(event) => setUseAnalyzedEvidence(event.target.checked)}
              className="mt-1 h-4 w-4 rounded border-slate-300 text-teal focus:ring-teal"
              disabled={isGenerating}
            />
            <span>
              Attach evidence from latest analysis in FIR
              <span className="mt-1 block break-all text-xs text-slate-500">
                {analysisResult.cloudinary_url}
              </span>
            </span>
          </label>
        ) : null}

        <button
          type="submit"
          className="inline-flex items-center justify-center rounded-xl bg-ink px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isGenerating || !username.trim() || !incidentDescription.trim()}
        >
          {isGenerating ? 'Generating FIR...' : 'Generate FIR PDF'}
        </button>
      </form>

      {error ? (
        <p className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
          {error}
        </p>
      ) : null}

      {firResult ? (
        <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <p className="text-sm font-semibold text-emerald-800">FIR generated successfully.</p>
          <p className="mt-1 text-xs text-emerald-700">FIR ID: {firResult.fir_id}</p>
          <button
            type="button"
            onClick={() => onDownload(firResult.fir_id, firResult.filename)}
            className="mt-3 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800"
          >
            Download FIR
          </button>
        </div>
      ) : null}
    </section>
  );
}
