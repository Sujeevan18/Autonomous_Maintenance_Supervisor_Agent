import React from 'react';
import { Activity } from 'lucide-react';

interface AnomalyTrendChartProps {
  anomalyScore?: number | string;
}

export function AnomalyTrendChart({ anomalyScore = 0.84 }: AnomalyTrendChartProps) {
  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Activity className="w-4 h-4 text-pink-400" />
          Isolation Forest Anomaly Deviation History
        </h2>
        <span className="text-xs text-pink-400 font-mono">Current Score: {anomalyScore}</span>
      </div>

      <div className="w-full h-40 bg-[#070A12] border border-slate-800/80 rounded-xl p-4 relative overflow-hidden flex items-end">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 120" preserveAspectRatio="none">
          <line x1="0" y1="30" x2="1000" y2="30" stroke="#1e293b" strokeDasharray="4 4" />
          <line x1="0" y1="60" x2="1000" y2="60" stroke="#1e293b" strokeDasharray="4 4" />

          {/* Anomaly Spike Path */}
          <path
            d="M 0 100 L 200 95 L 400 90 L 600 70 L 800 30 L 1000 15"
            fill="none"
            stroke="#ec4899"
            strokeWidth="3"
          />
        </svg>

        <div className="absolute top-2 left-3 text-[10px] font-mono text-slate-500 space-y-4">
          <p>1.0</p>
          <p>0.5</p>
          <p>0.0</p>
        </div>
      </div>
    </div>
  );
}
