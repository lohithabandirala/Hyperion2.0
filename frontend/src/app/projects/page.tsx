"use client";

import { useEffect, useState } from "react";
import { getProjects, createProject, deleteProject } from "@/services/api";
import Link from "next/link";

interface Project {
  id: number;
  title: string;
  description?: string;
  created_at: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchProjectsList = async () => {
    try {
      const res = await getProjects();
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let ignore = false;
    getProjects()
      .then((res) => {
        if (!ignore) {
          setProjects(res.data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (!ignore) {
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    await createProject(newTitle, newDesc);
    setNewTitle("");
    setNewDesc("");
    setShowModal(false);
    fetchProjectsList();
  };

  const handleDelete = async (id: number) => {
    if (confirm("Delete this project?")) {
      await deleteProject(id);
      fetchProjectsList();
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto w-full space-y-6">
      <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Project Workspace Management</h1>
          <p className="text-xs text-slate-500 mt-1">Organize and isolate sources, canonical registries, and multi-channel outputs by project.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm"
        >
          + Create Project
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-slate-400">Loading projects...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {projects.map((p) => (
            <div key={p.id} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                    PRJ-{p.id}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {new Date(p.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-base mb-1">{p.title}</h3>
                <p className="text-xs text-slate-500 line-clamp-2">{p.description || "No description provided."}</p>
              </div>

              <div className="flex justify-between items-center pt-4 border-t border-slate-100 text-xs font-bold">
                <Link href="/" className="text-blue-600 hover:underline">
                  Open Workspace →
                </Link>
                <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:underline">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">Create New Project</h3>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Project Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Northern Power Grid Strategic Incident"
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Description</label>
              <textarea
                rows={3}
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                placeholder="Operational scope, target stakeholders..."
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg"
              />
            </div>
            <div className="flex justify-end gap-3 text-xs font-semibold">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 bg-slate-100 rounded-lg">
                Cancel
              </button>
              <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
