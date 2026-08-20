import React from 'react';
import { Gauge } from 'lucide-react';

interface ConfidenceTrendChartProps {
  confidence?: number;
}

export function ConfidenceTrendChart({ confidence = 99.95 }: ConfidenceTrendChartProps) {
  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Gauge className="w-4 h-4 text-purple-400" />
          Supervisor Policy Decision Confidence Calibration
        </h2>
        <span className="text-xs text-purple-400 font-mono">Macro F1: {confidence}%</span>
      </div>

      <div className="w-full h-40 bg-[#070A12] border border-slate-800/80 rounded-xl p-4 relative overflow-hidden flex items-end">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 120" preserveAspectRatio="none">
          <line x1="0" y1="30" x2="1000" y2="30" stroke="#1e293b" strokeDasharray="4 4" />
          <line x1="0" y1="60" x2="1000" y2="60" stroke="#1e293b" strokeDasharray="4 4" />

          {/* High Steady Confidence Line */}
          <path
            d="M 0 20 L 300 18 L 600 22 L 900 15 L 1000 15"
            fill="none"
            stroke="#a855f7"
            strokeWidth="3"
          />
        </svg>

        <div className="absolute top-2 left-3 text-[10px] font-mono text-slate-500 space-y-4">
          <p>100%</p>
          <p>90%</p>
          <p>80%</p>
        </div>
      </div>
    </div>
  );
}
