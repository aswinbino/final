import React from 'react';
import { 
  ShieldCheck, 
  User, 
  FileText, 
  GitFork, 
  HelpCircle, 
  Calendar, 
  GitCompare, 
  FileDown,
  LayoutDashboard
} from 'lucide-react';

const ROLES = [
  { value: 'Freelancer', label: 'Freelancer / Contractor', icon: '💻' },
  { value: 'Tenant', label: 'Tenant / Lessee', icon: '🏢' },
  { value: 'Employee', label: 'Employee / Staff', icon: '💼' },
  { value: 'Business Owner', label: 'Business Owner', icon: '👔' },
  { value: 'Vendor', label: 'Vendor / Supplier', icon: '📦' },
  { value: 'General', label: 'General / Standard', icon: '⚖️' },
];

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  userRole, 
  setUserRole, 
  activeContract,
  onOpenReport
}) {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl px-6 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-[2px] flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="brand-font font-bold text-xl text-white tracking-tight">ClauseGuard</span>
              <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">AI</span>
            </div>
            <p className="text-xs text-slate-400">Explainable Legal Risk & Decision Support</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0 text-sm font-medium">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${
              activeTab === 'dashboard' 
                ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Overview
          </button>

          <button
            onClick={() => setActiveTab('clauses')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${
              activeTab === 'clauses' 
                ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <FileText className="w-4 h-4" />
            Clauses
          </button>

          <button
            onClick={() => setActiveTab('chains')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${
              activeTab === 'chains' 
                ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <GitFork className="w-4 h-4" />
            Risk Chains
          </button>

          <button
            onClick={() => setActiveTab('whatif')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${
              activeTab === 'whatif' 
                ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            What-If Simulator
          </button>

          <button
            onClick={() => setActiveTab('obligations')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${
              activeTab === 'obligations' 
                ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Calendar className="w-4 h-4" />
            Obligations
          </button>

          <button
            onClick={() => setActiveTab('compare')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${
              activeTab === 'compare' 
                ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <GitCompare className="w-4 h-4" />
            Compare
          </button>
        </nav>

        {/* User Role Context Engine Selector & Action */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700/80 px-2.5 py-1.5 rounded-xl shadow-inner">
            <User className="w-4 h-4 text-indigo-400" />
            <span className="text-xs text-slate-400 hidden sm:inline">Role:</span>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer pr-1"
            >
              {ROLES.map((r) => (
                <option key={r.value} value={r.value} className="bg-slate-900 text-slate-200">
                  {r.icon} {r.label}
                </option>
              ))}
            </select>
          </div>

          {activeContract && (
            <button
              onClick={onOpenReport}
              className="btn-primary text-xs px-3 py-1.5"
              title="Generate Decision Support Report"
            >
              <FileDown className="w-4 h-4" />
              <span className="hidden sm:inline">Report</span>
            </button>
          )}
        </div>

      </div>
    </header>
  );
}
