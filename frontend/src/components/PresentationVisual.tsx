"use client";

import React, { useState } from 'react';

interface PresentationProps {
  content: string;
}

interface Slide {
  title: string;
  subtitle?: string;
  content: string[];
  visual_recommendation?: string;
  speaker_notes?: string;
}

export default function PresentationVisual({ content }: PresentationProps) {
  const [currentIdx, setCurrentIdx] = useState(0);

  let slides: Slide[] = [];
  let isInvalidJson = false;

  try {
    const parsed = JSON.parse(content);
    if (parsed.slides && Array.isArray(parsed.slides)) {
      slides = parsed.slides;
    }
  } catch {
    isInvalidJson = true;
  }

  if (isInvalidJson) {
    return <div className="whitespace-pre-wrap font-sans text-slate-800">{content}</div>;
  }

  if (slides.length === 0) {
    return <div className="p-4 text-slate-500">No slides available in this deck.</div>;
  }

  const slide = slides[currentIdx] || slides[0];

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Slide Canvas */}
      <div className="bg-slate-900 text-white rounded-xl shadow-2xl border border-slate-700 aspect-[16/9] flex flex-col justify-between p-8 relative overflow-hidden">
        {/* Slide Header */}
        <div className="border-b border-slate-800 pb-4">
          <div className="flex justify-between items-center text-xs text-blue-400 font-semibold tracking-wider uppercase mb-1">
            <span>NTRO Executive Presentation</span>
            <span>Slide {currentIdx + 1} of {slides.length}</span>
          </div>
          <h2 className="text-2xl font-black text-white">{slide.title}</h2>
          {slide.subtitle && (
            <p className="text-sm text-blue-300 mt-1">{slide.subtitle}</p>
          )}
        </div>

        {/* Slide Body */}
        <div className="my-auto space-y-3 pl-4">
          {Array.isArray(slide.content) && slide.content.map((bullet: string, idx: number) => (
            <div key={idx} className="flex items-start space-x-3 text-slate-200 text-base leading-relaxed">
              <span className="text-blue-500 font-bold mt-0.5">•</span>
              <span>{bullet}</span>
            </div>
          ))}
        </div>

        {/* Slide Footer */}
        <div className="border-t border-slate-800 pt-3 flex justify-between items-center text-xs text-slate-400">
          <span className="italic">Visual: {slide.visual_recommendation || "Executive overview chart"}</span>
          <span className="font-mono">OFFICIAL / NTRO-TRANSFORM</span>
        </div>
      </div>

      {/* Slide Navigation & Speaker Notes */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-start">
        {/* Navigator Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setCurrentIdx(Math.max(0, currentIdx - 1))}
            disabled={currentIdx === 0}
            className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            ← Previous
          </button>
          <span className="text-sm font-medium text-slate-600">
            {currentIdx + 1} / {slides.length}
          </span>
          <button
            onClick={() => setCurrentIdx(Math.min(slides.length - 1, currentIdx + 1))}
            disabled={currentIdx === slides.length - 1}
            className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Next →
          </button>
        </div>

        {/* Speaker Notes */}
        {slide.speaker_notes && (
          <div className="flex-1 bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900">
            <span className="font-bold block mb-1">Speaker Notes:</span>
            {slide.speaker_notes}
          </div>
        )}
      </div>
    </div>
  );
}
