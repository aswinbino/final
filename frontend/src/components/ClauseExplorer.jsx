import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  AlertTriangle, 
  CheckCircle2, 
  ExternalLink, 
  BookOpen, 
  FileText,
  Shield,
  Layers,
  Sparkles
} from 'lucide-react';

const CATEGORIES = [
  'All',
  'Payment',
  'Termination',
  'Liability',
  'Confidentiality',
  'IP',
  'Penalties',
  'Renewal',
  'Dispute Resolution',
  'Obligations',
  'General',
];

export default function ClauseExplorer({ clauses, selectedSeverity = 'All' }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [severityFilter, setSeverityFilter] = useState(selectedSeverity);
  const [selectedClauseEvidence, setSelectedClauseEvidence] = useState(null);

  const filteredClauses = useMemo(() => {
    if (!clauses) return [];
    return clauses.filter((clause) => {
      // Category filter
      if (selectedCategory !== 'All' && clause.category !== selectedCategory) {
        return false;
      }
      // Severity filter
      if (severityFilter !== 'All' && clause.risk_level !== severityFilter) {
        return false;
      }
      // Search term
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const textMatch = clause.raw_text?.toLowerCase().includes(query) || clause.cleaned_text?.toLowerCase().includes(query);
        const reasonMatch = clause.risk_reasoning?.toLowerCase().includes(query);
        const categoryMatch = clause.category?.toLowerCase().includes(query);
        if (!textMatch && !reasonMatch && !categoryMatch) return false;
      }
      return true;
    });
  }, [clauses, selectedCategory, severityFilter, searchTerm]);

  return (
    <div className="space-y-6">
      
      {/* Search and Filters Bar */}
      <div className="glass-panel p-4 border border-slate-800 bg-slate-900/60 rounded-xl space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          
          {/* Keyword Search */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search clause text, legal reasons, or risk triggers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          {/* Severity filter buttons */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            {['All', 'High', 'Medium', 'Low'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  severityFilter === sev
                    ? sev === 'High' ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                    : sev === 'Medium' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : sev === 'Low' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40'
                    : 'bg-slate-800/40 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>

        </div>

        {/* Category Pill Filters */}
        <div className="flex items-center gap-1.5 flex-wrap pt-1 border-t border-slate-800/60">
          <span className="text-[11px] text-slate-500 mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Category:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                selectedCategory === cat
                  ? 'bg-indigo-500 text-white font-semibold'
                  : 'bg-slate-800/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Showing <strong className="text-slate-200">{filteredClauses.length}</strong> of {clauses?.length || 0} extracted clauses</span>
        <span className="flex items-center gap-1.5 text-cyan-400 text-[11px]">
          <Sparkles className="w-3 h-3" /> All risks backed by Module 7 Verbatim Evidence Grounding
        </span>
      </div>

      {/* Clause Cards List */}
      <div className="space-y-4">
        {filteredClauses.length === 0 ? (
          <div className="glass-panel p-12 text-center border border-slate-800 bg-slate-900/30">
            <FileText className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="text-slate-400 text-sm">No clauses matched the selected filters.</p>
            <button 
              onClick={() => { setSelectedCategory('All'); setSeverityFilter('All'); setSearchTerm(''); }}
              className="mt-3 text-xs text-cyan-400 hover:underline"
            >
              Reset all filters
            </button>
          </div>
        ) : (
          filteredClauses.map((clause, idx) => {
            const isHigh = clause.risk_level === 'High';
            const isMed = clause.risk_level === 'Medium';

            return (
              <div
                key={clause.id || idx}
                className={`glass-panel p-5 border transition-all rounded-xl ${
                  isHigh 
                    ? 'border-red-900/50 bg-red-950/10 hover:border-red-500/50' 
                    : isMed 
                    ? 'border-amber-900/50 bg-amber-950/10 hover:border-amber-500/50' 
                    : 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
                }`}
              >
                {/* Clause Header */}
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                      Clause #{clause.index + 1}
                    </span>

                    <span className="badge-category">
                      {clause.category}
                    </span>

                    {clause.page_number && (
                      <span className="text-[11px] text-slate-500">
                        Page {clause.page_number}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={
                      isHigh ? 'badge-risk-high' : isMed ? 'badge-risk-medium' : 'badge-risk-low'
                    }>
                      {clause.risk_level} Risk
                    </span>

                    <button
                      onClick={() => setSelectedClauseEvidence(clause)}
                      className="px-2.5 py-1 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                      title="Inspect verbatim evidence (Module 7)"
                    >
                      <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Inspect Evidence</span>
                    </button>
                  </div>
                </div>

                {/* Clause Body Text */}
                <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 mb-3 text-xs text-slate-200 leading-relaxed font-mono">
                  {clause.cleaned_text || clause.raw_text}
                </div>

                {/* AI Risk Reasoning */}
                {clause.risk_reasoning && (
                  <div className="flex items-start gap-2 text-xs">
                    <Shield className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${
                      isHigh ? 'text-red-400' : isMed ? 'text-amber-400' : 'text-emerald-400'
                    }`} />
                    <span className="text-slate-400">
                      <strong className="text-slate-300">AI Assessment: </strong>
                      {clause.risk_reasoning}
                    </span>
                  </div>
                )}

                {/* Direct Verbatim Evidence Snippets */}
                {clause.risks && clause.risks.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800/60 flex flex-wrap gap-2">
                    {clause.risks.map((r, rIdx) => (
                      <div 
                        key={rIdx}
                        className="text-[11px] px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1.5"
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          r.severity === 'High' ? 'bg-red-400' : 'bg-amber-400'
                        }`} />
                        <span className="font-semibold text-slate-200">{r.risk_type}:</span>
                        <span className="text-slate-400 italic">"{r.evidence_text}"</span>
                      </div>
                    ))}
                  </div>
                )}

              </div>
            );
          })
        )}
      </div>

      {/* Module 7: Verbatim Evidence Modal Drawer */}
      {selectedClauseEvidence && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel border border-slate-700 bg-slate-900 max-w-2xl w-full p-6 rounded-2xl shadow-2xl relative max-h-[85vh] overflow-y-auto">
            
            <div className="flex items-start justify-between mb-4 pb-3 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-lg text-white">Verbatim Evidence Grounding</span>
                  <span className="badge-category">{selectedClauseEvidence.category}</span>
                </div>
                <p className="text-xs text-slate-400">
                  Clause #{selectedClauseEvidence.index + 1} · Page {selectedClauseEvidence.page_number || 1} · Module 7 Explainable AI
                </p>
              </div>

              <button
                onClick={() => setSelectedClauseEvidence(null)}
                className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold"
              >
                ✕
              </button>
            </div>

            {/* Complete Raw Text */}
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                Full Clause Text
              </h4>
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono leading-relaxed max-h-48 overflow-y-auto">
                {selectedClauseEvidence.raw_text}
              </div>
            </div>

            {/* Extracted Evidence Snippets */}
            <div>
              <h4 className="text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Detected Unfavorable Conditions (Verbatim Proof)
              </h4>

              {selectedClauseEvidence.risks && selectedClauseEvidence.risks.length > 0 ? (
                <div className="space-y-3">
                  {selectedClauseEvidence.risks.map((risk, i) => (
                    <div 
                      key={i}
                      className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200">{risk.risk_type}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          risk.severity === 'High' ? 'bg-red-500/20 text-red-300' : 'bg-amber-500/20 text-amber-300'
                        }`}>
                          {risk.severity} Severity
                        </span>
                      </div>
                      <p className="text-slate-400 text-[11px]">{risk.description}</p>
                      <div className="p-2 rounded bg-indigo-950/30 border border-indigo-900/50 text-indigo-300 font-mono text-[11px]">
                        <strong>Verbatim Quote: </strong>"{risk.evidence_text}"
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-slate-950/60 text-xs text-slate-400 text-center">
                  No critical risk pattern violations detected in this clause. Standard commercial terms.
                </div>
              )}
            </div>

            <div className="mt-6 pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedClauseEvidence(null)}
                className="btn-secondary text-xs px-4 py-2"
              >
                Close Inspector
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
