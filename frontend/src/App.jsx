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
  ArrowRight,
  Scale,
  GitFork,
  BookOpen
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [userRole, setUserRole] = useState('Freelancer / Contractor');
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

  // Trigger full pipeline conforming to 6 Core Modules & Target API Schema
  const runFullPipeline = async (contractId, role, rawText = null, originalName = null) => {
    setIsProcessing(true);
    setError(null);
    try {
      setProcessingStatus(`Analyzing contract with 6 Core NLP Modules for ${role}...`);

      // Call Target API Schema endpoint
      const analyzeRes = await api.analyzeContract({
        contract_id: contractId,
        text: rawText,
        role: role,
        filename: originalName || activeContract?.original_name || 'Contract.pdf',
      });

      // Update Document Status (Module 1)
      const doc = analyzeRes.document;
      const updatedContract = {
        id: doc.id,
        filename: doc.filename,
        original_name: doc.filename,
        total_pages: doc.total_pages,
        clause_count: doc.total_clauses,
        status: doc.status,
      };
      setActiveContract(updatedContract);

      // Update Clauses (Module 2, 3, 4)
      setClauses(analyzeRes.clauses || []);

      // Update Risk Assessment & Risk Chains (Module 5 & 6)
      const highClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'HIGH');
      const medClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'MEDIUM');
      const lowClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'LOW');

      setRiskAnalysis({
        contract_id: doc.id,
        overall_risk_score: parseFloat(analyzeRes.user_context.risk_summary.risk_exposure_index) / 100 || 0.1,
        overall_risk_level: analyzeRes.user_context.risk_summary.overall_status,
        summary: `Personalized risk evaluation completed for ${role}. ${highClauses.length} critical high-risk clauses identified across ${analyzeRes.clauses.length} analyzed provisions.`,
        role_used: role,
        risk_summary: analyzeRes.user_context.risk_summary,
        high_risk_clauses: highClauses,
        medium_risk_clauses: medClauses,
        low_risk_clauses: lowClauses,
        risk_chains: (analyzeRes.interconnected_risk_chains || []).map(ch => ({
          chain_id: ch.chain_id,
          title: ch.description,
          description: ch.description,
          sequence: ch.sequence,
          link_basis: ch.link_basis || 'Cross-Reference',
          combined_risk: 'HIGH',
          clauses: [],
        })),
        recommendations: [
          'Counter-propose mutual 30 days written termination notice.',
          'Cap aggregate liability at 1x contract fees paid.',
          'Condition IP transfer strictly upon receipt of full payment.',
          'Limit payment withholding exclusively to disputed line items.',
        ],
      });

      // Extract Obligations (Module 8 background)
      try {
        const obRes = await api.extractObligations(doc.id);
        setObligations(obRes.obligations || []);
      } catch (e) {
        // Fallback or empty if not yet extracted
      }

      setProcessingStatus('');
    } catch (err) {
      console.error("Pipeline failure:", err);
      setError(err.response?.data?.detail || err.message || "Failed to process contract.");
    } finally {
      setIsProcessing(false);
    }
  };

  // Re-run personalized risk analysis when user role changes
  useEffect(() => {
    if (activeContract && activeContract.id) {
      runFullPipeline(activeContract.id, userRole);
    }
  }, [userRole]);

  // Handle direct file upload (Module 1)
  const handleUploadSuccess = async (file) => {
    setIsProcessing(true);
    setProcessingStatus('Module 1: Parsing PDF (PyMuPDF) / DOCX (python-docx)...');
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('role', userRole);

      const analyzeRes = await api.analyzeContract(formData);
      const doc = analyzeRes.document;
      const newContract = {
        id: doc.id,
        filename: doc.filename,
        original_name: file.name,
        total_pages: doc.total_pages,
        clause_count: doc.total_clauses,
        status: doc.status,
      };

      setActiveContract(newContract);
      setAllContracts((prev) => [newContract, ...prev]);

      // Populate state with target API response
      setClauses(analyzeRes.clauses || []);

      const highClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'HIGH');
      const medClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'MEDIUM');
      const lowClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'LOW');

      setRiskAnalysis({
        contract_id: doc.id,
        overall_risk_score: parseFloat(analyzeRes.user_context.risk_summary.risk_exposure_index) / 100 || 0.1,
        overall_risk_level: analyzeRes.user_context.risk_summary.overall_status,
        summary: `Risk evaluation completed for ${userRole}. Identified ${highClauses.length} critical clauses and ${medClauses.length} moderate cautions.`,
        role_used: userRole,
        risk_summary: analyzeRes.user_context.risk_summary,
        high_risk_clauses: highClauses,
        medium_risk_clauses: medClauses,
        low_risk_clauses: lowClauses,
        risk_chains: (analyzeRes.interconnected_risk_chains || []).map(ch => ({
          chain_id: ch.chain_id,
          title: ch.description,
          description: ch.description,
          sequence: ch.sequence,
          link_basis: ch.link_basis || 'Cross-Reference',
          combined_risk: 'HIGH',
          clauses: [],
        })),
        recommendations: [
          'Propose mutual 30 days written termination notice.',
          'Request aggregate liability cap of 1x fees paid.',
          'Condition deliverable IP ownership upon full payment.',
        ],
      });

      // Extract obligations
      try {
        const obRes = await api.extractObligations(doc.id);
        setObligations(obRes.obligations || []);
      } catch (e) {}

      setProcessingStatus('');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Upload failed");
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle instant demo sample load
  const handleLoadSample = async (sample) => {
    setIsProcessing(true);
    setProcessingStatus(`Loading sample contract (${sample.title}) for ${sample.role}...`);
    setUserRole(sample.role);

    try {
      const analyzeRes = await api.analyzeContract({
        text: sample.text,
        filename: sample.filename,
        role: sample.role,
      });

      const doc = analyzeRes.document;
      const newContract = {
        id: doc.id,
        filename: sample.filename,
        original_name: sample.title,
        total_pages: doc.total_pages,
        clause_count: doc.total_clauses,
        status: doc.status,
      };

      setActiveContract(newContract);
      setAllContracts((prev) => [newContract, ...prev]);
      setClauses(analyzeRes.clauses || []);

      const highClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'HIGH');
      const medClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'MEDIUM');
      const lowClauses = (analyzeRes.clauses || []).filter(c => c.risk_level === 'LOW');

      setRiskAnalysis({
        contract_id: doc.id,
        overall_risk_score: parseFloat(analyzeRes.user_context.risk_summary.risk_exposure_index) / 100 || 0.1,
        overall_risk_level: analyzeRes.user_context.risk_summary.overall_status,
        summary: `Personalized evaluation for ${sample.role}: ${highClauses.length} critical high-risk clause(s) found across ${analyzeRes.clauses.length} provisions.`,
        role_used: sample.role,
        risk_summary: analyzeRes.user_context.risk_summary,
        high_risk_clauses: highClauses,
        medium_risk_clauses: medClauses,
        low_risk_clauses: lowClauses,
        risk_chains: (analyzeRes.interconnected_risk_chains || []).map(ch => ({
          chain_id: ch.chain_id,
          title: ch.description,
          description: ch.description,
          sequence: ch.sequence,
          link_basis: ch.link_basis || 'Cross-Reference',
          combined_risk: 'HIGH',
          clauses: [],
        })),
        recommendations: [
          'Propose mutual 30 days written termination notice.',
          'Request aggregate liability cap of 1x fees paid.',
          'Condition deliverable IP ownership upon full payment.',
        ],
      });

      setProcessingStatus('');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load sample");
    } finally {
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
        
        {/* Module 1: Upload & Ingestion Confirmation Area */}
        <UploadSection
          onUploadSuccess={handleUploadSuccess}
          onLoadSample={handleLoadSample}
          isProcessing={isProcessing}
          activeContract={activeContract}
          totalClauses={clauses.length}
          userRole={userRole}
          onRoleChange={setUserRole}
        />

        {/* Global Loading Indicator */}
        {isProcessing && (
          <div className="glass-panel p-4 mb-6 border border-cyan-500/40 bg-indigo-950/40 rounded-xl flex items-center justify-between text-xs text-indigo-200 animate-pulse shadow-lg shadow-cyan-500/10">
            <div className="flex items-center gap-2.5">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
              <span>{processingStatus || 'Analyzing contract provisions across 8 legal categories with FAISS and RoBERTa...'}</span>
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
              onSelectRole={setUserRole}
            />

            {clauses.length > 0 && (
              <div className="mt-8">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-slate-200">Featured High-Priority Clauses</h3>
                    <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-cyan-300 border border-indigo-500/30">
                      Module 2 & 4
                    </span>
                  </div>
                  <button
                    onClick={() => setActiveTab('clauses')}
                    className="text-xs text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <span>View all {clauses.length} clauses</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
                <ClauseExplorer clauses={clauses.slice(0, 5)} selectedSeverity="All" activeRole={userRole} />
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Clause Explorer (Modules 2, 3, 4) */}
        {activeTab === 'clauses' && (
          <div>
            <ClauseExplorer clauses={clauses} selectedSeverity={selectedSeverityFilter} activeRole={userRole} />
          </div>
        )}

        {/* Tab 3: Risk Chains (Module 6) */}
        {activeTab === 'chains' && (
          <div>
            <RiskChainsView riskChains={riskAnalysis?.risk_chains || []} clauses={clauses} />
          </div>
        )}

        {/* Tab 4: What-If Simulator */}
        {activeTab === 'whatif' && (
          <div>
            <WhatIfSimulator contractId={activeContract?.id} userRole={userRole} />
          </div>
        )}

        {/* Tab 5: Obligations Table */}
        {activeTab === 'obligations' && (
          <div>
            <ObligationsTable obligations={obligations} />
          </div>
        )}

        {/* Tab 6: Contract Comparison */}
        {activeTab === 'compare' && (
          <div>
            <ContractComparator
              contracts={allContracts}
              currentContractId={activeContract?.id}
            />
          </div>
        )}

      </main>

      {/* Decision Support Report Modal */}
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
            <span>— Explainable and Personalized NLP Framework for Contract Risk Assessment</span>
          </div>
          <span className="font-mono text-[11px] text-slate-600">
            PyMuPDF · python-docx · RoBERTa · Sentence-Transformers · FAISS · FastAPI · React
          </span>
        </div>
      </footer>

    </div>
  );
}
