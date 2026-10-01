"use client";

import React from 'react';

interface InfographicProps {
  content: string;
}

interface InfographicSection {
  title: string;
  value: string;
  explanation: string;
}

interface InfographicData {
  headline?: string;
  subheadline?: string;
  key_statistic?: string;
  sections?: InfographicSection[];
  key_takeaway?: string;
}

export default function InfographicVisual({ content }: InfographicProps) {
  let data: InfographicData | null = null;
  try {
    data = JSON.parse(content);
  } catch {
    // If not JSON, render fallback
    return <div className="whitespace-pre-wrap font-sans text-slate-800">{content}</div>;
  }

  const sections = data.sections || [];

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-blue-950 text-white p-8 rounded-xl shadow-xl border border-slate-700 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="text-center border-b border-slate-700 pb-6 mb-8">
        <div className="inline-block px-3 py-1 bg-blue-600/30 text-blue-400 text-xs font-semibold tracking-widest rounded-full uppercase mb-3 border border-blue-500/30">
          NTRO Strategic Infographic Briefing
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">
          {data.headline || "Infrastructure Operations Report"}
        </h1>
        {data.subheadline && (
          <p className="text-slate-300 text-sm max-w-2xl mx-auto">
            {data.subheadline}
          </p>
        )}
      </div>

      {/* Big Hero Statistic */}
      {data.key_statistic && (
        <div className="bg-gradient-to-r from-blue-600/20 to-indigo-600/20 border border-blue-500/30 rounded-xl p-6 mb-8 text-center backdrop-blur-sm">
          <div className="text-xs uppercase tracking-wider text-blue-300 font-semibold mb-1">Key Operational Metric</div>
          <div className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-300">
            {data.key_statistic}
          </div>
        </div>
      )}

      {/* Grid of Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {sections.map((sec: InfographicSection, idx: number) => (
          <div key={idx} className="bg-slate-800/80 border border-slate-700 rounded-lg p-5 hover:border-blue-500/50 transition">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {sec.title}
              </span>
              <span className="text-sm font-extrabold text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/50">
                {sec.value}
              </span>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed">
              {sec.explanation}
            </p>
          </div>
        ))}
      </div>

      {/* Key Takeaway Footer */}
      {data.key_takeaway && (
        <div className="bg-slate-900/90 border-l-4 border-blue-500 p-4 rounded-r-lg flex items-center justify-between text-sm text-slate-300">
          <div>
            <span className="font-bold text-white mr-2">Key Takeaway:</span>
            {data.key_takeaway}
          </div>
          <span className="text-xs text-slate-500 font-mono shrink-0 ml-4">CONFIDENTIAL &amp; VERIFIED</span>
        </div>
      )}
    </div>
  );
}
