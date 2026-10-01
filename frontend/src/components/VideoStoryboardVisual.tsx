"use client";

import React from 'react';

interface VideoProps {
  content: string;
}

export default function VideoStoryboardVisual({ content }: VideoProps) {
  let videoData: any = null;
  try {
    videoData = JSON.parse(content);
  } catch (e) {
    return <div className="whitespace-pre-wrap font-sans text-slate-800">{content}</div>;
  }

  const scenes = videoData.scenes || [];
  const subtitles = videoData.subtitles || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Video Package Overview Card */}
      <div className="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 shadow-md">
        <div className="flex justify-between items-start mb-2">
          <div>
            <div className="text-xs font-bold text-red-500 uppercase tracking-widest mb-1 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              Video Package &amp; Storyboard Specification
            </div>
            <h2 className="text-xl font-bold text-white">{videoData.title || "Operational Briefing Video"}</h2>
          </div>
          {videoData.duration_seconds && (
            <span className="bg-slate-800 text-blue-400 font-mono text-xs px-2.5 py-1 rounded border border-slate-700">
              Total Duration: {videoData.duration_seconds}s
            </span>
          )}
        </div>
        {videoData.description && (
          <p className="text-slate-400 text-xs mt-1 leading-relaxed">
            {videoData.description}
          </p>
        )}
      </div>

      {/* Storyboard Scenes */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider">
          Scene Breakdown ({scenes.length} Scenes)
        </h3>
        <div className="grid grid-cols-1 gap-4">
          {scenes.map((scene: any, idx: number) => (
            <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow transition">
              <div className="flex justify-between items-center border-b border-slate-100 pb-3 mb-3">
                <span className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <span className="bg-slate-900 text-white text-xs w-6 h-6 rounded-full inline-flex items-center justify-center">
                    {scene.scene_number || idx + 1}
                  </span>
                  Scene {scene.scene_number || idx + 1}
                </span>
                <div className="flex items-center gap-2 text-xs">
                  <span className="bg-blue-50 text-blue-700 font-medium px-2 py-0.5 rounded border border-blue-200">
                    ⏱ {scene.duration || "10s"}
                  </span>
                  {scene.transition && (
                    <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                      Transition: {scene.transition}
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {/* Visual Direction */}
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 space-y-1.5">
                  <span className="font-bold text-slate-700 block uppercase tracking-wider text-[11px]">
                    📹 Visual Direction &amp; Camera
                  </span>
                  <p className="text-slate-600 leading-relaxed">
                    {scene.visual_description}
                  </p>
                  {scene.camera_direction && (
                    <p className="text-slate-500 italic mt-1">
                      Camera: {scene.camera_direction}
                    </p>
                  )}
                  {scene.on_screen_text && (
                    <div className="mt-2 text-blue-700 font-semibold bg-blue-100/50 p-1.5 rounded">
                      [On-Screen]: &quot;{scene.on_screen_text}&quot;
                    </div>
                  )}
                </div>

                {/* Voiceover / Narration */}
                <div className="bg-blue-50/50 p-3 rounded-lg border border-blue-100/80 space-y-1.5">
                  <span className="font-bold text-blue-900 block uppercase tracking-wider text-[11px]">
                    🎙️ Voiceover Narration
                  </span>
                  <p className="text-slate-800 text-sm leading-relaxed italic">
                    &quot;{scene.narration}&quot;
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Subtitles Track */}
      {subtitles.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">
            Timed Subtitle Segments (SRT / VTT Ready)
          </h3>
          <div className="space-y-2 font-mono text-xs">
            {subtitles.map((sub: any, idx: number) => (
              <div key={idx} className="flex gap-3 bg-slate-50 p-2 rounded border border-slate-100">
                <span className="text-blue-600 font-semibold shrink-0">
                  {sub.start} → {sub.end}
                </span>
                <span className="text-slate-700 font-sans">{sub.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
