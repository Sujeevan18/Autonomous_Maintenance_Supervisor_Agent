import React from 'react';
import { Activity } from 'lucide-react';

interface RiskTrendChartProps {
  simulatedCycles?: number;
}

export function RiskTrendChart({ simulatedCycles = 0 }: RiskTrendChartProps) {
  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Activity className="w-4 h-4 text-amber-400" />
          Multi-Horizon Failure Risk Trajectory Evolution
        </h2>
        <span className="text-xs text-slate-400 font-mono">Confidence Band: ±5% (MC-Dropout Uncertainty)</span>
      </div>

      <div className="w-full h-44 bg-[#070A12] border border-slate-800/80 rounded-xl p-4 relative overflow-hidden flex items-end">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 140" preserveAspectRatio="none">
          <defs>
            <linearGradient id="riskGradComp" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.05" />
            </linearGradient>
          </defs>

          <line x1="0" y1="35" x2="1000" y2="35" stroke="#1e293b" strokeDasharray="4 4" />
          <line x1="0" y1="70" x2="1000" y2="70" stroke="#1e293b" strokeDasharray="4 4" />
          <line x1="0" y1="105" x2="1000" y2="105" stroke="#1e293b" strokeDasharray="4 4" />

          <path
            d="M 0 120 Q 250 110, 500 80 T 1000 20 L 1000 140 L 0 140 Z"
            fill="url(#riskGradComp)"
          />

          <path
            d="M 0 110 Q 250 95, 500 65 T 1000 10"
            fill="none"
            stroke="#fbbf24"
            strokeWidth="1.5"
            strokeDasharray="2 2"
            opacity="0.6"
          />

          <path
            d="M 0 120 Q 250 110, 500 80 T 1000 20"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="3"
          />

          <circle
            cx={Math.min(990, 50 + simulatedCycles * 42)}
            cy={120 - simulatedCycles * 4.5}
            r="6"
            fill="#fbbf24"
            stroke="#ffffff"
            strokeWidth="2"
            className="animate-pulse"
          />
        </svg>

        <div className="absolute top-2 left-3 text-[10px] font-mono text-slate-500 space-y-5">
          <p>1.0</p>
          <p>0.75</p>
          <p>0.50</p>
          <p>0.25</p>
        </div>
      </div>
    </div>
  );
}
