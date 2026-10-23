import React, { useState } from 'react';
import { 
  Calendar, 
  Clock, 
  DollarSign, 
  FileCheck, 
  User, 
  Filter, 
  AlertCircle,
  ExternalLink
} from 'lucide-react';

const OBLIGATION_TYPES = [
  'All',
  'Payment',
  'Notice Period',
  'Renewal Deadline',
  'Delivery Deadline',
  'Financial Amount',
];

export default function ObligationsTable({ obligations }) {
  const [selectedType, setSelectedType] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  if (!obligations || obligations.length === 0) {
    return (
      <div className="glass-panel p-12 text-center border border-slate-800 bg-slate-900/40 rounded-2xl">
        <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-200 mb-1">No Deadlines or Obligations Extracted</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          No explicit payment deadlines, notice timelines, or recurring calendar commitments were identified in the parsed clauses.
        </p>
      </div>
    );
  }

  const filteredObligations = obligations.filter((ob) => {
    if (selectedType !== 'All' && ob.obligation_type !== selectedType) return false;
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      return (
        ob.description?.toLowerCase().includes(q) ||
        ob.party?.toLowerCase().includes(q) ||
        ob.deadline?.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const getTypeIcon = (type) => {
    switch (type) {
      case 'Payment':
      case 'Financial Amount':
        return <DollarSign className="w-3.5 h-3.5 text-emerald-400" />;
      case 'Notice Period':
      case 'Renewal Deadline':
      case 'Delivery Deadline':
        return <Clock className="w-3.5 h-3.5 text-cyan-400" />;
      default:
        return <Calendar className="w-3.5 h-3.5 text-indigo-400" />;
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="glass-panel p-5 border border-indigo-900/40 bg-gradient-to-r from-indigo-950/30 to-slate-900/50 rounded-2xl">
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-300 flex-shrink-0 mt-0.5">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-sm mb-1">Module 8 · Obligations, Notice Periods & Deadlines Tracker</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Consolidated register of all operational commitments, payment deadlines, renewal cutoffs, and notice requirements extracted from contractual covenants.
            </p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 border border-slate-800 bg-slate-900/60 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Type pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] text-slate-500 mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Type:
          </span>
          {OBLIGATION_TYPES.map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                selectedType === type
                  ? 'bg-indigo-500 text-white font-semibold'
                  : 'bg-slate-800/50 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Filter obligations..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full md:w-64 bg-slate-950/80 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
        />
      </div>

      {/* Obligations Structured Table */}
      <div className="glass-panel border border-slate-800 bg-slate-900/60 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/70 text-slate-400 uppercase tracking-wider text-[11px] font-semibold">
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Responsible Party</th>
                <th className="py-3 px-4">Obligation Details</th>
                <th className="py-3 px-4">Deadline / Amount</th>
                <th className="py-3 px-4">Evidence Quote</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredObligations.map((ob, idx) => (
                <tr key={ob.id || idx} className="hover:bg-slate-800/30 transition-colors">
                  
                  {/* Type */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700 text-slate-200 font-medium text-[11px]">
                      {getTypeIcon(ob.obligation_type)}
                      {ob.obligation_type}
                    </span>
                  </td>

                  {/* Party */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    <span className="font-semibold text-indigo-300 flex items-center gap-1 text-[11px]">
                      <User className="w-3 h-3" />
                      {ob.party || "Unspecified Party"}
                    </span>
                  </td>

                  {/* Description */}
                  <td className="py-3.5 px-4 text-slate-200 max-w-sm font-mono text-[11px]">
                    {ob.description}
                  </td>

                  {/* Deadline or Amount */}
                  <td className="py-3.5 px-4 whitespace-nowrap">
                    {ob.deadline || ob.amount ? (
                      <span className="px-2 py-0.5 rounded font-mono font-semibold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-[11px]">
                        {ob.deadline || `$${ob.amount}`}
                      </span>
                    ) : (
                      <span className="text-slate-500 text-[11px]">—</span>
                    )}
                  </td>

                  {/* Evidence Text */}
                  <td className="py-3.5 px-4 text-slate-400 italic max-w-xs truncate text-[11px]">
                    "{ob.evidence_text}"
                  </td>

                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
