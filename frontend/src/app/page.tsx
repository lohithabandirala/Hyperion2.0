"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  createProject,
  uploadSource,
  createSourceText,
  createSourceUrl,
  createTransformation,
  loadDemoData
} from "@/services/api";

interface SourceInfo {
  source_id: number;
  project_id: number;
  title: string;
  filename: string;
  preview: string;
  is_demo: boolean;
  words_count: number;
  facts_count: number;
}

export default function Dashboard() {
  const router = useRouter();
  
  // Ingestion Mode State
  const [ingestMode, setIngestMode] = useState<"file" | "text" | "url">("file");
  const [file, setFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState("");
  const [textTitle, setTextTitle] = useState("Manual Intel Brief");
  const [urlInput, setUrlInput] = useState("");
  const [activeSourceInfo, setActiveSourceInfo] = useState<SourceInfo | null>(null);

  // Configuration Form State
  const [audience, setAudience] = useState("Executive");
  const [tone, setTone] = useState("Professional");
  const [detail, setDetail] = useState("Medium");
  const [objective, setObjective] = useState("Inform");
  const [language, setLanguage] = useState("English");
  
  // 7 Selected Outputs
  const [outputs, setOutputs] = useState<Record<string, boolean>>({
    linkedin: true,
    x: true,
    advisory: true,
    summary: true,
    infographic: true,
    presentation: true,
    video: true,
  });

  const [loading, setLoading] = useState(false);
  const [demoLoaded, setDemoLoaded] = useState(false);

  // 1-Click Load Demo Action
  const handleLoadDemo = async () => {
    setLoading(true);
    try {
      const res = await loadDemoData();
      setActiveSourceInfo({
        source_id: res.data.source_id,
        project_id: res.data.project_id,
        title: res.data.title,
        filename: res.data.filename,
        preview: res.data.content_preview,
        is_demo: true,
        words_count: 248,
        facts_count: 6
      });
      setDemoLoaded(true);
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } }; message?: string };
      alert("Failed to load demo data: " + (errorObj.response?.data?.detail || errorObj.message));
    } finally {
      setLoading(false);
    }
  };

  const handleStartTransformation = async () => {
    const selectedOutputs = Object.keys(outputs).filter(k => outputs[k]);
    if (selectedOutputs.length === 0) {
      alert("Please select at least one output artefact.");
      return;
    }

    setLoading(true);
    try {
      let sourceId = activeSourceInfo?.source_id;

      // If source not loaded via demo, create it now
      if (!sourceId) {
        const projRes = await createProject("NTRO Strategic Transformation", "Operations Workflow");
        const projId = projRes.data.id;

        if (ingestMode === "file") {
          if (!file) {
            alert("Please select a file to upload.");
            setLoading(false);
            return;
          }
          const srcRes = await uploadSource(projId, file);
          sourceId = srcRes.data.id;
        } else if (ingestMode === "text") {
          if (!pastedText.trim()) {
            alert("Please enter text content.");
            setLoading(false);
            return;
          }
          const srcRes = await createSourceText(projId, textTitle, pastedText);
          sourceId = srcRes.data.id;
        } else if (ingestMode === "url") {
          if (!urlInput.trim()) {
            alert("Please enter a valid URL.");
            setLoading(false);
            return;
          }
          const srcRes = await createSourceUrl(projId, urlInput);
          sourceId = srcRes.data.id;
        }
      }

      // Trigger the Transformation Pipeline
      const transformRes = await createTransformation({
        source_id: sourceId,
        audience,
        tone,
        language,
        detail_level: detail,
        objective,
        outputs: selectedOutputs
      });

      const transformId = transformRes.data.transformation_id;
      router.push(`/transform/${transformId}`);
    } catch (err: unknown) {
      console.error(err);
      const errorObj = err as { response?: { data?: { detail?: string } }; message?: string };
      alert("Error starting transformation: " + (errorObj.response?.data?.detail || errorObj.message));
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-blue-100 text-blue-800 tracking-wider">
              NTRO PS 26154
            </span>
            <span className="text-xs text-slate-500 font-mono">CANONICAL FACT ARCHITECTURE</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-1">
            Automated Content Transformation Platform
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Transform a single source of truth into synchronized, fact-verified multi-channel artefacts.
          </p>
        </div>

        {/* Demo Button */}
        <button
          onClick={handleLoadDemo}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white font-bold px-5 py-3 rounded-lg shadow-md transition transform active:scale-95 text-sm shrink-0"
        >
          <span>⚡</span>
          <span>{demoLoaded ? "Reload Demo Scenario" : "Load Demo Scenario"}</span>
        </button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Ingestion & Outputs (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Step 1: Source Ingestion */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center">1</span>
                Source Ingestion
              </h2>
              <span className="text-xs text-slate-400 font-medium">PDF, DOCX, TXT, Image, Video, URL</span>
            </div>

            {/* Mode Switcher */}
            <div className="flex bg-slate-100 p-1 rounded-lg mb-4 text-xs font-semibold">
              <button
                onClick={() => { setIngestMode("file"); setActiveSourceInfo(null); }}
                className={`flex-1 py-2 rounded-md transition ${ingestMode === "file" && !activeSourceInfo?.is_demo ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"}`}
              >
                Upload File (PDF / DOCX / Media)
              </button>
              <button
                onClick={() => { setIngestMode("text"); setActiveSourceInfo(null); }}
                className={`flex-1 py-2 rounded-md transition ${ingestMode === "text" && !activeSourceInfo?.is_demo ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"}`}
              >
                Paste Text
              </button>
              <button
                onClick={() => { setIngestMode("url"); setActiveSourceInfo(null); }}
                className={`flex-1 py-2 rounded-md transition ${ingestMode === "url" && !activeSourceInfo?.is_demo ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"}`}
              >
                Web URL
              </button>
            </div>

            {/* Active Demo Source Preview */}
            {activeSourceInfo && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="bg-emerald-200 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded tracking-wider uppercase">
                      ACTIVE DEMO SOURCE
                    </span>
                    <h3 className="font-bold text-emerald-950 text-sm mt-1">{activeSourceInfo.title}</h3>
                  </div>
                  <button
                    onClick={() => setActiveSourceInfo(null)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Clear
                  </button>
                </div>
                <p className="text-xs text-emerald-800 italic line-clamp-3 mb-2">
                  &quot;{activeSourceInfo.preview}&quot;
                </p>
                <div className="flex gap-4 text-[11px] text-emerald-700 font-mono">
                  <span>✓ Extracted: 6 Canonical Facts</span>
                  <span>✓ Words: 248</span>
                  <span>✓ 100% Traceable</span>
                </div>
              </div>
            )}

            {/* Ingestion Inputs (If not demo) */}
            {!activeSourceInfo && (
              <>
                {ingestMode === "file" && (
                  <div className="border-2 border-dashed border-slate-300 p-6 text-center rounded-lg hover:bg-slate-50 transition">
                    <input
                      type="file"
                      id="file-upload-input"
                      className="hidden"
                      onChange={(e) => e.target.files && setFile(e.target.files[0])}
                    />
                    <label htmlFor="file-upload-input" className="cursor-pointer block">
                      {file ? (
                        <div className="space-y-1">
                          <div className="text-blue-600 font-bold text-sm">{file.name}</div>
                          <div className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB</div>
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <div className="text-slate-700 font-semibold text-sm">Choose PDF, DOCX, Image, or Video file</div>
                          <div className="text-xs text-slate-400">Supports OCR for images and transcription for video/audio</div>
                        </div>
                      )}
                    </label>
                  </div>
                )}

                {ingestMode === "text" && (
                  <div className="space-y-3">
                    <input
                      type="text"
                      placeholder="Document Title (e.g. Strategic Operational Bulletin)"
                      value={textTitle}
                      onChange={(e) => setTextTitle(e.target.value)}
                      className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
                    />
                    <textarea
                      placeholder="Paste raw text, situation reports, or policy announcements here..."
                      rows={5}
                      value={pastedText}
                      onChange={(e) => setPastedText(e.target.value)}
                      className="w-full text-xs p-3 border border-slate-300 rounded-lg"
                    />
                  </div>
                )}

                {ingestMode === "url" && (
                  <div>
                    <input
                      type="url"
                      placeholder="https://example.gov.in/press-release/incident-update"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      className="w-full text-xs p-3 border border-slate-300 rounded-lg"
                    />
                    <p className="text-[11px] text-slate-400 mt-1">Protected with SSRF validation and safe content extraction.</p>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Step 2: Select Communication Artefacts */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center">2</span>
                Output Artefacts
              </h2>
              <span className="text-xs text-blue-600 font-semibold">
                {Object.values(outputs).filter(Boolean).length} of 7 Selected
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                { key: "advisory", name: "Strategic Advisory", desc: "Formal executive situational directive", icon: "🛡️" },
                { key: "summary", name: "Executive Summary", desc: "High-density decision-maker briefing", icon: "📄" },
                { key: "linkedin", name: "LinkedIn Post", desc: "Strategic public/stakeholder engagement", icon: "💼" },
                { key: "x", name: "X / Twitter Thread", desc: "Multi-tweet thread under 280 chars", icon: "🐦" },
                { key: "infographic", name: "Infographic Layout", desc: "Visual metrics, hierarchy & key takeaway", icon: "📊" },
                { key: "presentation", name: "Presentation Deck", desc: "Slide-by-slide structure & speaker notes", icon: "📽️" },
                { key: "video", name: "Video Package", desc: "Scene storyboard, voiceover & subtitles", icon: "🎬" },
              ].map((item) => (
                <label
                  key={item.key}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition ${outputs[item.key] ? "bg-blue-50/70 border-blue-300 shadow-xs" : "bg-slate-50/50 border-slate-200 hover:bg-slate-100"}`}
                >
                  <input
                    type="checkbox"
                    checked={outputs[item.key]}
                    onChange={() => setOutputs({ ...outputs, [item.key]: !outputs[item.key] })}
                    className="w-4 h-4 text-blue-600 rounded mt-0.5"
                  />
                  <div>
                    <div className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <span>{item.icon}</span>
                      <span>{item.name}</span>
                    </div>
                    <div className="text-[11px] text-slate-500">{item.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Configuration & Trigger (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center">3</span>
              Operator Configuration
            </h2>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Target Audience</label>
              <select className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white" value={audience} onChange={e => setAudience(e.target.value)}>
                <option>Executive</option>
                <option>Government &amp; Ministry</option>
                <option>General Public</option>
                <option>Technical &amp; Engineering</option>
                <option>Media &amp; Press</option>
                <option>Internal Tactical Team</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Tone &amp; Posture</label>
              <select className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white" value={tone} onChange={e => setTone(e.target.value)}>
                <option>Professional</option>
                <option>Formal &amp; Official</option>
                <option>Urgent &amp; Alert</option>
                <option>Neutral &amp; Informative</option>
                <option>Technical Rigor</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Target Language</label>
                <select className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white" value={language} onChange={e => setLanguage(e.target.value)}>
                  <option>English</option>
                  <option>Hindi</option>
                  <option>Telugu</option>
                  <option>Tamil</option>
                  <option>Kannada</option>
                  <option>Marathi</option>
                  <option>Bengali</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Detail Level</label>
                <select className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white" value={detail} onChange={e => setDetail(e.target.value)}>
                  <option>Brief</option>
                  <option>Medium</option>
                  <option>Detailed</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Communication Objective</label>
              <select className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white" value={objective} onChange={e => setObjective(e.target.value)}>
                <option>Inform</option>
                <option>Alert &amp; Contain</option>
                <option>Explain &amp; Reassure</option>
                <option>Educate &amp; Guide</option>
                <option>Summarize Telemetry</option>
              </select>
            </div>
          </div>

          {/* Trigger Button */}
          <button
            onClick={handleStartTransformation}
            disabled={loading || (!file && !activeSourceInfo && !pastedText && !urlInput)}
            className={`w-full py-4 text-base font-black rounded-xl shadow-lg transition flex items-center justify-center gap-3 ${loading || (!file && !activeSourceInfo && !pastedText && !urlInput) ? "bg-slate-300 text-slate-500 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700 text-white hover:shadow-blue-500/25 active:scale-98"}`}
          >
            {loading ? (
              <>
                <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                <span>Initializing Pipeline...</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>TRANSFORM CONTENT</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
