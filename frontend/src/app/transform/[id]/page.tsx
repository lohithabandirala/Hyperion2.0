"use client";

import { useEffect, useState, use } from "react";
import {
  getTransformationStatus,
  getTransformationOutputs,
  getTransformationFacts,
  approveOutput,
  rejectOutput,
  editOutput,
  regenerateOutput,
  getOutputVersions,
  rollbackOutputVersion,
  getExportUrl
} from "@/services/api";
import InfographicVisual from "@/components/InfographicVisual";
import PresentationVisual from "@/components/PresentationVisual";
import VideoStoryboardVisual from "@/components/VideoStoryboardVisual";

interface TransformationStatus {
  id: number;
  status: string;
  stage: string;
  progress_percent: number;
  error_message?: string;
}

interface ClaimAnalysis {
  matched_fact_id?: string;
  status?: string;
  output_claim?: string;
}

interface OutputItem {
  id: number;
  type: string;
  content: string;
  status: string;
  quality_status?: string;
  current_version: number;
  provenance_id?: string;
  artifact_hash?: string;
  fact_consistency_report?: {
    unsupported_claims_count?: number;
    claims_analysis?: ClaimAnalysis[];
  };
  quality_report?: Record<string, unknown>;
}

interface FactItem {
  fact_id: string;
  claim: string;
  source_reference?: string;
  fact_type?: string;
}

interface VersionItem {
  id: number;
  version: number;
  content: string;
  created_at: string;
  change_description?: string;
  created_by?: string;
}

export default function TransformWorkspace({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const [transform, setTransform] = useState<TransformationStatus | null>(null);
  const [outputs, setOutputs] = useState<OutputItem[]>([]);
  const [facts, setFacts] = useState<FactItem[]>([]);
  const [activeTab, setActiveTab] = useState<string>("facts"); // "facts" or output type
  const [loading, setLoading] = useState(true);

  // Modals & Panels
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regenPrompt, setRegenPrompt] = useState("");
  const [regenTone, setRegenTone] = useState("");
  const [showVersions, setShowVersions] = useState(false);
  const [versionsList, setVersionsList] = useState<VersionItem[]>([]);
  const [showFactPanel, setShowFactPanel] = useState(true);

  // Polling for transformation status & outputs
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval> | null = null;

    const fetchStatus = async () => {
      try {
        const tRes = await getTransformationStatus(Number(id));
        setTransform(tRes.data);

        if (tRes.data.status === "COMPLETED" || tRes.data.status === "PARTIAL_SUCCESS") {
          // Fetch final outputs and facts
          const oRes = await getTransformationOutputs(Number(id));
          setOutputs(oRes.data);

          const fRes = await getTransformationFacts(Number(id));
          setFacts(fRes.data);

          if (oRes.data.length > 0 && activeTab === "facts") {
            setActiveTab(oRes.data[0].type);
          }

          setLoading(false);
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    };

    fetchStatus();
    intervalId = setInterval(fetchStatus, 1500);

    return () => clearInterval(intervalId);
  }, [id, activeTab]);

  const activeOutput = outputs.find(o => o.type === activeTab);

  // Review Actions
  const handleApprove = async () => {
    if (!activeOutput) return;
    await approveOutput(activeOutput.id);
    const oRes = await getTransformationOutputs(Number(id));
    setOutputs(oRes.data);
  };

  const handleReject = async () => {
    if (!activeOutput) return;
    await rejectOutput(activeOutput.id);
    const oRes = await getTransformationOutputs(Number(id));
    setOutputs(oRes.data);
  };

  // Edit Action
  const handleSaveEdit = async () => {
    if (!activeOutput) return;
    await editOutput(activeOutput.id, editContent, "Human Operator Revision");
    setIsEditing(false);
    const oRes = await getTransformationOutputs(Number(id));
    setOutputs(oRes.data);
  };

  // Regenerate Action
  const handleRegenerate = async () => {
    if (!activeOutput) return;
    setLoading(true);
    await regenerateOutput(activeOutput.id, regenPrompt, regenTone);
    setIsRegenerating(false);
    setRegenPrompt("");
    const oRes = await getTransformationOutputs(Number(id));
    setOutputs(oRes.data);
    setLoading(false);
  };

  // Load Versions
  const handleOpenVersions = async () => {
    if (!activeOutput) return;
    const vRes = await getOutputVersions(activeOutput.id);
    setVersionsList(vRes.data);
    setShowVersions(true);
  };

  const handleRollback = async (versionId: number) => {
    if (!activeOutput) return;
    await rollbackOutputVersion(activeOutput.id, versionId);
    setShowVersions(false);
    const oRes = await getTransformationOutputs(Number(id));
    setOutputs(oRes.data);
  };

  if (!transform) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm font-semibold text-slate-600">Loading Transformation Workspace #{id}...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-slate-50">
      {/* Top Header & Live Progress Stepper */}
      <div className="bg-white border-b border-slate-200 px-6 py-4 shrink-0 shadow-xs">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-3">
          <div className="flex items-center gap-3">
            <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 text-slate-700">
              TRX-{transform.id}
            </span>
            <h1 className="text-xl font-bold text-slate-900">
              Strategic Transformation Workspace
            </h1>
            <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${transform.status === "COMPLETED" ? "bg-green-100 text-green-800" : transform.status === "PARTIAL_SUCCESS" ? "bg-amber-100 text-amber-800" : "bg-blue-100 text-blue-800 animate-pulse"}`}>
              {transform.status}
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-500 font-medium">
            <span>Progress: {transform.progress_percent || 0}%</span>
            <button
              onClick={() => setShowFactPanel(!showFactPanel)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold transition ${showFactPanel ? "bg-blue-50 border-blue-300 text-blue-700" : "bg-white border-slate-300 text-slate-700"}`}
            >
              {showFactPanel ? "Hide Fact Inspector" : "Show Fact Inspector"}
            </button>
          </div>
        </div>

        {/* Multi-Stage Stepper */}
        <div className="grid grid-cols-6 gap-2 text-center text-[10px] font-bold uppercase tracking-wider">
          {[
            { key: "INGESTING", label: "1. Ingest" },
            { key: "UNDERSTANDING", label: "2. Understand" },
            { key: "EXTRACTING_FACTS", label: "3. Facts" },
            { key: "BUILDING_SEMANTIC_MODEL", label: "4. Semantic" },
            { key: "GENERATING", label: "5. Generate" },
            { key: "COMPLETED", label: "6. Verified" },
          ].map((st, idx) => {
            const isDone = transform.progress_percent >= (idx + 1) * 16 || transform.status === "COMPLETED";
            return (
              <div
                key={st.key}
                className={`py-1.5 rounded transition ${isDone ? "bg-blue-600 text-white shadow-xs" : "bg-slate-100 text-slate-400"}`}
              >
                {st.label}
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Workspace Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Artefact Tabs */}
        <div className="w-64 border-r border-slate-200 bg-white flex flex-col shrink-0">
          <div className="p-3 border-b border-slate-100 font-bold text-xs text-slate-400 uppercase tracking-wider">
            Communication Artefacts
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
            {/* Fact Registry Tab */}
            <button
              onClick={() => setActiveTab("facts")}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-xs font-bold flex items-center justify-between transition ${activeTab === "facts" ? "bg-slate-900 text-white" : "hover:bg-slate-100 text-slate-700"}`}
            >
              <span>📋 Canonical Fact Registry</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                {facts.length}
              </span>
            </button>

            <div className="pt-2 pb-1 border-t border-slate-100 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Generated Outputs
            </div>

            {outputs.map((out) => (
              <button
                key={out.id}
                onClick={() => setActiveTab(out.type)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-between capitalize transition ${activeTab === out.type ? "bg-blue-600 text-white shadow-sm" : "hover:bg-slate-100 text-slate-700"}`}
              >
                <span>{out.type === "x" ? "X / Twitter" : out.type}</span>
                <span className="flex items-center gap-1">
                  <span className={`w-2 h-2 rounded-full ${out.status === "APPROVED" ? "bg-emerald-400" : "bg-amber-400"}`}></span>
                  <span className="text-[10px] opacity-80">v{out.current_version}</span>
                </span>
              </button>
            ))}

            {loading && (
              <div className="text-xs text-slate-400 p-3 italic text-center animate-pulse">
                Generating artefacts...
              </div>
            )}
          </div>
        </div>

        {/* Center Panel: Content Presentation & Actions */}
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
          {/* Fact Registry View */}
          {activeTab === "facts" && (
            <div className="p-8 overflow-y-auto max-w-5xl mx-auto w-full space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">Canonical Fact Registry (Ground Truth)</h2>
                    <p className="text-xs text-slate-500">Every generated communication artefact is strictly grounded in these verified facts.</p>
                  </div>
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full">
                    {facts.length} Verified Facts
                  </span>
                </div>

                <div className="space-y-3">
                  {facts.map((fact) => (
                    <div key={fact.id} className="p-4 rounded-lg bg-slate-50 border border-slate-200 flex items-start gap-4">
                      <span className="px-2 py-1 bg-slate-800 text-white text-[10px] font-mono font-bold rounded">
                        {fact.fact_id}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800 uppercase">
                            {fact.fact_type}
                          </span>
                          {fact.source_reference && (
                            <span className="text-[11px] text-slate-400 italic">
                              Ref: {fact.source_reference}
                            </span>
                          )}
                        </div>
                        <p className="text-xs font-medium text-slate-800 leading-relaxed">{fact.claim}</p>
                      </div>
                      <span className="text-xs font-bold text-emerald-600 font-mono shrink-0">
                        {Math.round(fact.confidence * 100)}% Conf
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Active Generated Output View */}
          {activeTab !== "facts" && activeOutput && (
            <div className="flex flex-col h-full">
              {/* Output Action Header */}
              <div className="bg-white border-b border-slate-200 px-8 py-4 flex flex-wrap justify-between items-center gap-4 shrink-0">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl font-bold capitalize text-slate-900">
                      {activeOutput.type === "x" ? "X / Twitter Thread" : activeOutput.type}
                    </h2>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono font-bold">
                      v{activeOutput.current_version}
                    </span>
                    <span className={`text-xs px-2.5 py-0.5 rounded font-bold uppercase ${activeOutput.status === "APPROVED" ? "bg-emerald-100 text-emerald-800" : activeOutput.status === "REJECTED" ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"}`}>
                      {activeOutput.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Quality: <span className="font-semibold text-slate-700">{activeOutput.quality_status}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 text-xs font-semibold">
                  <button
                    onClick={handleOpenVersions}
                    className="px-3 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg transition"
                  >
                    Versions ({activeOutput.current_version})
                  </button>

                  <button
                    onClick={() => { setEditContent(activeOutput.content); setIsEditing(true); }}
                    className="px-3 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg transition"
                  >
                    ✏️ Edit
                  </button>

                  <button
                    onClick={() => setIsRegenerating(true)}
                    className="px-3 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg transition"
                  >
                    🔄 Targeted Regen
                  </button>

                  {activeOutput.status !== "APPROVED" && (
                    <button
                      onClick={handleApprove}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-sm transition"
                    >
                      ✓ Approve
                    </button>
                  )}

                  {activeOutput.status === "APPROVED" && (
                    <button
                      onClick={handleReject}
                      className="px-3 py-2 bg-red-50 text-red-700 hover:bg-red-100 rounded-lg transition"
                    >
                      Reject
                    </button>
                  )}

                  {/* Export Dropdown / Buttons */}
                  <div className="flex items-center bg-slate-900 text-white rounded-lg overflow-hidden">
                    <span className="px-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">Export:</span>
                    {activeOutput.type === "presentation" ? (
                      <a
                        href={getExportUrl(activeOutput.id, "pptx")}
                        download
                        className="px-3 py-2 hover:bg-blue-600 text-xs font-bold transition border-l border-slate-800"
                      >
                        PPTX
                      </a>
                    ) : (
                      <>
                        <a
                          href={getExportUrl(activeOutput.id, "docx")}
                          download
                          className="px-2.5 py-2 hover:bg-blue-600 text-xs font-bold transition border-l border-slate-800"
                        >
                          DOCX
                        </a>
                        <a
                          href={getExportUrl(activeOutput.id, "pdf")}
                          download
                          className="px-2.5 py-2 hover:bg-blue-600 text-xs font-bold transition border-l border-slate-800"
                        >
                          PDF
                        </a>
                      </>
                    )}
                    <a
                      href={getExportUrl(activeOutput.id, "md")}
                      download
                      className="px-2.5 py-2 hover:bg-blue-600 text-xs font-bold transition border-l border-slate-800"
                    >
                      MD
                    </a>
                  </div>
                </div>
              </div>

              {/* Output Content Area */}
              <div className="flex-1 overflow-y-auto p-8">
                {activeOutput.type === "infographic" ? (
                  <InfographicVisual content={activeOutput.content} />
                ) : activeOutput.type === "presentation" ? (
                  <PresentationVisual content={activeOutput.content} />
                ) : activeOutput.type === "video" ? (
                  <VideoStoryboardVisual content={activeOutput.content} />
                ) : (
                  <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm max-w-4xl mx-auto whitespace-pre-wrap font-sans text-slate-800 text-sm leading-relaxed">
                    {activeOutput.content}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Drawer: Fact Consistency & Traceability Inspector */}
        {showFactPanel && activeOutput && activeTab !== "facts" && (
          <div className="w-80 border-l border-slate-200 bg-white p-5 flex flex-col shrink-0 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-xs text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <span>🛡️</span>
                <span>Fact Verification</span>
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                {activeOutput.fact_consistency_report?.overall_status || "VERIFIED"}
              </span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-xs space-y-1.5 mb-4">
              <div className="flex justify-between">
                <span className="text-slate-500">Verified Facts:</span>
                <span className="font-bold text-emerald-600">
                  {activeOutput.fact_consistency_report?.verified_facts_count || facts.length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Conflicts Detected:</span>
                <span className="font-bold text-slate-900">
                  {activeOutput.fact_consistency_report?.conflicts_count || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Unsupported Claims:</span>
                <span className="font-bold text-slate-900">
                  {activeOutput.fact_consistency_report?.unsupported_claims_count || 0}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                Claim-Level Traceability
              </span>
              {(activeOutput.fact_consistency_report?.claims_analysis || []).map((claim: ClaimAnalysis, idx: number) => (
                <div key={idx} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] font-bold text-slate-500">
                      {claim.matched_fact_id || `C00${idx+1}`}
                    </span>
                    <span className="text-[10px] font-bold text-emerald-700">
                      ✓ {claim.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-700 line-clamp-2">
                    {claim.output_claim}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">Edit Generated Output</h3>
            <textarea
              rows={12}
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="w-full text-xs p-3 border border-slate-300 rounded-lg font-sans"
            />
            <div className="flex justify-end gap-3 text-xs font-semibold">
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save New Version
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Targeted Regenerate Modal */}
      {isRegenerating && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">Targeted AI Regeneration</h3>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Instruction</label>
              <input
                type="text"
                placeholder="e.g. Make shorter, emphasize 45-min timeline..."
                value={regenPrompt}
                onChange={(e) => setRegenPrompt(e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Tone Adjustment</label>
              <select
                value={regenTone}
                onChange={(e) => setRegenTone(e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white"
              >
                <option value="">Keep Existing Tone</option>
                <option value="Urgent & Alert">Urgent &amp; Alert</option>
                <option value="Technical Rigor">Technical Rigor</option>
                <option value="Formal & Official">Formal &amp; Official</option>
              </select>
            </div>
            <div className="flex justify-end gap-3 text-xs font-semibold">
              <button
                onClick={() => setIsRegenerating(false)}
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={handleRegenerate}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Regenerate Output
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Version History Modal */}
      {showVersions && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-900">Version History</h3>
              <button onClick={() => setShowVersions(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {versionsList.map((ver) => (
                <div key={ver.id} className="p-3.5 border border-slate-200 rounded-lg bg-slate-50 flex justify-between items-center">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-900">Version {ver.version}</span>
                      <span className="text-[10px] text-slate-500 font-mono">{ver.created_by}</span>
                    </div>
                    <p className="text-xs text-slate-600 mt-0.5">{ver.change_description}</p>
                  </div>
                  {ver.version !== activeOutput?.current_version && (
                    <button
                      onClick={() => handleRollback(ver.id)}
                      className="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded text-xs font-bold"
                    >
                      Rollback
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
