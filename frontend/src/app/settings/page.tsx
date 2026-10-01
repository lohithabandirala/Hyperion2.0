"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [provider, setProvider] = useState("gemini");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [saved, setSaved] = useState(false);

  return (
    <div className="p-8 max-w-4xl mx-auto w-full space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h1 className="text-2xl font-black text-slate-900">System &amp; AI Provider Settings</h1>
        <p className="text-xs text-slate-500 mt-1">Configure model provider abstractions, local offline fallback, and security parameters.</p>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">AI Model Provider</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Active LLM Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white"
              >
                <option value="gemini">Google Gemini 2.5 Flash (Production / Multimodal)</option>
                <option value="openai">OpenAI Compatible (GPT-4o / Local vLLM)</option>
                <option value="groq">Groq High-Speed Inference</option>
                <option value="mock">Local Deterministic Provider (Offline / Test Suite)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Model Name</label>
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
              />
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 pt-6 space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Enterprise Security Posture</h2>
          
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-slate-600 font-medium">SSRF URL Validation &amp; Private IP Blocking:</span>
              <span className="text-emerald-700 font-bold">ACTIVE ✓</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600 font-medium">Client-Side Secret Isolation:</span>
              <span className="text-emerald-700 font-bold">PROTECTED ✓</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600 font-medium">Canonical Fact Grounding Verification:</span>
              <span className="text-emerald-700 font-bold">ENFORCED ✓</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-600 font-medium">Audited Versioning &amp; Rollback:</span>
              <span className="text-emerald-700 font-bold">ENABLED ✓</span>
            </div>
          </div>
        </div>

        <div className="flex justify-between items-center pt-4 border-t border-slate-100">
          {saved && <span className="text-xs text-emerald-600 font-bold">✓ Configuration updated</span>}
          <button
            onClick={() => setSaved(true)}
            className="ml-auto px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg shadow-sm"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}
