import React, { useState } from 'react';
import { FileText } from 'lucide-react';

interface HumanReviewPanelProps {
  onSubmitFeedback?: (validation: string, notes: string) => void;
}

export function HumanReviewPanel({ onSubmitFeedback }: HumanReviewPanelProps) {
  const [validation, setValidation] = useState('Accept: Perform Preventive Maintenance');
  const [notes, setNotes] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmitFeedback) onSubmitFeedback(validation, notes);
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl space-y-3">
      <div>
        <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
          <FileText className="w-3.5 h-3.5 text-indigo-400" />
          Human Engineer Feedback &amp; Policy Adaptation
        </h3>
        <p className="text-[11px] text-slate-400 mt-0.5">
          Log engineer override or validation to continuously retrain the supervisor policy network.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-[11px] text-slate-400 mb-1 font-semibold">Engineer Decision Validation:</label>
          <select
            value={validation}
            onChange={(e) => setValidation(e.target.value)}
            className="w-full bg-[#070A12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="Accept: Perform Preventive Maintenance">Accept: Perform Preventive Maintenance</option>
            <option value="Override: Continue Operation">Override: Continue Operation</option>
            <option value="Override: Immediate Grounding">Override: Immediate Grounding</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] text-slate-400 mb-1 font-semibold">Chief Engineer Notes:</label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g. HPC outlet pressure harmonic confirmed via borescope..."
            className="w-full bg-[#070A12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <button
          type="submit"
          className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition active:scale-98"
        >
          {submitted ? '✓ Policy Network Updated!' : 'Submit Engineer Feedback & Adapt Policy'}
        </button>
      </form>
    </div>
  );
}
