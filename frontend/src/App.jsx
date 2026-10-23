import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UploadSection from './components/UploadSection';
import DashboardSummary from './components/DashboardSummary';
import ClauseExplorer from './components/ClauseExplorer';
import RiskChainsView from './components/RiskChainsView';
import WhatIfSimulator from './components/WhatIfSimulator';
import ObligationsTable from './components/ObligationsTable';
import ContractComparator from './components/ContractComparator';
import ReportModal from './components/ReportModal';
import api from './services/api';
import { SAMPLE_CONTRACTS } from './data/sampleContracts';
import { 
  ShieldCheck, 
  Loader2, 
  AlertCircle, 
  CheckCircle, 
  FileText, 
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [userRole, setUserRole] = useState('Freelancer');
  const [activeContract, setActiveContract] = useState(null);
  const [allContracts, setAllContracts] = useState([]);
  const [clauses, setClauses] = useState([]);
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [obligations, setObligations] = useState([]);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [error, setError] = useState(null);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [selectedSeverityFilter, setSelectedSeverityFilter] = useState('All');

  // Trigger full pipeline for a contract ID
  const runFullPipeline = async (contractId, role) => {
    setIsProcessing(true);
    setError(null);
    try {
      // 1. Extract Clauses (Module 2 & 7)
      setProcessingStatus('Module 2: Segmenting & classifying clauses...');
      const clauseRes = await api.extractClauses(contractId, role);
      setClauses(clauseRes.clauses);

      // 2. Risk Analysis & Chains (Modules 3, 4, 5)
      setProcessingStatus(`Module 3-5: Computing personalized risks for ${role}...`);
      const riskRes = await api.runRiskAnalysis(contractId, role);
      setRiskAnalysis(riskRes);

      // 3. Extract Obligations (Module 8)
      setProcessingStatus('Module 8: Identifying notice periods & obligations...');
      const obRes = await api.extractObligations(contractId);
      setObligations(obRes.obligations);

      setProcessingStatus('');
    } catch (err) {
      console.error("Pipeline failure:", err);
      setError(err.response?.data?.detail || err.message || "Failed to process contract.");
    } finally {
      setIsProcessing(false);
    }
  };

  // When user changes role in dropdown, automatically re-run personalized risk analysis
  useEffect(() => {
    if (activeContract && activeContract.id) {
      runFullPipeline(activeContract.id, userRole);
    }
  }, [userRole]);

  // Handle file upload
  const handleUploadSuccess = async (file) => {
    setIsProcessing(true);
    setProcessingStatus('Module 1: Uploading and parsing contract text...');
    try {
      const uploadRes = await api.uploadContract(file);
      const newContract = {
        id: uploadRes.contract_id,
        filename: uploadRes.filename,
        original_name: uploadRes.filename,
      };
      setActiveContract(newContract);
      setAllContracts((prev) => [newContract, ...prev]);

      // Poll until parsing is ready
      await waitForProcessing(newContract.id);
      await runFullPipeline(newContract.id, userRole);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Upload failed");
      setIsProcessing(false);
    }
  };

  const waitForProcessing = async (contractId, maxAttempts = 20) => {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const res = await api.getContractStatus(contractId);
        if (res.status === 'done') return true;
        if (res.status === 'error') throw new Error(res.error || 'Document parsing failed.');
      } catch (e) {
        if (i === maxAttempts - 1) throw e;
      }
      await new Promise((r) => setTimeout(r, 500));
    }
    return true;
  };

  // Handle instant demo sample load
  const handleLoadSample = async (sample) => {
    setIsProcessing(true);
    setProcessingStatus(`Loading sample agreement (${sample.title})...`);
    setUserRole(sample.role);

    try {
      const blob = new Blob([sample.text], { type: 'text/plain' });
      const file = new File([blob], sample.filename, { type: 'text/plain' });

      const uploadRes = await api.uploadContract(file);
      const newContract = {
        id: uploadRes.contract_id,
        filename: sample.filename,
        original_name: sample.title,
      };
      setActiveContract(newContract);
      setAllContracts((prev) => [newContract, ...prev]);

      await waitForProcessing(newContract.id);
      await runFullPipeline(newContract.id, sample.role);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load sample");
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 flex flex-col font-sans">
      
      {/* Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        userRole={userRole}
        setUserRole={setUserRole}
        activeContract={activeContract}
        onOpenReport={() => setIsReportOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        
        {/* Upload & Dropzone Area (always accessible or collapsable) */}
        <UploadSection
          onUploadSuccess={handleUploadSuccess}
          onLoadSample={handleLoadSample}
          isProcessing={isProcessing}
        />

        {/* Global Loading Indicator */}
        {isProcessing && (
          <div className="glass-panel p-4 mb-6 border border-indigo-500/40 bg-indigo-950/30 rounded-xl flex items-center justify-between text-xs text-indigo-200 animate-pulse">
            <div className="flex items-center gap-2.5">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
              <span>{processingStatus || 'Analyzing contract clauses with Hugging Face & FAISS NLP models...'}</span>
            </div>
            <span className="font-mono text-[11px] text-cyan-400 font-semibold">Live Processing</span>
          </div>
        )}

        {/* Global Error Banner */}
        {error && (
          <div className="p-4 mb-6 rounded-xl bg-red-950/50 border border-red-500/50 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Active Contract Header */}
        {activeContract && (
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-2.5">
              <FileText className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-sm font-bold text-white">
                  {activeContract.original_name || activeContract.filename}
                </h2>
                <p className="text-[11px] text-slate-400 font-mono">
                  ID: {activeContract.id} · Active Role: <span className="text-cyan-400 font-semibold">{userRole}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 font-medium">
                <CheckCircle className="w-3.5 h-3.5" /> NLP Pipeline Complete
              </span>
            </div>
          </div>
        )}

        {/* Tab 1: Executive Dashboard Overview */}
        {activeTab === 'dashboard' && (
          <div>
            <DashboardSummary
              riskAnalysis={riskAnalysis}
              contract={activeContract}
              clauses={clauses}
              userRole={userRole}
              onSelectCategory={(sev) => {
                setSelectedSeverityFilter(sev);
                setActiveTab('clauses');
              }}
              onOpenReport={() => setIsReportOpen(true)}
            />

            {clauses.length > 0 && (
              <div className="mt-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-bold text-slate-200">Featured High-Priority Clauses</h3>
                  <button
                    onClick={() => setActiveTab('clauses')}
                    className="text-xs text-cyan-400 hover:underline flex items-center gap-1"
                  >
                    <span>View all {clauses.length} clauses</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
                <ClauseExplorer clauses={clauses.slice(0, 5)} selectedSeverity="All" />
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Clause Explorer (Modules 2, 3, 7) */}
        {activeTab === 'clauses' && (
          <div>
            <ClauseExplorer clauses={clauses} selectedSeverity={selectedSeverityFilter} />
          </div>
        )}

        {/* Tab 3: Risk Chains (Module 5) */}
        {activeTab === 'chains' && (
          <div>
            <RiskChainsView riskChains={riskAnalysis?.risk_chains || []} clauses={clauses} />
          </div>
        )}

        {/* Tab 4: What-If Simulator (Module 6) */}
        {activeTab === 'whatif' && (
          <div>
            <WhatIfSimulator contractId={activeContract?.id} userRole={userRole} />
          </div>
        )}

        {/* Tab 5: Obligations Table (Module 8) */}
        {activeTab === 'obligations' && (
          <div>
            <ObligationsTable obligations={obligations} />
          </div>
        )}

        {/* Tab 6: Contract Comparison (Module 9) */}
        {activeTab === 'compare' && (
          <div>
            <ContractComparator
              contracts={allContracts}
              currentContractId={activeContract?.id}
            />
          </div>
        )}

      </main>

      {/* Decision Support Report Modal (Module 10) */}
      {isReportOpen && activeContract && (
        <ReportModal
          contractId={activeContract.id}
          userRole={userRole}
          onClose={() => setIsReportOpen(false)}
        />
      )}

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-900 bg-slate-950/80 py-6 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-slate-400">ClauseGuard AI</span>
            <span>— Explainable, Personalized Legal Risk Platform</span>
          </div>
          <span className="font-mono text-[11px] text-slate-600">
            PyMuPDF · python-docx · RoBERTa · Sentence-Transformers · FAISS · FastAPI · React
          </span>
        </div>
      </footer>

    </div>
  );
}
