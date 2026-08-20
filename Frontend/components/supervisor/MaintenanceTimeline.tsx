import React from 'react';
import { Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface MaintenanceTimelineProps {
  currentCycle: number;
  rulCycles: number;
}

export function MaintenanceTimeline({ currentCycle = 168, rulCycles = 24 }: MaintenanceTimelineProps) {
  const events = [
    { cycle: currentCycle - 68, label: 'Baseline Inspection Completed', status: 'done' },
    { cycle: currentCycle - 28, label: 'Sensor_11 Anomaly First Observed', status: 'warning' },
    { cycle: currentCycle, label: 'Current Telemetry Sampling (Cycle 168)', status: 'current' },
    { cycle: currentCycle + rulCycles, label: 'Target Preventive Maintenance Window', status: 'future' },
  ];

  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl space-y-3">
      <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
        <Clock className="w-4 h-4 text-indigo-400" />
        Maintenance Lifecycle Timeline
      </h3>

      <div className="relative pl-6 space-y-4 border-l border-slate-800 my-2">
        {events.map((evt, idx) => (
          <div key={idx} className="relative">
            <div
              className={`absolute -left-[31px] top-0.5 w-3.5 h-3.5 rounded-full border ${
                evt.status === 'done'
                  ? 'bg-emerald-500 border-emerald-400'
                  : evt.status === 'warning'
                  ? 'bg-amber-500 border-amber-400 animate-pulse'
                  : evt.status === 'current'
                  ? 'bg-indigo-500 border-indigo-400 ring-4 ring-indigo-500/20'
                  : 'bg-slate-800 border-slate-700'
              }`}
            />
            <div className="flex justify-between items-start text-xs">
              <span className="font-semibold text-slate-200">{evt.label}</span>
              <span className="font-mono text-slate-400 text-[11px]">Cycle {evt.cycle}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
