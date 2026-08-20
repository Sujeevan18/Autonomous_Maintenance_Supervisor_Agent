import React from 'react';
import { Cpu, ShieldCheck, Activity } from 'lucide-react';

interface AgentEvidencePanelProps {
  rulAgentStatus?: string;
  riskAgentStatus?: string;
  anomalyAgentStatus?: string;
}

export function AgentEvidencePanel({
  rulAgentStatus = 'ACTIVE',
  riskAgentStatus = 'ACTIVE',
  anomalyAgentStatus = 'ACTIVE',
}: AgentEvidencePanelProps) {
  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl space-y-3">
      <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
        <Cpu className="w-4 h-4 text-blue-400" />
        Upstream Agent Evidence Stream
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
        <div className="bg-[#070A12] border border-slate-800/80 rounded-xl p-3 flex justify-between items-center">
          <div>
            <p className="font-bold text-slate-200">RUL Prognostics</p>
            <p className="text-[10px] text-slate-400 mt-0.5">LSTM / XGBoost Twin</p>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
            {rulAgentStatus}
          </span>
        </div>

        <div className="bg-[#070A12] border border-slate-800/80 rounded-xl p-3 flex justify-between items-center">
          <div>
            <p className="font-bold text-slate-200">Failure Risk Agent</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Deep Survival / Cox</p>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
            {riskAgentStatus}
          </span>
        </div>

        <div className="bg-[#070A12] border border-slate-800/80 rounded-xl p-3 flex justify-between items-center">
          <div>
            <p className="font-bold text-slate-200">Explainable Anomaly</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Autoencoder + SHAP</p>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
            {anomalyAgentStatus}
          </span>
        </div>
      </div>
    </div>
  );
}
