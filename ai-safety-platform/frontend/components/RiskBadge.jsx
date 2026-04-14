export default function RiskBadge({ risk = "LOW" }) {
  const tone =
    risk === "CRITICAL"
      ? "bg-red-500/20 text-red-300 border-red-400/40"
      : risk === "HIGH"
        ? "bg-orange-500/20 text-orange-200 border-orange-400/40"
        : risk === "MEDIUM"
          ? "bg-amber-500/20 text-amber-200 border-amber-400/40"
          : "bg-emerald-500/20 text-emerald-200 border-emerald-400/40";

  return <span className={`rounded-full border px-3 py-1 text-xs font-semibold tracking-wide ${tone}`}>{risk}</span>;
}

