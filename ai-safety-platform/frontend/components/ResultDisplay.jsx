function scoreColor(score) {
  if (score > 0.8) {
    return 'text-rose-700 bg-rose-100 border-rose-200';
  }
  if (score > 0.5) {
    return 'text-amber-700 bg-amber-100 border-amber-200';
  }
  return 'text-emerald-700 bg-emerald-100 border-emerald-200';
}

export default function ResultDisplay({ result }) {
  if (!result) {
    return null;
  }

  return (
    <section className="glass-card rounded-2xl p-6 md:p-8">
      <h2 className="mb-4 text-xl font-bold text-ink">Analysis Result</h2>

      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white/70 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Toxicity Score</p>
          <p className="mt-1 text-2xl font-extrabold text-slate-900">{result.toxicity_score.toFixed(4)}</p>
        </div>

        <div className={`rounded-xl border p-4 ${scoreColor(result.toxicity_score)}`}>
          <p className="text-xs font-semibold uppercase tracking-wide">Risk Label</p>
          <p className="mt-1 text-2xl font-extrabold">{result.risk_label}</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white/70 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Reference ID</p>
          <p className="mt-1 break-all text-sm font-semibold text-slate-800">
            {result.evidence_id || result.analysis_id}
          </p>
        </div>
      </div>

      {result.extracted_text ? (
        <div className="mt-5 rounded-xl border border-slate-200 bg-white/80 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Extracted Text (OCR)</p>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-800">{result.extracted_text}</p>
        </div>
      ) : null}

      {result.cloudinary_url ? (
        <div className="mt-5 rounded-xl border border-slate-200 bg-white/80 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Cloud Evidence URL</p>
          <a
            href={result.cloudinary_url}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-block break-all text-sm font-semibold text-teal hover:underline"
          >
            {result.cloudinary_url}
          </a>
          <p className="mt-2 break-all text-xs text-slate-500">
            Public ID: {result.cloudinary_public_id}
          </p>
        </div>
      ) : null}
    </section>
  );
}
