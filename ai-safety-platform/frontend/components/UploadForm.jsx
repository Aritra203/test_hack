import { useState } from 'react';

const modes = [
  { key: 'text', label: 'Analyze Text' },
  { key: 'image', label: 'Analyze Image' },
];

export default function UploadForm({
  onAnalyzeText,
  onAnalyzeImage,
  isLoading,
  error,
}) {
  const [mode, setMode] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [fileInput, setFileInput] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (mode === 'text') {
      const cleanText = textInput.trim();
      if (!cleanText) {
        return;
      }
      await onAnalyzeText(cleanText);
      return;
    }

    if (!fileInput) {
      return;
    }
    await onAnalyzeImage(fileInput);
  };

  return (
    <section className="glass-card rounded-2xl p-6 md:p-8">
      <div className="mb-5 flex flex-wrap gap-2">
        {modes.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setMode(item.key)}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
              mode === item.key
                ? 'bg-ink text-white shadow-panel'
                : 'bg-white/60 text-ink hover:bg-white'
            }`}
            disabled={isLoading}
          >
            {item.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {mode === 'text' ? (
          <div>
            <label className="mb-2 block text-sm font-semibold text-ink">Content to Analyze</label>
            <textarea
              value={textInput}
              onChange={(event) => setTextInput(event.target.value)}
              rows={6}
              placeholder="Paste suspicious message, chat, or social post..."
              className="w-full rounded-xl border border-slate-200 bg-white/80 px-4 py-3 text-sm text-slate-800 outline-none ring-0 transition placeholder:text-slate-400 focus:border-teal focus:shadow-panel"
              disabled={isLoading}
              required
            />
          </div>
        ) : (
          <div>
            <label className="mb-2 block text-sm font-semibold text-ink">Upload Image Evidence</label>
            <input
              type="file"
              accept="image/*"
              onChange={(event) => setFileInput(event.target.files?.[0] || null)}
              className="w-full rounded-xl border border-dashed border-slate-300 bg-white/80 px-4 py-3 text-sm text-slate-700 file:mr-3 file:rounded-lg file:border-0 file:bg-ink file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-slate-700"
              disabled={isLoading}
              required={mode === 'image'}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || (mode === 'text' ? !textInput.trim() : !fileInput)}
          className="inline-flex items-center justify-center rounded-xl bg-coral px-5 py-3 text-sm font-bold text-white transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoading ? 'Analyzing...' : 'Run Safety Analysis'}
        </button>
      </form>

      {error ? (
        <p className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
          {error}
        </p>
      ) : null}
    </section>
  );
}
