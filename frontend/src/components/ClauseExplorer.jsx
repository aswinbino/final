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
  Sparkles,
  Copy,
  Check,
  Scale,
  ArrowRightLeft,
  Info
} from 'lucide-react';

const CORE_CATEGORIES = [
  'All',
  'Payment Terms & Fees',
  'Termination & Cancellation',
  'Liability & Indemnification',
  'Confidentiality & Non-Disclosure',
  'Intellectual Property Rights (IP)',
  'Penalties & Liquidated Damages',
  'Renewal Terms & Extensions',
  'Dispute Resolution & Governing Law',
];

export default function ClauseExplorer({ clauses, selectedSeverity = 'All', activeRole = 'Freelancer / Contractor' }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [severityFilter, setSeverityFilter] = useState(selectedSeverity);
  const [selectedClauseEvidence, setSelectedClauseEvidence] = useState(null);
  const [copiedClauseId, setCopiedClauseId] = useState(null);

  const handleCopyProposal = (clauseId, text) => {
    navigator.clipboard.writeText(text);
    setCopiedClauseId(clauseId);
    setTimeout(() => setCopiedClauseId(null), 2500);
  };

  const filteredClauses = useMemo(() => {
    if (!clauses) return [];
    return clauses.filter((clause) => {
      // Category filter (match full or partial name)
      if (selectedCategory !== 'All') {
        const cat = (clause.category || '').toLowerCase();
        const sel = selectedCategory.toLowerCase();
        if (!cat.includes(sel.split(' ')[0]) && !sel.includes(cat.split(' ')[0])) {
          return false;
        }
      }
      // Severity filter
      if (severityFilter !== 'All') {
        const sev = (clause.risk_level || '').toUpperCase();
        const target = severityFilter.toUpperCase();
        if (!sev.includes(target) && !target.includes(sev)) {
          return false;
        }
      }
      // Search term
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const textMatch = (clause.verbatim_text || clause.raw_text || clause.cleaned_text || '').toLowerCase().includes(query);
        const explMatch = (clause.simple_explanation || '').toLowerCase().includes(query);
        const statMatch = (clause.legal_evidence || '').toLowerCase().includes(query);
        const catMatch = (clause.category || '').toLowerCase().includes(query);
        if (!textMatch && !explMatch && !statMatch && !catMatch) return false;
      }
      return true;
    });
  }, [clauses, selectedCategory, severityFilter, searchTerm]);

  return (
    <div className="space-y-6">
      
      {/* 6 Core Modules Banner Indicator */}
      <div className="glass-panel p-4 border border-indigo-900/50 bg-gradient-to-r from-indigo-950/40 to-slate-900/70 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <Scale className="w-5 h-5 text-cyan-400 flex-shrink-0" />
          <div>
            <span className="font-bold text-white">Modules 2, 3 & 4 · Explainable NLP & Actionable Mitigation</span>
            <p className="text-slate-400 text-[11px]">
              Every clause is classified across 8 legal provisions with plain-language summaries, statutory doctrines, and copyable counter-proposals.
            </p>
          </div>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono text-[11px] font-semibold flex-shrink-0">
          Personalized for {activeRole}
        </span>
      </div>

      {/* Search and Category Filters Bar */}
      <div className="glass-panel p-5 border border-slate-800 bg-slate-900/70 rounded-2xl space-y-4 shadow-xl">
        <div className="flex flex-col md:flex-row gap-3">
          
          {/* Keyword Search */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search clause text, simple explanations, statutory doctrines, or counter-proposals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          {/* Qualitative Severity Badging Filter Buttons */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            {['All', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => {
              const label = sev === 'All' ? 'All Severities' : sev === 'HIGH' ? 'HIGH RISK' : sev === 'MEDIUM' ? 'MEDIUM CAUTION' : 'LOW RISK';
              const isSelected = severityFilter.toUpperCase() === sev;
              return (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                    isSelected
                      ? sev === 'HIGH' ? 'bg-red-500/25 text-red-300 border border-red-500/60 shadow-lg shadow-red-500/10'
                      : sev === 'MEDIUM' ? 'bg-amber-500/25 text-amber-300 border border-amber-500/60 shadow-lg shadow-amber-500/10'
                      : sev === 'LOW' ? 'bg-emerald-500/25 text-emerald-300 border border-emerald-500/60 shadow-lg shadow-emerald-500/10'
                      : 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/50'
                      : 'bg-slate-800/40 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-transparent'
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>

        </div>

        {/* 8 Mandatory Category Pills */}
        <div className="pt-2 border-t border-slate-800/60">
          <div className="flex items-center gap-1.5 mb-2">
            <Filter className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              8 Core Legal Provisions:
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {CORE_CATEGORIES.map((cat) => {
              const isSelected = selectedCategory === cat;
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-[11px] font-medium transition-all ${
                    isSelected
                      ? 'bg-indigo-600 text-white font-bold shadow-md shadow-indigo-500/20'
                      : 'bg-slate-800/60 text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-700/60'
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Showing <strong className="text-white">{filteredClauses.length}</strong> of {clauses?.length || 0} extracted clauses</span>
        <span className="flex items-center gap-1.5 text-cyan-400 text-[11px] font-mono">
          <Sparkles className="w-3.5 h-3.5" /> Verbatim Provenance & Grounded Rationale
        </span>
      </div>

      {/* Clause Cards List */}
      <div className="space-y-5">
        {filteredClauses.length === 0 ? (
          <div className="glass-panel p-12 text-center border border-slate-800 bg-slate-900/30 rounded-2xl">
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
            const riskUpper = (clause.risk_level || 'LOW').toUpperCase();
            const isHigh = riskUpper.includes('HIGH');
            const isMed = riskUpper.includes('MED');

            const clauseId = clause.id || `CLAUSE-${(idx + 1).toString().padStart(3, '0')}`;
            const verbatimText = clause.verbatim_text || clause.raw_text || clause.cleaned_text || '';

            return (
              <div
                key={clauseId}
                className={`glass-panel p-6 border transition-all rounded-2xl shadow-xl relative overflow-hidden ${
                  isHigh 
                    ? 'border-red-900/60 bg-gradient-to-b from-red-950/20 to-slate-900/70 hover:border-red-500/60' 
                    : isMed 
                    ? 'border-amber-900/60 bg-gradient-to-b from-amber-950/20 to-slate-900/70 hover:border-amber-500/60' 
                    : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                }`}
              >
                {/* Clause Header Bar */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="font-mono text-xs px-2.5 py-1 rounded-md bg-slate-800 text-slate-200 border border-slate-700 font-bold">
                      {clauseId}
                    </span>

                    <span className="badge-category font-semibold text-xs">
                      {clause.category}
                    </span>

                    {clause.page_number && (
                      <span className="text-xs text-slate-400 font-mono px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/60">
                        Page {clause.page_number}
                      </span>
                    )}

                    {clause.related_clause_ids && clause.related_clause_ids.length > 0 && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-cyan-300 border border-indigo-500/40">
                        🔗 {clause.related_clause_ids.length} Linked in Risk Chain
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border ${
                      isHigh ? 'bg-red-500/20 text-red-300 border-red-500/50' : isMed ? 'bg-amber-500/20 text-amber-300 border-amber-500/50' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50'
                    }`}>
                      {isHigh ? 'HIGH RISK' : isMed ? 'MEDIUM CAUTION' : 'LOW RISK'}
                    </span>

                    <button
                      onClick={() => setSelectedClauseEvidence(clause)}
                      className="px-2.5 py-1 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                      title="Inspect verbatim evidence & grounding"
                    >
                      <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Inspect Grounding</span>
                    </button>
                  </div>
                </div>

                {/* Feature 1: Plain-Language Summary Box */}
                {clause.simple_explanation && (
                  <div className="mb-4 p-3.5 rounded-xl bg-indigo-950/30 border border-indigo-500/30 text-xs text-indigo-200 leading-relaxed flex items-start gap-2.5">
                    <Info className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <strong className="text-cyan-300 font-semibold block mb-0.5">
                        Simple Language Summary (Non-Legal Translation):
                      </strong>
                      <span>{clause.simple_explanation}</span>
                    </div>
                  </div>
                )}

                {/* Feature 1: Verbatim Source Excerpt */}
                <div className="mb-4">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1.5">
                    <span className="font-semibold uppercase tracking-wider">Verbatim Contract Excerpt (Original Text)</span>
                    <span className="font-mono text-slate-500">Exact Provenance · Page {clause.page_number || 1}</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 font-mono leading-relaxed max-h-36 overflow-y-auto">
                    {verbatimText}
                  </div>
                </div>

                {/* Feature 1: Statutory Evidence Grounding Citation */}
                {clause.legal_evidence && (
                  <div className="mb-4 p-3 rounded-xl bg-amber-950/25 border border-amber-500/30 text-xs text-amber-200 flex items-start gap-2.5">
                    <Scale className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <strong className="text-amber-300 font-semibold block mb-0.5">
                        Statutory Evidence & Legal Doctrine:
                      </strong>
                      <span className="font-mono text-amber-200 font-medium">{clause.legal_evidence}</span>
                      {clause.risk_reasoning && (
                        <p className="text-slate-300 text-[11px] mt-1">{clause.risk_reasoning}</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Feature 2: Mitigation Engine ("How Can It Be Changed?") */}
                {(isHigh || isMed) && clause.suggested_change && (
                  <div className="mt-4 p-4 rounded-xl bg-slate-950/90 border border-emerald-500/30 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                        <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Actionable Mitigation Engine · Suggested Counter-Proposal</span>
                      </div>
                      
                      <button
                        onClick={() => handleCopyProposal(clauseId, clause.suggested_change)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                          copiedClauseId === clauseId 
                            ? 'bg-emerald-500 text-slate-950 font-bold shadow-lg shadow-emerald-500/20' 
                            : 'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40'
                        }`}
                      >
                        {copiedClauseId === clauseId ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>Copied to Clipboard!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy Counter-Proposal</span>
                          </>
                        )}
                      </button>
                    </div>

                    <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-xs text-emerald-200 font-mono leading-relaxed">
                      "{clause.suggested_change}"
                    </div>
                  </div>
                )}

                {/* Feature 3: Role Priority Shift Explanation */}
                {clause.role_reasoning && (
                  <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center gap-2 text-xs text-slate-400">
                    <ArrowRightLeft className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                    <span>
                      <strong className="text-slate-300">Personalized Role Impact: </strong>
                      {clause.role_reasoning}
                    </span>
                  </div>
                )}

              </div>
            );
          })
        )}
      </div>

      {/* Verbatim Grounding Modal Drawer */}
      {selectedClauseEvidence && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel border border-slate-700 bg-slate-900 max-w-2xl w-full p-6 rounded-2xl shadow-2xl relative max-h-[85vh] overflow-y-auto">
            
            <div className="flex items-start justify-between mb-4 pb-3 border-b border-slate-800">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-lg text-white">Verbatim Evidence Grounding</span>
                  <span className="badge-category">{selectedClauseEvidence.category}</span>
                </div>
                <p className="text-xs text-slate-400 font-mono">
                  {selectedClauseEvidence.id} · Page {selectedClauseEvidence.page_number || 1} · Module 3 Statutory Grounding
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
                Full Verbatim Clause
              </h4>
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono leading-relaxed max-h-48 overflow-y-auto">
                {selectedClauseEvidence.verbatim_text || selectedClauseEvidence.raw_text}
              </div>
            </div>

            {/* Statutory Law Authority */}
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <Scale className="w-3.5 h-3.5 text-amber-400" />
                Statutory Authority & Grounded Precedent
              </h4>
              <div className="p-3.5 rounded-xl bg-slate-950 border border-amber-500/30 text-xs text-amber-200 font-mono">
                {selectedClauseEvidence.legal_evidence}
              </div>
            </div>

            {/* Mitigation Suggestion */}
            {selectedClauseEvidence.suggested_change && (
              <div className="mb-4">
                <h4 className="text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider flex items-center gap-1.5 text-emerald-400">
                  <Sparkles className="w-3.5 h-3.5" />
                  Proposed Counter-Proposal Clause
                </h4>
                <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-500/30 text-xs text-emerald-200 font-mono">
                  "{selectedClauseEvidence.suggested_change}"
                </div>
              </div>
            )}

            <div className="mt-6 pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedClauseEvidence(null)}
                className="btn-secondary text-xs px-4 py-2"
              >
                Close Grounding Inspector
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
