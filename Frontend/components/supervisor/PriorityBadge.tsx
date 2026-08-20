import React from 'react';

interface PriorityBadgeProps {
  priority: 'Low' | 'Medium' | 'High' | 'Critical' | string;
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  const normalized = priority.toLowerCase();
  let colorStyle = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';

  if (normalized === 'critical') {
    colorStyle = 'bg-red-500/20 text-red-300 border-red-500/40 animate-pulse';
  } else if (normalized === 'high') {
    colorStyle = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
  } else if (normalized === 'medium') {
    colorStyle = 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
  } else if (normalized === 'low') {
    colorStyle = 'bg-blue-500/20 text-blue-300 border-blue-500/40';
  }

  return (
    <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold border uppercase tracking-wide ${colorStyle}`}>
      {priority} Priority
    </span>
  );
}
