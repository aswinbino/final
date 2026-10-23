import React from 'react';
import { 
  GitFork, 
  AlertTriangle, 
  ArrowRight, 
  Layers, 
  ShieldAlert, 
  Info,
  CheckCircle2
} from 'lucide-react';

export default function RiskChainsView({ riskChains, clauses }) {
  if (!riskChains || riskChains.length === 0) {
    return (
      <div className="glass-panel p-12 text-center border border-slate-800 bg-slate-900/40 rounded-2xl">
        <GitFork className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-200 mb-1">No Compounding Risk Chains Detected</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          The clauses in this contract appear largely modular without cascading legal dependency traps (such as Payment default triggering immediate liquidated damages + unilateral termination).
        </p>
      </div>
    );
  }

  // Map clause ID to clause details
  const clauseMap = (clauses || []).reduce((acc, c) => {
    acc[c.id] = c;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      
      {/* Module Overview Banner */}
      <div className="glass-panel p-5 border border-indigo-900/40 bg-gradient-to-r from-indigo-950/30 to-slate-900/50 rounded-2xl">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-300 flex-shrink-0 mt-0.5">
            <GitFork className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-bold text-white text-sm">Module 5 · Compounding Legal Risk Chains</h3>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {riskChains.length} Chains Identified
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Standard contract reviews analyze clauses in isolation. ClauseGuard's <strong>Risk Chain Engine</strong> traces multi-clause domino effects where separate obligations (e.g. strict payment deadlines, liquidated damages, and unilateral termination) combine to amplify total liability exposure.
            </p>
          </div>
        </div>
      </div>

      {/* Chain Cards */}
      <div className="space-y-5">
        {riskChains.map((chain, idx) => {
          const isHigh = chain.combined_risk === 'High';

          return (
            <div 
              key={chain.chain_id || idx}
              className={`glass-panel p-6 border rounded-2xl relative overflow-hidden transition-all ${
                isHigh 
                  ? 'border-red-900/60 bg-red-950/15 hover:border-red-500/50' 
                  : 'border-amber-900/60 bg-amber-950/15 hover:border-amber-500/50'
              }`}
            >
              {/* Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <div className="flex items-center gap-2.5">
                  <span className="w-6 h-6 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center text-xs font-mono font-bold">
                    #{idx + 1}
                  </span>
                  <h4 className="font-bold text-base text-slate-100">{chain.title}</h4>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider border ${
                    isHigh ? 'bg-red-500/20 text-red-300 border-red-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  }`}>
                    {chain.combined_risk} Compounded Risk
                  </span>
                </div>
              </div>

              {/* Chain Description */}
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 mb-5 text-xs text-slate-300 leading-relaxed flex items-start gap-2.5">
                <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${isHigh ? 'text-red-400' : 'text-amber-400'}`} />
                <div>
                  <strong className="text-white">Cascading Impact: </strong>
                  {chain.description}
                </div>
              </div>

              {/* Linked Nodes Flow */}
              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-3">
                  Interconnected Clauses in this Chain:
                </span>

                <div className="flex flex-col md:flex-row items-stretch md:items-center gap-2.5">
                  {chain.clauses.map((clauseId, cIdx) => {
                    const clause = clauseMap[clauseId] || { 
                      id: clauseId, 
                      category: 'Linked Clause', 
                      index: cIdx, 
                      risk_level: 'High' 
                    };

                    return (
                      <React.Fragment key={clauseId}>
                        <div className="flex-1 p-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors">
                          <div className="flex items-center justify-between gap-2 mb-1.5">
                            <span className="badge-category text-[10px]">
                              {clause.category}
                            </span>
                            <span className="text-[10px] font-mono text-slate-500">
                              Clause #{clause.index !== undefined ? clause.index + 1 : '—'}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 line-clamp-2 font-mono">
                            {clause.cleaned_text || clause.raw_text || "Referenced contractual obligation"}
                          </p>
                        </div>

                        {cIdx < chain.clauses.length - 1 && (
                          <div className="flex items-center justify-center text-slate-600 py-1 md:py-0">
                            <ArrowRight className="w-4 h-4 transform rotate-90 md:rotate-0 text-indigo-400" />
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
