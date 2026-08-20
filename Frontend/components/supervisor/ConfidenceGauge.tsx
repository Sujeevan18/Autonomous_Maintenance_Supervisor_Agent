import React from 'react';

interface ConfidenceGaugeProps {
  confidence: number; // 0 to 1 or 0 to 100
  label?: string;
}

export function ConfidenceGauge({ confidence, label = 'Policy Confidence' }: ConfidenceGaugeProps) {
  const pct = confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence);
  const strokeDashoffset = 251.2 - (251.2 * pct) / 100;

  return (
    <div className="flex flex-col items-center justify-center p-2">
      <div className="relative w-24 h-24 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="#1e293b"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="#10b981"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray="251.2"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        <div className="absolute text-center">
          <span className="text-xl font-black text-white font-mono">{pct}%</span>
        </div>
      </div>
      <span className="text-[11px] font-semibold text-slate-400 mt-1">{label}</span>
    </div>
  );
}
