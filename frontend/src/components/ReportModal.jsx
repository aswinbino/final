import React, { useState, useEffect } from 'react';
import { 
  FileDown, 
  CheckCircle2, 
  FileText, 
  Code, 
  Printer, 
  Loader2, 
  AlertTriangle,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import api from '../services/api';

export default function ReportModal({ contractId, userRole, onClose }) {
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [viewMode, setViewMode] = useState('summary'); // 'summary' | 'json'
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchReport() {
      if (!contractId) return;
      setLoading(true);
      setError(null);
      try {
        const res = await api.generateReport(contractId, userRole, 'json');
        setReportData(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || "Failed to generate report.");
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [contractId, userRole]);

  const handleGeneratePdf = async () => {
    setPdfLoading(true);
    try {
      const res = await api.generateReport(contractId, userRole, 'pdf');
      if (res.download_url) {
        setDownloadUrl(res.download_url);
        window.open(res.download_url, '_blank');
      }
    } catch (err) {
      alert("PDF generation error: " + (err.response?.data?.detail || err.message));
    } finally {
      setPdfLoading(false);
    }
  };

  const copyJson = () => {
    if (reportData) {
      navigator.clipboard.writeText(JSON.stringify(reportData, null, 2));
      alert("Report JSON copied to clipboard!");
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel border border-slate-700 bg-slate-900 max-w-4xl w-full p-6 rounded-2xl shadow-2xl relative max-h-[90vh] flex flex-col">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-400">
              <FileDown className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white">Module 10 · Decision Support & Risk Report</h3>
              <p className="text-xs text-slate-400">Personalized for {userRole} · Exportable Summary</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="bg-slate-950 p-1 rounded-xl border border-slate-800 flex items-center gap-1 text-xs">
              <button
                onClick={() => setViewMode('summary')}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  viewMode === 'summary' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Summary View
              </button>
              <button
                onClick={() => setViewMode('json')}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  viewMode === 'json' ? 'bg-indigo-600 text-white font-semibold' : 'text-slate-400 hover:text-white'
                }`}
              >
                Raw JSON
              </button>
            </div>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto py-5 pr-1 space-y-6">
          {loading ? (
            <div className="py-20 text-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mx-auto mb-2" />
              <p className="text-xs text-slate-400">Synthesizing full decision report...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs">
              {error}
            </div>
          ) : viewMode === 'json' ? (
            <div className="relative">
              <button
                onClick={copyJson}
                className="absolute top-3 right-3 px-3 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs font-mono hover:bg-slate-700"
              >
                Copy JSON
              </button>
              <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 max-h-[60vh] overflow-auto">
                {JSON.stringify(reportData, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="space-y-6">
              
              {/* Executive Overview */}
              <div className="glass-panel p-5 border border-slate-800 bg-slate-950/60 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Executive Summary
                  </span>
                  <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full uppercase border ${
                    reportData?.executive_summary?.overall_risk_level === 'High' ? 'bg-red-500/20 text-red-300 border-red-500/40' :
                    reportData?.executive_summary?.overall_risk_level === 'Medium' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                    'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  }`}>
                    {reportData?.executive_summary?.overall_risk_level} Risk
                  </span>
                </div>

                <p className="text-xs text-slate-200 leading-relaxed">
                  {reportData?.executive_summary?.summary}
                </p>

                <div className="grid grid-cols-4 gap-2 pt-2 text-center text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Total Clauses</span>
                    <strong className="text-slate-200 font-bold text-sm">
                      {reportData?.executive_summary?.total_clauses_analyzed}
                    </strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-red-950/30 border border-red-900/40">
                    <span className="text-red-400 block text-[10px]">High Risk</span>
                    <strong className="text-red-300 font-bold text-sm">
                      {reportData?.executive_summary?.high_risk_count}
                    </strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-900/40">
                    <span className="text-amber-400 block text-[10px]">Medium Risk</span>
                    <strong className="text-amber-300 font-bold text-sm">
                      {reportData?.executive_summary?.medium_risk_count}
                    </strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-emerald-950/30 border border-emerald-900/40">
                    <span className="text-emerald-400 block text-[10px]">Low Risk</span>
                    <strong className="text-emerald-300 font-bold text-sm">
                      {reportData?.executive_summary?.low_risk_count}
                    </strong>
                  </div>
                </div>
              </div>

              {/* High Risk Clauses Section */}
              {reportData?.risk_breakdown?.high?.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" /> High-Risk Unfavorable Terms
                  </h4>
                  <div className="space-y-2.5">
                    {reportData.risk_breakdown.high.map((clause, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-red-950 text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-slate-200">
                            Clause #{idx + 1} [{clause.category}]
                          </span>
                          <span className="text-[10px] text-red-400 font-mono">High Risk</span>
                        </div>
                        <p className="text-slate-300 font-mono text-[11px] mb-2">{clause.cleaned_text}</p>
                        <p className="text-[11px] text-red-400 italic">
                          <strong>Finding: </strong>{clause.risk_reasoning}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Recommendations */}
              {reportData?.recommendations?.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">
                    Recommended Negotiation Counter-Terms
                  </h4>
                  <div className="space-y-2">
                    {reportData.recommendations.map((rec, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between flex-shrink-0">
          <span className="text-[11px] text-slate-500 font-mono">
            Report ID: {reportData?.report_metadata?.contract_id?.slice(0, 8)} · ClauseGuard AI v1.0
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={handleGeneratePdf}
              disabled={pdfLoading}
              className="btn-primary text-xs px-4 py-2"
            >
              {pdfLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <FileDown className="w-4 h-4" />
                  <span>Download PDF Report</span>
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="btn-secondary text-xs px-4 py-2"
            >
              Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
