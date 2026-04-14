export default function LoadingSkeleton() {
  return (
    <div className="glass animate-pulse rounded-2xl p-6">
      <div className="h-6 w-44 rounded bg-slate-600/50" />
      <div className="mt-4 h-4 w-full rounded bg-slate-600/40" />
      <div className="mt-2 h-4 w-10/12 rounded bg-slate-600/40" />
      <div className="mt-2 h-4 w-8/12 rounded bg-slate-600/40" />
    </div>
  );
}

