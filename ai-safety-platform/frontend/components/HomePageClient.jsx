"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import toast, { Toaster } from "react-hot-toast";

import LoadingSkeleton from "./LoadingSkeleton";
import RiskBadge from "./RiskBadge";
import { fadeUp, stagger } from "../animations/motion";
import { analyzeImage, analyzeText, downloadFir, generateFir, getAnalytics, getFirJob } from "../services/api";

const testimonials = [
  { quote: "We reduced response time by 60% for abuse reports.", name: "TrustOps Lead, EduTech" },
  { quote: "Legal-ready FIR drafts made escalation far faster.", name: "Cyber Cell Liaison" },
  { quote: "Our safety team got explainable AI, not black-box output.", name: "Child Safety NGO" },
];

const steps = [
  { title: "Ingest", text: "Collect text, image evidence, and conversation context from reports." },
  { title: "Analyze", text: "Hybrid AI detects toxicity, grooming patterns, and escalation severity." },
  { title: "Act", text: "Generate legal mappings and downloadable FIR draft for escalation." },
];

function parseError(error) {
  return error?.response?.data?.detail || error?.message || "Something went wrong.";
}

export default function HomePageClient() {
  const [darkMode, setDarkMode] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [text, setText] = useState("");
  const [contextInput, setContextInput] = useState("");
  const [languageHint, setLanguageHint] = useState("");
  const [subjectIsMinor, setSubjectIsMinor] = useState(true);
  const [imageFile, setImageFile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [firLoading, setFirLoading] = useState(false);
  const [firState, setFirState] = useState({ jobId: "", status: "", firId: "", filename: "" });

  const parsedMessages = useMemo(
    () =>
      contextInput
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line, idx) => ({ sender: idx % 2 === 0 ? "user" : "other", message: line })),
    [contextInput]
  );

  async function runTextAnalysis() {
    if (!text.trim()) {
      toast.error("Enter text before analysis.");
      return;
    }
    setLoading(true);
    try {
      const data = await analyzeText({
        text,
        previous_messages: parsedMessages,
        language_hint: languageHint || null,
        subject_is_minor: subjectIsMinor,
      });
      setAnalysis(data);
      toast.success("Text analyzed successfully.");
    } catch (error) {
      toast.error(parseError(error));
    } finally {
      setLoading(false);
    }
  }

  async function runImageAnalysis() {
    if (!imageFile) {
      toast.error("Upload an image first.");
      return;
    }
    setLoading(true);
    try {
      const data = await analyzeImage(imageFile, subjectIsMinor, languageHint);
      setAnalysis(data);
      toast.success("Image analyzed successfully.");
    } catch (error) {
      toast.error(parseError(error));
    } finally {
      setLoading(false);
    }
  }

  async function refreshAnalytics() {
    try {
      const data = await getAnalytics();
      setAnalytics(data);
    } catch {
      setAnalytics(null);
    }
  }

  async function startFirFlow() {
    if (!analysis?.result) {
      toast.error("Run analysis first.");
      return;
    }
    setFirLoading(true);
    try {
      const response = await generateFir({
        complainant_name: "Citizen Reporter",
        complainant_contact: "+91-9000000000",
        incident_description: analysis.analyzed_text || analysis.extracted_text || text,
        location: "India",
        incident_datetime: new Date().toISOString(),
        accused_details: "Unknown social account",
        additional_notes: "Generated via AI Safety dashboard.",
        previous_messages: parsedMessages,
        language_hint: languageHint || null,
        subject_is_minor: subjectIsMinor,
        evidence_urls: analysis.cloudinary_url ? [analysis.cloudinary_url] : [],
      });

      if (response.status === "completed") {
        setFirState({ jobId: response.job_id, status: "completed", firId: response.fir_id, filename: response.filename });
        toast.success("FIR generated instantly.");
      } else {
        setFirState({ jobId: response.job_id, status: response.status, firId: "", filename: "" });
        toast.success("FIR generation queued.");
      }
    } catch (error) {
      toast.error(parseError(error));
    } finally {
      setFirLoading(false);
    }
  }

  async function checkFirJob() {
    if (!firState.jobId) {
      toast.error("No FIR job found.");
      return;
    }
    try {
      const job = await getFirJob(firState.jobId);
      setFirState((prev) => ({
        ...prev,
        status: job.status,
        firId: job.fir_id || "",
        filename: job.filename || "",
      }));
      if (job.status === "completed") toast.success("FIR is ready to download.");
      if (job.status === "failed") toast.error(job.error || "FIR generation failed.");
    } catch (error) {
      toast.error(parseError(error));
    }
  }

  async function handleDownloadFir() {
    if (!firState.firId) {
      toast.error("FIR ID missing.");
      return;
    }
    try {
      const response = await downloadFir(firState.firId);
      const blob = new Blob([response.data], { type: "application/pdf" });
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href;
      a.download = firState.filename || "fir_report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(href);
      toast.success("FIR downloaded.");
    } catch (error) {
      toast.error(parseError(error));
    }
  }

  return (
    <main className={`soft-scroll ${darkMode ? "dark" : ""}`}>
      <Toaster position="top-right" />

      <section className="mx-auto max-w-6xl px-5 pb-20 pt-12">
        <motion.div variants={fadeUp} initial="hidden" animate="show" className="glass rounded-3xl p-8 shadow-glow md:p-12">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-200">AI Safety & Smart FIR</p>
            <button
              onClick={() => setDarkMode((v) => !v)}
              className="rounded-full border border-slate-500/50 px-4 py-1 text-xs font-semibold text-slate-100 hover:border-slate-300"
            >
              {darkMode ? "Dark" : "Light"}
            </button>
          </div>
          <h1 className="mt-4 text-4xl font-extrabold leading-tight md:text-6xl">
            Detect abuse, protect children, and generate <span className="gradient-text">legal FIRs</span> with explainable AI.
          </h1>
          <p className="mt-6 max-w-3xl text-slate-300">
            Enterprise-grade trust & safety platform for cyberbullying, threat escalation, hate speech, grooming signals, and multilingual toxic context.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="#dashboard" className="rounded-xl bg-brand-500 px-5 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-brand-400">
              Launch Live Demo
            </a>
            <button
              onClick={refreshAnalytics}
              className="rounded-xl border border-slate-500/50 bg-slate-900/40 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:-translate-y-0.5 hover:border-slate-300"
            >
              Load Analytics
            </button>
          </div>
        </motion.div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-5 px-5 md:grid-cols-3">
        {["Multimodal Detection", "Explainable AI", "Legal Intelligence"].map((title) => (
          <div key={title} className="glass rounded-2xl p-6 transition hover:-translate-y-1">
            <h3 className="text-lg font-bold">{title}</h3>
            <p className="mt-2 text-sm text-slate-300">Production-focused architecture with cloud evidence, contextual analysis, and compliance-ready outputs.</p>
          </div>
        ))}
      </section>

      <section className="mx-auto mt-20 max-w-6xl px-5">
        <h2 className="text-2xl font-bold md:text-3xl">How It Works</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {steps.map((step, idx) => (
            <motion.div key={step.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: idx * 0.08 }} className="glass rounded-2xl p-5">
              <p className="text-xs text-sky-300">Step {idx + 1}</p>
              <h3 className="mt-2 text-lg font-bold">{step.title}</h3>
              <p className="mt-2 text-sm text-slate-300">{step.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-20 max-w-6xl px-5">
        <div className="glass rounded-3xl p-6">
          <h2 className="text-2xl font-bold md:text-3xl">AI Demo Preview</h2>
          <p className="mt-2 text-sm text-slate-300">Live risk engine with explainability, legal section mapping, and FIR pipeline.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-4">
            {["Cyberbullying", "Threat", "Hate Speech", "Sexual Harassment"].map((t) => (
              <div key={t} className="rounded-xl border border-slate-700 bg-slate-900/50 px-3 py-2 text-xs text-slate-200">{t}</div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto mt-20 max-w-6xl px-5" id="dashboard">
        <motion.div variants={stagger} initial="hidden" whileInView="show" viewport={{ once: true }} className="space-y-6">
          <motion.div variants={fadeUp} className="glass rounded-3xl p-7">
            <h2 className="text-2xl font-bold md:text-3xl">AI Safety Dashboard</h2>
            <p className="mt-2 text-slate-300">Analyze text/image evidence, review risk and legal sections, and generate FIR in one flow.</p>
          </motion.div>

          <motion.div variants={fadeUp} className="grid gap-5 lg:grid-cols-2">
            <div className="glass rounded-2xl p-6">
              <label className="mb-2 block text-sm text-slate-300">Suspicious text</label>
              <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6} className="w-full rounded-xl border border-slate-600 bg-slate-900/60 p-3 text-sm outline-none focus:border-brand-400" placeholder="Paste chat, post, or message..." />
              <label className="mb-2 mt-4 block text-sm text-slate-300">Previous conversation context (one line per message)</label>
              <textarea value={contextInput} onChange={(e) => setContextInput(e.target.value)} rows={5} className="w-full rounded-xl border border-slate-600 bg-slate-900/60 p-3 text-sm outline-none focus:border-brand-400" placeholder={"Message 1\nMessage 2\nMessage 3"} />
              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <input value={languageHint} onChange={(e) => setLanguageHint(e.target.value)} className="rounded-xl border border-slate-600 bg-slate-900/60 px-3 py-2 text-sm outline-none focus:border-brand-400" placeholder="Language hint (optional)" />
                <label className="flex items-center gap-2 rounded-xl border border-slate-600 bg-slate-900/60 px-3 py-2 text-sm">
                  <input type="checkbox" checked={subjectIsMinor} onChange={(e) => setSubjectIsMinor(e.target.checked)} />
                  Subject is minor
                </label>
              </div>
              <div className="mt-4 flex flex-wrap gap-3">
                <button onClick={runTextAnalysis} className="rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold hover:bg-brand-400">Analyze Text</button>
                <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files?.[0] || null)} className="text-xs" />
                <button onClick={runImageAnalysis} className="rounded-xl border border-slate-500 px-4 py-2 text-sm font-semibold hover:border-slate-300">Analyze Image</button>
              </div>
            </div>

            <div className="glass rounded-2xl p-6">
              {loading ? (
                <LoadingSkeleton />
              ) : analysis?.result ? (
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold">Analysis Result</h3>
                    <RiskBadge risk={analysis.result.risk_level} />
                  </div>
                  <p className="mt-3 text-sm text-slate-300">Toxicity Score: {analysis.result.toxicity_score}</p>
                  <p className="text-sm text-slate-300">Language: {analysis.result.detected_language}</p>
                  <p className="text-sm text-slate-300">Escalation: {analysis.result.escalation_detected ? "Yes" : "No"}</p>
                  <div className="mt-4 rounded-xl border border-slate-700 p-3">
                    <p className="text-xs uppercase tracking-wide text-slate-400">Legal Mapping</p>
                    <ul className="mt-2 space-y-2 text-sm text-slate-200">
                      {analysis.result.legal_sections.map((law) => (
                        <li key={`${law.law}-${law.section}`}>• {law.section} ({law.law})</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mt-4 rounded-xl border border-slate-700 p-3">
                    <p className="text-xs uppercase tracking-wide text-slate-400">Explainability</p>
                    <ul className="mt-2 space-y-2 text-sm text-slate-200">
                      {(analysis.result.explainable_spans || []).slice(0, 6).map((span, idx) => (
                        <li key={`${span.term}-${idx}`}>• "{span.term}" → {span.reason}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="text-slate-300">No analysis yet. Run a text/image scan to view safety insights.</p>
              )}
            </div>
          </motion.div>

          <motion.div variants={fadeUp} className="glass rounded-2xl p-6">
            <div className="flex flex-wrap items-center gap-3">
              <button onClick={startFirFlow} disabled={firLoading} className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 disabled:opacity-60">
                {firLoading ? "Generating FIR..." : "Generate FIR"}
              </button>
              <button onClick={checkFirJob} className="rounded-xl border border-slate-500 px-4 py-2 text-sm font-semibold hover:border-slate-300">Check FIR Job</button>
              <button onClick={handleDownloadFir} className="rounded-xl border border-slate-500 px-4 py-2 text-sm font-semibold hover:border-slate-300">Download FIR</button>
              {firState.status ? <span className="text-sm text-slate-300">Status: {firState.status}</span> : null}
            </div>
          </motion.div>
        </motion.div>
      </section>

      <section className="mx-auto mt-20 max-w-6xl px-5">
        <div className="grid gap-5 md:grid-cols-3">
          {testimonials.map((t) => (
            <div key={t.name} className="glass rounded-2xl p-5">
              <p className="text-sm text-slate-200">"{t.quote}"</p>
              <p className="mt-3 text-xs text-slate-400">{t.name}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-20 max-w-6xl px-5 pb-10">
        <div className="glass rounded-3xl p-8 text-center">
          <h3 className="text-3xl font-extrabold">Make digital spaces safer now</h3>
          <p className="mx-auto mt-3 max-w-2xl text-slate-300">
            Deploy AI-led abuse intelligence with legal-grade reporting and child protection workflows.
          </p>
          {analytics ? (
            <p className="mt-4 text-sm text-slate-300">
              Analytics: {analytics.total_analyses} analyses, {analytics.recent_incidents} in the last 7 days.
            </p>
          ) : null}
        </div>
      </section>

      <footer className="mx-auto max-w-6xl px-5 pb-20 pt-8 text-center text-xs text-slate-400">
        Built for child safety, cyber threat response, and legal intelligence workflows.
      </footer>
    </main>
  );
}
