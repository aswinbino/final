import React from 'react';
import { 
  GitFork, 
  AlertTriangle, 
  ArrowRight, 
  Layers, 
  ShieldAlert, 
  Info,
  CheckCircle2,
  Tag,
  Link2,
  Sparkles
} from 'lucide-react';

export default function RiskChainsView({ riskChains, clauses }) {
  if (!riskChains || riskChains.length === 0) {
    return (
      <div className="glass-panel p-12 text-center border border-slate-800 bg-slate-900/40 rounded-2xl">
        <GitFork className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-200 mb-1">No Cascading Risk Chains Detected</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          The clauses in this contract appear largely modular without cascading domino triggers (e.g. delivery delay triggering daily penalties, which trigger fee withholding, escalating into immediate contract termination).
        </p>
      </div>
    );
  }

  // Map clause ID / code to clause details
  const clauseMap = (clauses || []).reduce((acc, c) => {
    acc[c.id] = c;
    if (c.clause_code) acc[c.clause_code] = c;
    return acc;
  }, {});

  const getLinkBasisBadge = (basis) => {
    switch (basis) {
      case 'Cross-Reference':
        return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/40';
      case 'Shared Defined Term':
        return 'bg-purple-500/15 text-purple-300 border-purple-500/40';
      default:
        return 'bg-indigo-500/15 text-indigo-300 border-indigo-500/40';
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Module 6 Overview Banner */}
      <div className="glass-panel p-5 border border-indigo-900/50 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-slate-900/80 rounded-2xl">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-300 flex-shrink-0 mt-0.5 shadow-lg shadow-indigo-500/10">
            <GitFork className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <h3 className="font-bold text-white text-base">
                Module 6 · Cross-Clause Relationship & Interconnected Risk Chains
              </h3>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-mono">
                {riskChains.length} Cascades Identified
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
              Traditional contract reviews evaluate clauses in isolation. ClauseGuard's <strong>Cascading Risk Engine</strong> traces multi-clause domino effects where separate terms combine to amplify exposure. Links are mapped across 
              <span className="text-cyan-300 font-medium"> Explicit Cross-References</span>, 
              <span className="text-purple-300 font-medium"> Shared Defined Terms</span>, and 
              <span className="text-indigo-300 font-medium"> Semantic Candidates (FAISS)</span>.
            </p>
          </div>
        </div>
      </div>

      {/* Chain Cards */}
      <div className="space-y-6">
        {riskChains.map((chain, idx) => {
          const isHigh = (chain.combined_risk || 'HIGH').toUpperCase() === 'HIGH';
          const linkBasis = chain.link_basis || 'Cross-Reference';

          return (
            <div 
              key={chain.chain_id || idx}
              className={`glass-panel p-6 border rounded-2xl relative overflow-hidden transition-all shadow-xl ${
                isHigh 
                  ? 'border-red-900/60 bg-gradient-to-b from-red-950/15 via-slate-900/70 to-slate-900/90 hover:border-red-500/50' 
                  : 'border-amber-900/60 bg-gradient-to-b from-amber-950/15 via-slate-900/70 to-slate-900/90 hover:border-amber-500/50'
              }`}
            >
              {/* Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 text-xs font-mono font-bold">
                    {chain.chain_id || `CHAIN-${idx + 1}`}
                  </span>
                  <h4 className="font-bold text-base text-white">
                    {chain.title || chain.description}
                  </h4>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  {/* Link Basis Tag */}
                  <span className={`text-[11px] font-mono px-2.5 py-1 rounded-lg border flex items-center gap-1 font-semibold ${getLinkBasisBadge(linkBasis)}`}>
                    <Link2 className="w-3 h-3" />
                    <span>Basis: {linkBasis}</span>
                  </span>

                  {/* Compounded Risk Badge */}
                  <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border ${
                    isHigh ? 'bg-red-500/20 text-red-300 border-red-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  }`}>
                    {chain.combined_risk || 'HIGH'} Cascading Risk
                  </span>
                </div>
              </div>

              {/* Chain Rationale / Description */}
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 mb-5 text-xs text-slate-300 leading-relaxed flex items-start gap-3">
                <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${isHigh ? 'text-red-400' : 'text-amber-400'}`} />
                <div>
                  <strong className="text-white block mb-0.5">Cascading Trigger Explanation: </strong>
                  {chain.description}
                </div>
              </div>

              {/* Step Sequence Flow Rendering */}
              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-3 font-mono">
                  Cascading Chain Sequence ({chain.sequence?.length || (chain.clauses?.length || 0)} Trigger Steps):
                </span>

                <div className="space-y-3">
                  {(chain.sequence || []).map((stepText, sIdx) => {
                    const isLast = sIdx === (chain.sequence.length - 1);
                    return (
                      <div key={sIdx} className="flex items-start gap-3 relative">
                        {/* Step Number Circle */}
                        <div className={`w-7 h-7 rounded-full flex items-center justify-center font-mono text-xs font-bold flex-shrink-0 z-10 ${
                          sIdx === 0 ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20' :
                          isLast ? 'bg-red-500 text-white shadow-md shadow-red-500/20' :
                          'bg-indigo-600 text-white'
                        }`}>
                          {sIdx + 1}
                        </div>

                        {/* Connecting Line */}
                        {!isLast && (
                          <div className="absolute left-3.5 top-7 bottom-0 w-0.5 bg-slate-800 -mb-3 z-0" />
                        )}

                        {/* Step Card Content */}
                        <div className="flex-1 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-colors">
                          <p className="text-xs font-mono font-medium text-slate-200">
                            {stepText}
                          </p>
                        </div>
                      </div>
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
