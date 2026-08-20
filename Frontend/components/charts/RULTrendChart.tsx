import React from 'react';
import { Clock } from 'lucide-react';

interface RULTrendChartProps {
  rulCycles?: number;
}

export function RULTrendChart({ rulCycles = 24 }: RULTrendChartProps) {
  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-blue-400" />
          RUL Prognostics Trajectory (Cycles vs Time)
        </h2>
        <span className="text-xs text-blue-400 font-mono">Current: {rulCycles} Cycles Remaining</span>
      </div>

      <div className="w-full h-40 bg-[#070A12] border border-slate-800/80 rounded-xl p-4 relative overflow-hidden flex items-end">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 120" preserveAspectRatio="none">
          <line x1="0" y1="30" x2="1000" y2="30" stroke="#1e293b" strokeDasharray="4 4" />
          <line x1="0" y1="60" x2="1000" y2="60" stroke="#1e293b" strokeDasharray="4 4" />
          <line x1="0" y1="90" x2="1000" y2="90" stroke="#1e293b" strokeDasharray="4 4" />

          {/* RUL Linear Degradation Line */}
          <path
            d="M 0 10 L 800 110 L 1000 115"
            fill="none"
            stroke="#3b82f6"
            strokeWidth="3"
          />
        </svg>

        <div className="absolute top-2 left-3 text-[10px] font-mono text-slate-500 space-y-4">
          <p>200</p>
          <p>100</p>
          <p>50</p>
          <p>0</p>
        </div>
      </div>
    </div>
  );
}
