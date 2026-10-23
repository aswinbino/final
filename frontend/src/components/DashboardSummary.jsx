import React from 'react';
import { 
  AlertTriangle, 
  ShieldAlert, 
  ShieldCheck, 
  Shield, 
  Lightbulb, 
  FileText, 
  ArrowUpRight,
  TrendingUp,
  UserCheck
} from 'lucide-react';

export default function DashboardSummary({ 
  riskAnalysis, 
  contract, 
  clauses, 
  userRole, 
  onSelectCategory,
  onOpenReport
}) {
  if (!riskAnalysis) return null;

  const {
    overall_risk_score = 0,
    overall_risk_level = 'Low',
    summary = '',
    recommendations = [],
    high_risk_clauses = [],
    medium_risk_clauses = [],
    low_risk_clauses = [],
  } = riskAnalysis;

  const totalClauses = (clauses?.length) || (high_risk_clauses.length + medium_risk_clauses.length + low_risk_clauses.length);
  const scorePercent = Math.round(overall_risk_score * 100);

  const getRiskColor = (level) => {
    switch (level) {
      case 'High': return 'text-red-400 border-red-500/40 bg-red-500/10';
      case 'Medium': return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
      default: return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
    }
  };

  return (
    <div className="space-y-6 mb-8">
      
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        {/* Overall Risk Card */}
        <div className="glass-panel p-5 border border-slate-800 bg-slate-900/60 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Risk Status</span>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${getRiskColor(overall_risk_level)}`}>
              {overall_risk_level}
            </span>
          </div>

          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-4xl font-extrabold text-white brand-font tracking-tight">{scorePercent}%</span>
            <span className="text-xs text-slate-400">Risk Exposure Index</span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-full transition-all duration-700 ${
                overall_risk_level === 'High' ? 'bg-gradient-to-r from-amber-500 to-red-500' :
                overall_risk_level === 'Medium' ? 'bg-gradient-to-r from-emerald-500 to-amber-500' :
                'bg-gradient-to-r from-cyan-500 to-emerald-500'
              }`}
              style={{ width: `${Math.max(5, Math.min(100, scorePercent))}%` }}
            />
          </div>
        </div>

        {/* High Risk Count */}
        <div 
          onClick={() => onSelectCategory('High')}
          className="glass-panel p-5 border border-slate-800 hover:border-red-500/40 bg-slate-900/60 cursor-pointer transition-all hover:scale-[1.01]"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Critical Risk Clauses</span>
            <div className="w-7 h-7 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-red-400 brand-font mb-1">
            {high_risk_clauses.length}
          </div>
          <p className="text-[11px] text-slate-400">Requires mandatory renegotiation or exclusion</p>
        </div>

        {/* Medium Risk Count */}
        <div 
          onClick={() => onSelectCategory('Medium')}
          className="glass-panel p-5 border border-slate-800 hover:border-amber-500/40 bg-slate-900/60 cursor-pointer transition-all hover:scale-[1.01]"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Moderate Caution</span>
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-amber-400 brand-font mb-1">
            {medium_risk_clauses.length}
          </div>
          <p className="text-[11px] text-slate-400">Unfavorable terms needing clarification</p>
        </div>

        {/* Total Analyzed */}
        <div 
          onClick={() => onSelectCategory('All')}
          className="glass-panel p-5 border border-slate-800 hover:border-indigo-500/40 bg-slate-900/60 cursor-pointer transition-all hover:scale-[1.01]"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Clauses</span>
            <div className="w-7 h-7 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-slate-100 brand-font mb-1">
            {totalClauses}
          </div>
          <p className="text-[11px] text-slate-400">
            {low_risk_clauses.length} standard / routine clauses
          </p>
        </div>

      </div>

      {/* Role Context Engine Banner (Module 4) */}
      <div className="glass-panel p-4 border border-indigo-900/50 bg-gradient-to-r from-indigo-950/40 to-slate-900/60 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-300 flex-shrink-0">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
                Module 4 · Active Personalization Engine:
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-white border border-indigo-500/30">
                {userRole}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              {summary}
            </p>
          </div>
        </div>

        <button
          onClick={onOpenReport}
          className="btn-secondary text-xs px-3 py-1.5 whitespace-nowrap self-end md:self-auto"
        >
          <span>View Full Decision Report</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Key AI Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="glass-panel p-5 border border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-2 mb-3 text-slate-200 font-semibold text-sm">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <span>AI Negotiation Action Items (Decision Support)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {recommendations.map((rec, idx) => (
              <div 
                key={idx}
                className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs text-slate-300 flex items-start gap-2.5"
              >
                <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="leading-relaxed">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
