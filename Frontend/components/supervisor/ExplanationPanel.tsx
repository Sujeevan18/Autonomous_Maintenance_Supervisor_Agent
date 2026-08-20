import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ExplanationPanelProps {
  currentCycle: number;
  failureRisk: number;
  rulCycles: number;
  attribution?: string;
  policyAction?: string;
}

export function ExplanationPanel({
  currentCycle = 168,
  failureRisk = 89,
  rulCycles = 24,
  attribution = 'High Pressure Compressor (HPC) pressure anomaly attribution',
  policyAction = 'Perform Preventive Maintenance',
}: ExplanationPanelProps) {
  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl space-y-2">
      <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
        Explainable Decision Justification (XAI)
      </h3>

      <div className="bg-[#070A12] border border-slate-800 rounded-xl p-3 text-xs text-slate-300 italic leading-relaxed">
        &quot;At Cycle {currentCycle}, predicted 48h failure probability reached {failureRisk}% with Remaining Useful Life at {rulCycles} cycles. {attribution} triggers {policyAction} policy.&quot;
      </div>
    </div>
  );
}
