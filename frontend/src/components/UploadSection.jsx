import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Sparkles,
  Layers,
  FileCheck,
  Shield,
  ArrowRight
} from 'lucide-react';
import { SAMPLE_CONTRACTS } from '../data/sampleContracts';

export default function UploadSection({ 
  onUploadSuccess, 
  onLoadSample, 
  isProcessing,
  activeContract,
  totalClauses,
  userRole,
  onRoleChange
}) {
  const [uploadError, setUploadError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    setUploadError(null);
    if (rejectedFiles && rejectedFiles.length > 0) {
      setUploadError("Please upload a valid .pdf, .docx, or .doc contract document.");
      return;
    }
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      try {
        await onUploadSuccess(file);
      } catch (err) {
        setUploadError(err.response?.data?.detail || err.message || "Upload failed");
      }
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  return (
    <div className="space-y-6 mb-8">
      
      {/* Module 1 Document Ingestion & Confirmation Panel */}
      {activeContract && (
        <div className="glass-panel p-5 border border-cyan-500/30 bg-gradient-to-r from-slate-900/90 via-indigo-950/40 to-slate-900/90 rounded-2xl shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-32 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 flex-shrink-0 shadow-lg shadow-cyan-500/10">
                <FileCheck className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-semibold">
                    Module 1 Verified
                  </span>
                  <span className="text-xs text-slate-400 font-mono">ID: {activeContract.id}</span>
                </div>
                <h3 className="text-base font-bold text-white truncate max-w-md mt-0.5">
                  {activeContract.original_name || activeContract.filename}
                </h3>
              </div>
            </div>

            {/* Ingestion Status Metadata Counters */}
            <div className="flex items-center gap-4 flex-wrap bg-slate-950/60 border border-slate-800/80 px-4 py-2.5 rounded-xl">
              <div>
                <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Total Pages</span>
                <span className="text-sm font-bold text-white font-mono">{activeContract.total_pages || activeContract.page_count || 1}</span>
              </div>
              <div className="w-px h-6 bg-slate-800" />
              <div>
                <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Clauses Extracted</span>
                <span className="text-sm font-bold text-cyan-300 font-mono">{totalClauses || activeContract.clause_count || 0}</span>
              </div>
              <div className="w-px h-6 bg-slate-800" />
              <div>
                <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Processing Status</span>
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 font-mono">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {activeContract.status || "NLP Pipeline Complete"}
                </span>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Main Upload Area & Instant Demo Contract Loader */}
      <div className="glass-panel p-6 border border-slate-800 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row gap-6 items-stretch">
          
          {/* Dropzone container */}
          <div 
            {...getRootProps()}
            className={`flex-1 border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px] ${
              isDragActive 
                ? 'border-cyan-400 bg-cyan-500/10 shadow-lg shadow-cyan-500/10' 
                : 'border-slate-700/80 hover:border-indigo-400 bg-slate-900/40 hover:bg-slate-900/70'
            }`}
          >
            <input {...getInputProps()} />

            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4 text-cyan-400 group-hover:scale-110 transition-transform">
              {isProcessing ? (
                <Loader2 className="w-7 h-7 animate-spin text-indigo-400" />
              ) : (
                <UploadCloud className="w-7 h-7" />
              )}
            </div>

            <h3 className="font-semibold text-lg text-slate-100 mb-1">
              {isProcessing ? "Processing Document NLP Pipeline..." : "Upload Contract Document (PDF or DOCX)"}
            </h3>
            <p className="text-xs text-slate-400 max-w-sm mb-3">
              Drag & drop your legal contract here, or click to browse files.
            </p>

            <span className="text-[11px] font-mono px-3 py-1 rounded-full bg-slate-800/80 text-cyan-300 border border-slate-700 flex items-center gap-1.5">
              <span>PyMuPDF & python-docx Parsers</span>
              <span>·</span>
              <span>8 Core Legal Provisions</span>
            </span>
          </div>

          {/* Quick Demo Contract Loader */}
          <div className="lg:w-96 flex flex-col justify-between bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>Instant Sample Contracts</span>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">4 Roles Available</span>
              </div>
              <p className="text-xs text-slate-400 mb-3">
                Experience dynamic role re-weighting and cross-clause risk chains immediately:
              </p>

              <div className="space-y-2">
                {SAMPLE_CONTRACTS.map((sample) => (
                  <button
                    key={sample.id}
                    disabled={isProcessing}
                    onClick={() => onLoadSample(sample)}
                    className="w-full text-left p-2.5 rounded-xl bg-slate-800/50 hover:bg-indigo-950/40 border border-slate-700/60 hover:border-indigo-500/40 transition-all flex items-start gap-2.5 group"
                  >
                    <FileText className="w-4 h-4 text-indigo-400 mt-0.5 group-hover:text-cyan-300 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-semibold text-slate-200 group-hover:text-cyan-200 truncate">
                        {sample.title}
                      </p>
                      <div className="flex items-center justify-between mt-0.5">
                        <span className="text-[10px] text-cyan-400 font-medium font-mono">
                          {sample.role}
                        </span>
                        <span className="text-[10px] text-slate-500 group-hover:text-slate-300 flex items-center gap-0.5">
                          Load <ArrowRight className="w-2.5 h-2.5" />
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
              <span>Module 1 · Upload Status</span>
              <span className="text-emerald-400 flex items-center gap-1 font-medium font-mono text-[10px]">
                <CheckCircle2 className="w-3 h-3" /> Ready
              </span>
            </div>
          </div>

        </div>

        {uploadError && (
          <div className="mt-4 p-3 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

    </div>
  );
}
