import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { SAMPLE_CONTRACTS } from '../data/sampleContracts';

export default function UploadSection({ onUploadSuccess, onLoadSample, isProcessing }) {
  const [uploadError, setUploadError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

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
    },
    maxFiles: 1,
  });

  return (
    <div className="glass-panel p-6 mb-8 border border-slate-800 shadow-2xl relative overflow-hidden">
      {/* Background ambient light */}
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

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
            {isProcessing ? "Processing Document NLP Pipeline..." : "Upload Contract Document"}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mb-3">
            Drag and drop your <span className="text-indigo-300 font-medium">.PDF</span> or <span className="text-indigo-300 font-medium">.DOCX</span> contract here, or click to browse files
          </p>

          <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-slate-800/80 text-slate-400 border border-slate-700">
            PyMuPDF & python-docx Parsers · Max 50 MB
          </span>
        </div>

        {/* Quick Demo Contract Loader */}
        <div className="lg:w-80 flex flex-col justify-between bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <div>
            <div className="flex items-center gap-2 mb-2 text-indigo-400 font-semibold text-sm">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Instant Sample Contracts</span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Try ClauseGuard AI immediately with pre-loaded realistic legal agreements containing high-risk traps:
            </p>

            <div className="space-y-2.5">
              {SAMPLE_CONTRACTS.map((sample) => (
                <button
                  key={sample.id}
                  disabled={isProcessing}
                  onClick={() => onLoadSample(sample)}
                  className="w-full text-left p-2.5 rounded-xl bg-slate-800/50 hover:bg-indigo-950/40 border border-slate-700/60 hover:border-indigo-500/40 transition-all flex items-start gap-2.5 group"
                >
                  <FileText className="w-4 h-4 text-indigo-400 mt-0.5 group-hover:text-cyan-300 flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-slate-200 group-hover:text-cyan-200 truncate">
                      {sample.title}
                    </p>
                    <span className="text-[10px] text-slate-400">
                      Optimized for <strong className="text-slate-300">{sample.role}</strong> role
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>Module 1 Document Parser</span>
            <span className="text-emerald-400 flex items-center gap-1 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" /> Ready
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
  );
}
