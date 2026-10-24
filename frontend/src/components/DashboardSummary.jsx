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
  UserCheck,
  Scale,
  GitFork,
  BookOpen,
  Sparkles,
  Layers,
  ArrowRight
} from 'lucide-react';

const ROLE_PRIORITY_NOTES = {
  'Freelancer / Contractor': 'High priority on Payment Withholding, Immediate Termination, and Non-Compete restrictions that prevent earning.',
  'Tenant': 'High priority on Rent Delays, Deposit Forfeiture, and Auto-Renewal extensions. (Non-compete covenants de-prioritized to Low Risk).',
  'Employee': 'High priority on Post-Employment Non-Competes, Pre-Existing IP assignment, and at-will termination without severance.',
  'Client / Small Business Owner': 'High priority on Supplier Liability Caps, Uncapped Customer Indemnity, and Overseas Dispute Seats.',
};

export default function DashboardSummary({ 
  riskAnalysis, 
  contract, 
  clauses, 
  userRole, 
  onSelectCategory,
  onOpenReport,
  onSelectRole
}) {
  if (!riskAnalysis) return null;

  const {
    overall_risk_score = 0,
    overall_risk_level = 'LOW',
    summary = '',
    recommendations = [],
    high_risk_clauses = [],
    medium_risk_clauses = [],
    low_risk_clauses = [],
    risk_summary,
  } = riskAnalysis;

  // Use risk_summary from target schema if present
  const criticalCount = risk_summary?.critical_count ?? high_risk_clauses.length;
  const moderateCount = risk_summary?.moderate_caution_count ?? medium_risk_clauses.length;
  const lowCount = risk_summary?.low_risk_count ?? low_risk_clauses.length;
  const totalClauses = (clauses?.length) || (criticalCount + moderateCount + lowCount);

  const displayStatus = (risk_summary?.overall_status || overall_risk_level || 'LOW').toUpperCase();
  const exposureIndex = risk_summary?.risk_exposure_index || `${Math.round(overall_risk_score * 100)}%`;
  const exposureNum = parseInt(exposureIndex) || Math.round(overall_risk_score * 100);

  const getRiskColor = (level) => {
    switch (level.toUpperCase()) {
      case 'HIGH': return 'text-red-400 border-red-500/50 bg-red-500/10';
      case 'MEDIUM': return 'text-amber-400 border-amber-500/50 bg-amber-500/10';
      default: return 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10';
    }
  };

  return (
    <div className="space-y-6 mb-8">
      
      {/* Top Metric Cards (Target API Schema Grounding) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Overall Status & Risk Exposure Index Card */}
        <div className="glass-panel p-5 border border-slate-800 bg-slate-900/70 relative overflow-hidden flex flex-col justify-between shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Overall Status
            </span>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border font-mono ${getRiskColor(displayStatus)}`}>
              {displayStatus} RISK
            </span>
          </div>

          <div className="flex items-baseline gap-2 mb-3">
            <span className="text-4xl font-extrabold text-white brand-font tracking-tight font-mono">{exposureIndex}</span>
            <span className="text-xs text-slate-400">Risk Exposure Index</span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-full transition-all duration-700 ${
                displayStatus === 'HIGH' ? 'bg-gradient-to-r from-amber-500 to-red-500' :
                displayStatus === 'MEDIUM' ? 'bg-gradient-to-r from-emerald-500 to-amber-500' :
                'bg-gradient-to-r from-cyan-500 to-emerald-500'
              }`}
              style={{ width: `${Math.max(5, Math.min(100, exposureNum))}%` }}
            />
          </div>
        </div>

        {/* Critical Risk Count (HIGH RISK) */}
        <div 
          onClick={() => onSelectCategory('HIGH')}
          className="glass-panel p-5 border border-slate-800 hover:border-red-500/50 bg-slate-900/70 cursor-pointer transition-all hover:scale-[1.01] shadow-xl"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Critical Count
            </span>
            <div className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400 border border-red-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-4xl font-extrabold text-red-400 brand-font mb-1 font-mono">
            {criticalCount}
          </div>
          <p className="text-[11px] text-slate-400">HIGH RISK · Requires mandatory renegotiation or deletion</p>
        </div>

        {/* Moderate Caution Count (MEDIUM CAUTION) */}
        <div 
          onClick={() => onSelectCategory('MEDIUM')}
          className="glass-panel p-5 border border-slate-800 hover:border-amber-500/50 bg-slate-900/70 cursor-pointer transition-all hover:scale-[1.01] shadow-xl"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Moderate Caution
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 border border-amber-500/20">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="text-4xl font-extrabold text-amber-400 brand-font mb-1 font-mono">
            {moderateCount}
          </div>
          <p className="text-[11px] text-slate-400">MEDIUM CAUTION · Needs revision or clarifying amendments</p>
        </div>

        {/* Low Risk Standard Count (LOW RISK) */}
        <div 
          onClick={() => onSelectCategory('LOW')}
          className="glass-panel p-5 border border-slate-800 hover:border-emerald-500/50 bg-slate-900/70 cursor-pointer transition-all hover:scale-[1.01] shadow-xl"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Low Risk Count
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-4xl font-extrabold text-emerald-400 brand-font mb-1 font-mono">
            {lowCount}
          </div>
          <p className="text-[11px] text-slate-400">LOW RISK · Standard commercial provisions</p>
        </div>

      </div>

      {/* Feature 3: Dynamic Role Context & Matrix Shift Banner */}
      <div className="glass-panel p-5 border border-indigo-900/50 bg-gradient-to-r from-indigo-950/30 via-slate-900/70 to-slate-900/80 rounded-2xl shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-400 flex-shrink-0 mt-0.5">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-mono tracking-wider font-bold text-cyan-300">
                  Module 5 · Role-Aware Risk Matrix w_i(u)
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold">
                  Active Role: {userRole}
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                {ROLE_PRIORITY_NOTES[userRole] || 'Risks are dynamically ranked based on your active party identity.'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {onOpenReport && (
              <button
                onClick={onOpenReport}
                className="px-4 py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Export Executive Report</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Key Strategic Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="glass-panel p-5 border border-slate-800 bg-slate-900/60 rounded-2xl shadow-xl">
          <div className="flex items-center gap-2 mb-3 text-cyan-400 font-bold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>Top Negotiation Recommendations for {userRole}:</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {recommendations.slice(0, 4).map((rec, i) => (
              <div 
                key={i}
                className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5"
              >
                <span className="w-5 h-5 rounded-md bg-indigo-500/20 text-cyan-300 flex items-center justify-center text-[10px] font-mono font-bold flex-shrink-0 mt-0.5">
                  {i + 1}
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
