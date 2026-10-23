import React, { useState } from 'react';
import { 
  GitCompare, 
  PlusCircle, 
  MinusCircle, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight,
  TrendingUp,
  FileText,
  Loader2
} from 'lucide-react';
import api from '../services/api';

export default function ContractComparator({ contracts = [], currentContractId }) {
  const [contractAId, setContractAId] = useState(currentContractId || (contracts[0]?.id || ''));
  const [contractBId, setContractBId] = useState(contracts[1]?.id || (contracts[0]?.id || ''));
  const [loading, setLoading] = useState(false);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');

  const handleRunCompare = async () => {
    if (!contractAId || !contractBId) {
      setError("Please select both Contract Version A and Contract Version B.");
      return;
    }
    if (contractAId === contractBId) {
      setError("Please select two different contract files to compare revisions.");
      return;
    }

    setLoading(true);
    setError(null);
    setComparisonResult(null);

    try {
      const data = await api.compareContracts(contractAId, contractBId);
      setComparisonResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to compare contracts.");
    } finally {
      setLoading(false);
    }
  };

  const filteredDiffs = (comparisonResult?.diffs || []).filter((diff) => {
    if (activeFilter === 'added') return diff.change_type === 'added';
    if (activeFilter === 'removed') return diff.change_type === 'removed';
    if (activeFilter === 'modified') return diff.change_type === 'modified';
    if (activeFilter === 'risk_increased') return diff.risk_delta === 'increased';
    return true;
  });

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="glass-panel p-5 border border-indigo-900/40 bg-gradient-to-r from-indigo-950/30 to-slate-900/50 rounded-2xl">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-300 flex-shrink-0 mt-0.5">
            <GitCompare className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm mb-1">Module 9 · Side-by-Side Contract Revision Comparator</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Detect modified covenants, newly injected clauses, removed protections, and escalations in legal risk between contract drafts or counter-offers.
            </p>
          </div>
        </div>
      </div>

      {/* Contract Version Selectors */}
      <div className="glass-panel p-6 border border-slate-800 bg-slate-900/60 rounded-2xl shadow-xl space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Version A */}
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider">
              Base Version (Contract A)
            </label>
            <select
              value={contractAId}
              onChange={(e) => setContractAId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">Select Base Contract</option>
              {contracts.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.original_name || c.filename} ({c.id.slice(0, 8)})
                </option>
              ))}
            </select>
          </div>

          {/* Version B */}
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider">
              Revised Version (Contract B)
            </label>
            <select
              value={contractBId}
              onChange={(e) => setContractBId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="">Select Revised Contract</option>
              {contracts.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.original_name || c.filename} ({c.id.slice(0, 8)})
                </option>
              ))}
            </select>
          </div>

        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={handleRunCompare}
            disabled={loading || !contractAId || !contractBId}
            className="btn-primary text-xs px-5 py-2.5"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Compare Revisions</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Comparison Results */}
      {comparisonResult && (
        <div className="space-y-6">
          
          {/* Summary Banner */}
          <div className="glass-panel p-5 border border-slate-800 bg-slate-900/80 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider block mb-1">
                Executive Comparison Summary
              </span>
              <p className="text-xs text-slate-200 font-medium leading-relaxed">
                {comparisonResult.risk_summary}
              </p>
            </div>

            {/* Quick Stats */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 font-mono text-xs font-semibold">
                +{comparisonResult.added} Added
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-red-500/15 border border-red-500/30 text-red-300 font-mono text-xs font-semibold">
                -{comparisonResult.removed} Removed
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 font-mono text-xs font-semibold">
                ~{comparisonResult.modified} Modified
              </span>
            </div>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-medium">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeFilter === 'all' ? 'bg-indigo-600 text-white font-semibold' : 'bg-slate-800/60 text-slate-400 hover:text-white'
              }`}
            >
              All Diffs ({comparisonResult.diffs.length})
            </button>
            <button
              onClick={() => setActiveFilter('risk_increased')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeFilter === 'risk_increased' ? 'bg-red-600 text-white font-semibold' : 'bg-slate-800/60 text-slate-400 hover:text-white'
              }`}
            >
              ⚠️ Increased Risk Only
            </button>
            <button
              onClick={() => setActiveFilter('added')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeFilter === 'added' ? 'bg-emerald-600 text-white font-semibold' : 'bg-slate-800/60 text-slate-400 hover:text-white'
              }`}
            >
              Added Clauses
            </button>
            <button
              onClick={() => setActiveFilter('modified')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeFilter === 'modified' ? 'bg-amber-600 text-white font-semibold' : 'bg-slate-800/60 text-slate-400 hover:text-white'
              }`}
            >
              Modified Terms
            </button>
          </div>

          {/* Side-by-side Diff Cards */}
          <div className="space-y-4">
            {filteredDiffs.map((diff, idx) => {
              const isAdded = diff.change_type === 'added';
              const isRemoved = diff.change_type === 'removed';
              const isModified = diff.change_type === 'modified';
              const isEscalated = diff.risk_delta === 'increased';

              return (
                <div 
                  key={idx}
                  className={`glass-panel p-5 border rounded-2xl transition-all ${
                    isEscalated ? 'border-red-600/60 bg-red-950/20 shadow-lg shadow-red-950/20' :
                    isAdded ? 'border-emerald-600/40 bg-emerald-950/10' :
                    isRemoved ? 'border-red-800/40 bg-red-950/10' :
                    'border-slate-800 bg-slate-900/60'
                  }`}
                >
                  {/* Diff Header */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="badge-category text-[10px]">{diff.category}</span>
                      <span className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        isAdded ? 'bg-emerald-500/20 text-emerald-300' :
                        isRemoved ? 'bg-red-500/20 text-red-300' :
                        'bg-amber-500/20 text-amber-300'
                      }`}>
                        {diff.change_type}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {isEscalated && (
                        <span className="text-[11px] font-bold text-red-400 px-2.5 py-0.5 rounded-full bg-red-950 border border-red-500/40 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" /> Risk Escalated in B
                        </span>
                      )}
                      {diff.risk_level_a && (
                        <span className="text-[10px] font-mono text-slate-400">
                          A: {diff.risk_level_a} → B: {diff.risk_level_b || 'None'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Side-by-Side Content */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                    
                    {/* Contract A Text */}
                    <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                        Version A:
                      </span>
                      {diff.text_a ? (
                        <p className="leading-relaxed">{diff.text_a}</p>
                      ) : (
                        <p className="text-slate-600 italic">— Clause not present in Version A —</p>
                      )}
                    </div>

                    {/* Contract B Text */}
                    <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300">
                      <span className="text-[10px] uppercase font-bold text-cyan-500 block mb-1">
                        Version B:
                      </span>
                      {diff.text_b ? (
                        <p className="leading-relaxed">{diff.text_b}</p>
                      ) : (
                        <p className="text-red-400 italic">— Clause deleted in Version B —</p>
                      )}
                    </div>

                  </div>

                </div>
              );
            })}
          </div>

        </div>
      )}

    </div>
  );
}
