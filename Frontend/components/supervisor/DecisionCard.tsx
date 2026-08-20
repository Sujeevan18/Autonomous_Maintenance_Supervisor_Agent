import React from 'react';
import { Zap } from 'lucide-react';

interface DecisionCardProps {
  action: string;
  actionCode?: string;
  confidence: number;
  urgency?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export function DecisionCard({
  action,
  actionCode = '#3',
  confidence = 92.4,
  urgency = 'HIGH',
}: DecisionCardProps) {
  return (
    <div className="bg-gradient-to-br from-[#19150B] to-[#120F08] border border-amber-500/40 rounded-2xl p-5 shadow-xl flex flex-col justify-between relative overflow-hidden">
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400">
          <Zap className="w-4 h-4 fill-amber-400" />
          <span>RECOMMENDED ACTION (RL_PPO)</span>
        </div>
        <span className="px-2.5 py-0.5 rounded text-[10px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/40 uppercase">
          {urgency} URGENCY
        </span>
      </div>

      <div className="my-2">
        <h3 className="text-xl font-black text-amber-400 tracking-tight leading-snug">
          {action}
        </h3>
        <p className="text-xs text-amber-200/80 font-mono mt-1">Action Code: {actionCode}</p>
      </div>

      <div className="flex justify-between items-center text-xs pt-2 border-t border-amber-500/20">
        <span className="text-slate-400 font-mono">Policy Confidence:</span>
        <span className="text-emerald-400 font-bold font-mono">{confidence}%</span>
      </div>
    </div>
  );
}
