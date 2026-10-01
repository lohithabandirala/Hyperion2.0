"use client";

import { useEffect, useState } from "react";
import { getProjects, deleteProject } from "@/services/api";
import Link from "next/link";

interface Project {
  id: number;
  title: string;
  description?: string;
  created_at: string;
}

export default function HistoryPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProjects = async () => {
    try {
      const res = await getProjects();
      setProjects(res.data);
    } catch (err) {
      console.error("Error fetching history:", err);
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
        console.error("Error fetching history:", err);
        if (!ignore) {
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this project history?")) {
      await deleteProject(id);
      loadProjects();
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto w-full space-y-6">
      <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Transformation History</h1>
          <p className="text-xs text-slate-500 mt-1">Audit log and records of previous content transformations and published outputs.</p>
        </div>
        <Link
          href="/"
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-4 py-2.5 rounded-lg shadow-sm"
        >
          + New Transformation
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading history records...</div>
        ) : projects.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm space-y-2">
            <div>No previous transformations found.</div>
            <Link href="/" className="text-blue-600 font-bold hover:underline inline-block">
              Start your first transformation
            </Link>
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider">
              <tr>
                <th className="p-4">Project ID</th>
                <th className="p-4">Title &amp; Scope</th>
                <th className="p-4">Created At</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {projects.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition">
                  <td className="p-4 font-mono font-bold text-slate-500">PRJ-{p.id}</td>
                  <td className="p-4">
                    <div className="font-bold text-slate-900">{p.title}</div>
                    <div className="text-[11px] text-slate-400">{p.description || "Automated transformation pipeline"}</div>
                  </td>
                  <td className="p-4 text-slate-500 font-mono">
                    {new Date(p.created_at).toLocaleString()}
                  </td>
                  <td className="p-4 text-right space-x-2">
                    <Link
                      href="/"
                      className="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded font-bold"
                    >
                      Reopen
                    </Link>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 rounded font-bold"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
