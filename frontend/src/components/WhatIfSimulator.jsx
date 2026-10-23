import React, { useState } from 'react';
import { 
  HelpCircle, 
  Send, 
  Sparkles, 
  AlertTriangle, 
  FileText, 
  Loader2, 
  CheckCircle2, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import api from '../services/api';

const PRESET_SCENARIOS = [
  "What happens if I terminate early?",
  "What if I miss a payment or delivery deadline?",
  "What if the counterparty rejects deliverables?",
  "What are the consequences of an IP or confidentiality dispute?",
  "Can the client hire a competitor or can I work for another client?",
  "What happens if this agreement automatically renews?",
];

export default function WhatIfSimulator({ contractId, userRole }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (scenarioText) => {
    const textToSubmit = scenarioText || query;
    if (!textToSubmit.trim() || !contractId) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.runWhatIf(contractId, textToSubmit, userRole);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to analyze scenario.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="glass-panel p-5 border border-indigo-900/40 bg-gradient-to-r from-indigo-950/30 to-slate-900/50 rounded-2xl">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-300 flex-shrink-0 mt-0.5">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm mb-1">Module 6 · What-If Impact Scenario Simulator</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Query hypothetical disputes, termination events, or payment delays. ClauseGuard AI searches contract clauses, traces interconnected obligations, and outputs plain-language consequences grounded in verbatim evidence.
            </p>
          </div>
        </div>
      </div>

      {/* Query Console */}
      <div className="glass-panel p-6 border border-slate-800 bg-slate-900/60 rounded-2xl space-y-4 shadow-xl">
        
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Ask any contract scenario question (e.g. 'What happens if I terminate early?')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSubmit();
            }}
            className="flex-1 bg-slate-950/90 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400 transition-colors"
          />

          <button
            onClick={() => handleSubmit()}
            disabled={loading || !query.trim()}
            className="btn-primary text-sm px-5 py-3 whitespace-nowrap"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>Simulate</span>
                <Send className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Preset scenario chips */}
        <div>
          <span className="text-[11px] font-semibold text-slate-400 block mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Suggested Scenarios:
          </span>

          <div className="flex flex-wrap gap-2">
            {PRESET_SCENARIOS.map((preset, idx) => (
              <button
                key={idx}
                disabled={loading}
                onClick={() => {
                  setQuery(preset);
                  handleSubmit(preset);
                }}
                className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/60 hover:bg-indigo-950/60 border border-slate-700/70 hover:border-indigo-500/50 text-slate-300 hover:text-cyan-200 transition-colors text-left"
              >
                {preset}
              </button>
            ))}
          </div>
        </div>

      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Simulation Results */}
      {result && (
        <div className="glass-panel p-6 border border-slate-800 bg-slate-900/80 rounded-2xl space-y-6">
          
          {/* Answer Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div>
              <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider block mb-1">
                Scenario Result
              </span>
              <h4 className="text-base font-bold text-white">"{result.query}"</h4>
            </div>

            <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border self-start sm:self-auto ${
              result.risk_level === 'High' ? 'bg-red-500/20 text-red-300 border-red-500/40' :
              result.risk_level === 'Medium' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
              'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
            }`}>
              {result.risk_level} Scenario Risk
            </span>
          </div>

          {/* Plain Language Answer */}
          <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-900/50 text-slate-200 text-sm leading-relaxed">
            <strong className="text-cyan-300 block mb-1">Plain-Language Consequence Analysis:</strong>
            {result.answer}
          </div>

          {/* Identified Consequences List */}
          {result.consequences && result.consequences.length > 0 && (
            <div>
              <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Specific Contractual Consequences:
              </h5>

              <div className="space-y-2">
                {result.consequences.map((c, i) => (
                  <div key={i} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                    <span className="w-4 h-4 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center text-[10px] flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    <span className="leading-relaxed">{c}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Traced Relevant Clauses */}
          {result.relevant_clauses && result.relevant_clauses.length > 0 && (
            <div>
              <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                Governing Contract Clauses:
              </h5>

              <div className="space-y-3">
                {result.relevant_clauses.map((clause, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">
                          Clause #{clause.index + 1}
                        </span>
                        <span className="badge-category text-[10px]">{clause.category}</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        clause.risk_level === 'High' ? 'text-red-300 bg-red-950/50' :
                        clause.risk_level === 'Medium' ? 'text-amber-300 bg-amber-950/50' :
                        'text-emerald-300 bg-emerald-950/50'
                      }`}>
                        {clause.risk_level} Risk
                      </span>
                    </div>
                    <p className="font-mono text-slate-300 text-[11px] leading-relaxed">
                      {clause.cleaned_text || clause.raw_text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
